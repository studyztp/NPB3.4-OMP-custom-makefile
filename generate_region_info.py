from pathlib import Path
import shutil
import json
import re

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

# workdir = Path.cwd()
workdir = Path("/home/studyztp/test_ground/experiments/hardware-profiling/NPB_protocol/NPB3.4.2/multi-thread/NPB3.4-OMP-saphir")

benchmarks = ['bt', 'cg', 'ep', 'ft', 'is', 'lu', 'mg', 'sp']
size = "C"
region_length = 1000_000_000
arch = "aarch64"
threads = 8

info = {}

for benchmark in benchmarks:
    bench_dir = Path(workdir/f"{benchmark.upper()}/{size}/c_profiling/{region_length}")
    bb_info_file = bench_dir.glob("basic_block_info_output_*")
    info[benchmark] = {}
    info[benchmark][size] = {}
    for file in bb_info_file:
        static_info = get_static_info(Path(bench_dir/file.name))
        info[benchmark][size]["bb_info_filename"] = file.name

    bench_info_file_path = Path(bench_dir/f"{arch}/all_output_{threads}_threads.txt")
    with open(bench_info_file_path, 'r') as f:
        line = f.readline()
        r_1_fid = 0
        r_1_bid = 0
        r_1_count = 0
        r_2_fid = 0
        r_2_bid = 0
        r_2_count = 0
        while line:
            line = line.split()
            if len(line) > 0:
                if line[0] == 'Region:':
                    region = int(line[1])
                    line = f.readline()
                    line = f.readline()
                    region_IR_inst_count = int(line.split()[5])
                    sum_bbv = []
                    for _ in range(threads):
                        line = f.readline()
                        line = line.split()
                        bbv = line[3]
                        bbv = bbv[:-1]
                        bbv = bbv[1:]
                        bbv = bbv.split(',')
                        bbv = bbv[:-1]
                        bbv = [int(x) for x in bbv]
                        if len(sum_bbv) == 0:
                            sum_bbv = bbv
                        else:
                            sum_bbv = [x + y for x, y in zip(sum_bbv, bbv)]
                    line = f.readline()
                    line = line.split()
                    if line[0] == 'Timestamp:':
                        timestamp = line[1]
                        timestamp = timestamp[:-1]
                        timestamp = timestamp[1:]
                        timestamp = timestamp.split(',')
                        timestamp = timestamp[:-1]
                        timestamp = [int(x) for x in timestamp]
                        max_index = timestamp.index(max(timestamp))
                        bb_count = sum_bbv[max_index]
                        
                            
                        info[benchmark][size][region] = {
                            "warmupMarkerFunctionId" : r_2_fid,
                            "warmupMarkerBBId" : r_2_bid,
                            "warmupMarkerCount" : r_2_count,
                            "startMarkerFunctionId" : r_1_fid,
                            "startMarkerBBId" : r_1_bid,
                            "startMarkerCount" : r_1_count,
                            "endMarkerFunctionId" : static_info[int(max_index)]["function_id"],
                            "endMarkerBBId" : int(max_index),
                            "endMarkerCount" : bb_count,
                        }

                        r_2_fid = r_1_fid
                        r_2_bid = r_1_bid
                        r_2_count = r_1_count
                        r_1_fid = static_info[int(max_index)]["function_id"]
                        r_1_bid = int(max_index)
                        r_1_count = max(timestamp)

            line = f.readline()


with open(f"region_info_{size}_{region_length}.json", "w") as f:
    json.dump(info, f, indent=4)

for benchmark in benchmarks:
    bench_dir = Path(workdir/f"{benchmark.upper()}/{size}")
    region_info_dir = Path(bench_dir/"region_info")
    region_info_dir.mkdir(exist_ok=True)
    region_info_size_dir = Path(region_info_dir/f"{region_length}")
    region_info_size_dir.mkdir(exist_ok=True)
    for rid, rdata in info[benchmark][size].items():
        if rid == 'bb_info_filename':
            continue
        r_dir = Path(region_info_size_dir/f"{rid}")
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
        shutil.copy(Path(bench_dir/f"c_profiling/{region_length}/{info[benchmark][size]['bb_info_filename']}"), r_dir/info[benchmark][size]['bb_info_filename'])
    

