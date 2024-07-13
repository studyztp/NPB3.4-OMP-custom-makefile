from pathlib import Path
import shutil
import json
import math
import re

# define basic variables
# input_dir = Path("/home/studyztp/test_ground/experiments/hardware-profiling/NPB_protocol/NPB3.4.2/multi-thread/Overhead/NPB3.4-OMP-custom-makefile")
# output_dir = Path("/home/studyztp/test_ground/experiments/hardware-profiling/NPB_protocol/NPB3.4.2/multi-thread/NPB3.4-OMP")
# output_dir = Path("/home/studyztp/test_ground/experiments/hardware-profiling/NPB_protocol/NPB3.4.2/multi-thread/Overhead/NPB3.4-OMP-custom-makefile")

input_dir = Path().cwd()
output_dir = Path().cwd()

benchmarks = ['bt', 'cg', 'ep', 'ft', 'is', 'lu', 'mg', 'sp']   
# benchmarks = ["is"]
size = "B"
region_length = 1000_000_000
# arch = "x86_64"
arch = "aarch64"
threads = 1

all_bench_info = {}
# define basic vairables end

# define helper functions
def get_static_info(path):
    info = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                function_match = re.match(r'\[(\d+):([^\]]+)\]', line)
                if function_match:
                    function_id, function_name = function_match.groups()
                    basic_blocks = re.findall(r'\[(\d+):([^\]]*):(\d+)\]', line)
                    for basic_block in basic_blocks:
                        basic_block_id, basic_block_name, basic_block_ir_inst_count = basic_block
                        info[int(basic_block_id)] = {
                            "basic_block_name": basic_block_name,
                            "basic_block_ir_inst_count": int(basic_block_ir_inst_count),
                            "function_name": function_name,
                            "function_id": int(function_id)
                        }
    return info

# There are a few things to consider when constructing the warmup marker,
# start marker, and end marker information.
# Because the warmup marker invokes the start marker counter, and the start 
# marker counter invokes the end marker counter, the start marker information 
# is depending on the warmup marker information, and the end marker information
# is depending on the start marker information.

# There are a few facts:
# 1. The warmup marker and the start marker can be at the ROI begin, which do 
# not have BBV information.
# 2. The warmup marker and start marker can both at the ROI begin, in this case,
# because of how Nugget is implemented in LLVM, the warmup marker will immediately
# invoke the start marker.

# TODO: Include the timestamp information when selecting marker basic blocks

def get_global_count(global_bbv, bb_id):
    if global_bbv is None:
        return 0
    else:
        return global_bbv[bb_id]

def get_count_corresponding_to_previous_marker(previous_sum_bbv, bb_id, bb_count):
    if previous_sum_bbv is None:
        return bb_count
    else:
        return bb_count - previous_sum_bbv[bb_id]
    
def find_the_best_marker_bb_id(bbv, timestamp, threshold):
    min_count = math.inf
    min_bb_id = 0
    for bbid in range(len(bbv)):
        if timestamp[bbid] > threshold:
            if bbv[bbid] < min_count:
                min_count = bbv[bbid]
                min_bb_id = bbid
    return min_bb_id
    

