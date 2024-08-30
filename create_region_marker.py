import json
from pathlib import Path
import re
import math
import shutil

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

def get_best_bid_n_count(bbv, timestamp, safe_range):
    best_bid = math.inf
    best_count = math.inf
    for i in range(len(bbv)):
        if timestamp[i] >= safe_range:
            if bbv[i] < best_count:
                best_bid = i
                best_count = bbv[i]
    return best_bid, best_count

def create_region_marker(run_output_file, static_info, num_threads):
    marker_info = {}
    region_id = 0
    w_bid = 0
    w_count = 0
    s_bid = 0
    s_count = 0
    s_global_count = 0
    e_bid = 0
    e_count = 0
    e_global_count = None

    global_bbv = None
    with open(run_output_file, "r") as f:
        line = f.readline()
        while line:
            if "Region:" in line:
                line = f.readline()
                line = f.readline().split()
                ir_inst_count = int(line[5])
                safe_period = int(float(1-safe_perf) * float(ir_inst_count))
                regional_bbv = None
                regional_timestamp = None
                for _ in range(num_threads):
                    line = f.readline().split()
                    data = line[5][1:-2]
                    data = data.split(",")
                    thread_bbv = []
                    thread_timestamp = []
                    for ele in data:
                        ele = ele.split(":")
                        thread_bbv.append(int(ele[0]))
                        thread_timestamp.append(int(ele[1]))
                    if regional_bbv is None:
                        regional_bbv = thread_bbv
                        regional_timestamp = thread_timestamp
                    else:
                        for i in range(len(thread_bbv)):
                            regional_bbv[i] += thread_bbv[i]
                            regional_timestamp[i] = max(regional_timestamp[i], thread_timestamp[i])
                best_bid, best_count = get_best_bid_n_count(regional_bbv, regional_timestamp, safe_period)
                if global_bbv is None:
                    global_bbv = regional_bbv
                else:
                    for i in range(len(global_bbv)):
                        global_bbv[i] += regional_bbv[i]
                e_bid = best_bid
                e_count = best_count
                e_global_count = global_bbv[e_bid]
                marker_info[region_id] = {
                    "warmup_marker_bbid": w_bid,
                    "warmup_marker_bbid_count": w_count,
                    "warmup_marker_fid": static_info[w_bid]["function_id"],
                    "start_marker_bbid": s_bid,
                    "start_marker_bbid_count": s_count,
                    "start_marker_fid": static_info[s_bid]["function_id"],
                    "end_marker_bbid": e_bid,
                    "end_marker_bbid_count": e_count,
                    "end_marker_fid": static_info[e_bid]["function_id"],
                }
                region_id += 1
                w_bid = s_bid
                w_count = s_global_count
                s_bid = e_bid
                s_count = e_count
                s_global_count = e_global_count
            line = f.readline()
    return marker_info

target_thread = 1
target_experiment_name = "single_thread_c_profiling"
target_run_num = 0
target_arch = "aarch64"
size = "C"
region_length = 1000_000_000
safe_perf = 0.05

benchmarks =  ["bt", "cg", "ep", "is", "ft", "lu", "mg", "sp"]
workdir = Path().cwd()
output_dir = workdir

for bench in benchmarks:
    bench_dir = Path(workdir/f"{bench.upper()}/{size}/{target_experiment_name}/{region_length}")
    run_dir = Path(bench_dir/f"{target_arch}/run_{target_thread}_{target_run_num}")
    for file in bench_dir.glob("basic_block_info_output_*"):
        basic_block_info_file_path = Path(bench_dir/file.name)
        filename = file.name
        static_info = get_static_info(basic_block_info_file_path)
    run_output_file = Path(run_dir/f"all_output_{target_thread}_threads.txt")
    marker_info = create_region_marker(run_output_file, static_info, target_thread)
    bench_output_base = Path(output_dir/f"{bench.upper()}/{size}/region_info")
    bench_output_base.mkdir(exist_ok=True)
    bench_thread_output = Path(bench_output_base/f"{target_thread}")
    bench_thread_output.mkdir(exist_ok=True)
    bench_thread_region_size_output = Path(bench_thread_output/f"{region_length}")
    if bench_thread_region_size_output.exists():
        shutil.rmtree(bench_thread_region_size_output)
    bench_thread_region_size_output.mkdir(exist_ok=False)
    with open(bench_thread_region_size_output/f"{bench}_{target_run_num}_info.json", "w") as f:
        json.dump(marker_info, f, indent=4)
    for rid, rdata in marker_info.items():
        region_output_dir = Path(bench_thread_region_size_output/f"{rid}")
        region_output_dir.mkdir(exist_ok=True)
        with open(region_output_dir/f"{rid}_marker_info.txt", "w") as f:
            f.write(f"{rdata['warmup_marker_fid']}\n")
            f.write(f"{rdata['warmup_marker_bbid']}\n")
            f.write(f"{rdata['warmup_marker_bbid_count']}\n")
            f.write(f"{rdata['start_marker_fid']}\n")
            f.write(f"{rdata['start_marker_bbid']}\n")
            f.write(f"{rdata['start_marker_bbid_count']}\n")
            f.write(f"{rdata['end_marker_fid']}\n")
            f.write(f"{rdata['end_marker_bbid']}\n")
            f.write(f"{rdata['end_marker_bbid_count']}\n")
        shutil.copy(basic_block_info_file_path, Path(region_output_dir/filename))
