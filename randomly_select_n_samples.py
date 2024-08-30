import json
import random
from pathlib import Path

workdir = Path().cwd()

target_thread = 1
target_run_num = 0
size = "C"
region_length = 1000_000_000
num_samples = 10

benchmarks =  ["bt", "cg", "ep", "is", "ft", "lu", "mg", "sp"]

all_bench_info = {}

for bench in benchmarks:
    info_path = Path(workdir/f"{bench.upper()}/{size}/region_info/{target_thread}/{region_length}/{bench}_{target_run_num}_info.json")
    with open(info_path, "r") as f:
        info = json.load(f)
    total_regions = len(info.keys())
    rid_list = [int(rid) for rid in info.keys()]
    randomly_selected_regions = random.sample(rid_list, min(num_samples, total_regions))
    all_bench_info[bench] = randomly_selected_regions

with open(f"randomly_selected_{num_samples}_regions.json", "w") as f:
    json.dump(all_bench_info, f, indent=4)