def construct_regional_marker_information(path):
    all_info = {}
    global_bbv = None
    bb_info_file = path.glob("basic_block_info_output_*")
    for file in bb_info_file:
        static_info = get_static_info(Path(path/file.name))
        all_info["bb_info_filename"] = file.name
    
    bbv_file_path = Path(path/f"{arch}/all_output_{threads}_threads.txt")

    with open(bbv_file_path, "r") as f:
        line = f.readline()
        r_1_fid = 0
        r_1_bid = 0
        r_1_count = 0
        r_1_sum_bbv = None
        r_1_global_bbv = None
        r_2_fid = 0
        r_2_bid = 0
        r_2_count = 0
        r_2_sum_bbv = None
        r_2_global_bbv = None
        while line:
            line = line.split()
            if len(line) > 0:
                if line[0] == "Region:":
                    region = int(line[1])
                    line = f.readline()
                    total_IR_inst_count = int(line.split()[3])
                    line = f.readline()
                    region_IR_inst_count = int(line.split()[5])
                    cur_sum_bbv = []
                    cur_timestamp = []
                    for _ in range(threads):
                        line = f.readline()
                        line = line.split()
                        line = line[5]
                        line = line.split(",")
                        line = line[:-1]
                        line[0] = line[0][1:]
                        temp_bbv = []
                        temp_timestamp = []
                        for item in line:
                            item = item.split(":")
                            temp_bbv.append(int(item[0]))
                            temp_timestamp.append(int(item[1]))
                        if len(cur_sum_bbv) == 0:
                            cur_sum_bbv = temp_bbv
                            cur_timestamp = temp_timestamp
                        else:
                            cur_sum_bbv = [x + y for x, y in zip(cur_sum_bbv, temp_bbv)]
                            cur_timestamp = [x if x > y else y for x, y in zip(cur_timestamp, temp_timestamp)]
                    if global_bbv is None:
                        global_bbv = cur_sum_bbv
                    else:
                        global_bbv = [x + y for x, y in zip(global_bbv, cur_sum_bbv)]
                        
                    # TODO: modify here so we can consider the timestamp information
                    # when selecting the marker basic blocks
                    max_bid = int(cur_timestamp.index(max(cur_timestamp)))
                    max_count = cur_sum_bbv[max_bid]
                    cur_bid = find_the_best_marker_bb_id(cur_sum_bbv, cur_timestamp, region_IR_inst_count - 50_000_000)
                    cur_count = cur_sum_bbv[cur_bid]
                    gap = cur_timestamp[max_bid] - cur_timestamp[cur_bid]
                    cur_fid = static_info[cur_bid]["function_id"]

                    all_info[region] = {
                            "warmupMarkerFunctionId" : r_2_fid,
                            "warmupMarkerBBId" : r_2_bid,
                            "warmupMarkerCount" : get_global_count(r_2_global_bbv, r_2_bid),
                            "startMarkerFunctionId" : r_1_fid,
                            "startMarkerBBId" : r_1_bid,
                            "startMarkerCount" : r_1_count,
                            "startMarkerGlobalCount": get_global_count(r_1_global_bbv, r_1_bid),
                            "endMarkerFunctionId" : cur_fid,
                            "endMarkerBBId" : int(cur_bid),
                            "endMarkerCount" : cur_count,
                            "endMarkerGlobalCount": get_global_count(global_bbv, cur_bid),
                            "gap": gap,
                            "regionalIRInstCount": region_IR_inst_count,
                            "totalIRInstCount": total_IR_inst_count

                    }

                    r_2_fid = r_1_fid
                    r_2_bid = r_1_bid
                    # the count and bbv is local to the region
                    r_2_count = r_1_count
                    r_2_sum_bbv = r_1_sum_bbv
                    r_2_global_bbv = r_1_global_bbv
                    r_1_fid = cur_fid
                    r_1_bid = cur_bid
                    # the count and bbv is local to the region
                    r_1_count = cur_count
                    r_1_sum_bbv = cur_sum_bbv.copy()
                    r_1_global_bbv = global_bbv.copy()

            line = f.readline()

    return all_info

# define helper functions end

# real action here


for benchmark in benchmarks:
    bench_dir = Path(input_dir/f"{benchmark.upper()}/{size}/single_thread_c_profiling/{region_length}")
    bench_regional_marker_info = construct_regional_marker_information(bench_dir)
    if benchmark not in all_bench_info:
        all_bench_info[benchmark] = {}
    if size not in all_bench_info[benchmark]:
        all_bench_info[benchmark][size] = {}

    all_bench_info[benchmark][size][region_length] = bench_regional_marker_info

with open(output_dir/f"region_info_{size}_{region_length}_{threads}.json", "w") as f:
    json.dump(all_bench_info, f, indent=4)

# create info folder for each region

for benchmark in benchmarks:
    input_bench_dir = Path(input_dir/f"{benchmark.upper()}/{size}")
    output_bench_dir = Path(output_dir/f"{benchmark.upper()}/{size}")
    region_info_dir = Path(output_bench_dir/"region_info")
    region_info_dir.mkdir(exist_ok=True)
    region_info_thread_dir = Path(region_info_dir/f"{threads}")
    region_info_thread_dir.mkdir(exist_ok=True)
    region_info_thread_size_dir = Path(region_info_thread_dir/f"{region_length}")
    if region_info_thread_size_dir.exists():
        shutil.rmtree(region_info_thread_size_dir)
    region_info_thread_size_dir.mkdir(exist_ok=True)
    for rid, rdata in all_bench_info[benchmark][size][region_length].items():
        if rid == 'bb_info_filename':
            continue
        r_dir = Path(region_info_thread_size_dir/f"{rid}")
        r_dir.mkdir(exist_ok=True)
        with open(r_dir/f"{rid}_marker_info.txt", "w") as f:
            f.write(f"{rdata['warmupMarkerFunctionId']}\n")
            f.write(f"{rdata['warmupMarkerBBId']}\n")
            f.write(f"{rdata['warmupMarkerCount']}\n")
            f.write(f"{rdata['startMarkerFunctionId']}\n")
            f.write(f"{rdata['startMarkerBBId']}\n")
            f.write(f"{rdata['startMarkerCount']}\n")
            f.write(f"{rdata['endMarkerFunctionId']}\n")
            f.write(f"{rdata['endMarkerBBId']}\n")
            f.write(f"{rdata['endMarkerCount']}\n")
        shutil.copy(Path(input_bench_dir/f"single_thread_c_profiling/{region_length}/{all_bench_info[benchmark][size][region_length]['bb_info_filename']}"), r_dir/all_bench_info[benchmark][size][region_length]['bb_info_filename'])
    
