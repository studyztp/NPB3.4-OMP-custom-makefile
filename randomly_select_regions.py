import json
from pathlib import Path
import random

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
thread = 1
size = "B"
region_size = 1000_000_000

workdir = Path().cwd()

random.seed(627)

with open(workdir / f"region_info_{size}_{region_size}_{thread}.json", "r") as f:
    all_info = json.load(f)

all_selected_region = {}

for benchmark in benchmarks:
    all_region = list(all_info[benchmark][size][str(region_size)].keys())
    all_region.remove("bb_info_filename")
    selected_region = random.sample(all_region, 10)
    all_selected_region[benchmark] = selected_region

with open(workdir / f"randomly_selected_region_{size}_{str(region_size)}_{thread}.json", "w") as f:
    json.dump(all_selected_region, f, indent=4)


