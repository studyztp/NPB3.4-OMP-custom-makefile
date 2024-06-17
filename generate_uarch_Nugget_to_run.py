import json
from pathlib import Path
from sklearn.cluster import KMeans
from sklearn import random_projection
import numpy as np
import random
from scipy.spatial import distance

workdir = Path().cwd()

random_seed = 627
np.random.seed(random_seed)
random.seed(random_seed)

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]

with open(Path(workdir/"cluster_based_on_uarch.json")) as f:
    uarch_cluster_info = json.load(f)

to_run = {}

count = 0

# script to make arm gem5 Nuggets
arm_nugget_script = ""

for bench in benchmarks:
    bench_data = uarch_cluster_info[bench]
    bench_rids = set()
    for k in range(10, 31, 10):
        bench_rids.update(bench_data[str(k)]["rep_rid"].values())
        for value in bench_data[str(k)]["clusters"].values():
            the_regions = list(value)
            selected = set()
            while len(selected) < 3 and len(selected) < len(the_regions)-1:
                chosen_rid = random.sample(list(the_regions),min(3, len(the_regions)-1))
                for rid in chosen_rid:
                    the_regions.remove(rid)
                    if rid not in bench_rids:
                        selected.add(rid)
            bench_rids.update(selected)
    to_run[bench] = list(bench_rids)
    for rid in bench_rids:
        arm_nugget_script += f"make m5_fs PROGRAM={bench} REGION={rid};\n"
        arm_nugget_script += f"make final_compile_m5_fs PROGRAM={bench} REGION={rid} TARGET_ARCH=aarch64;\n"
        arm_nugget_script += f"make papi PROGRAM={bench} REGION={rid};\n"
        arm_nugget_script += f"make final_compile_papi PROGRAM={bench} REGION={rid} TARGET_ARCH=aarch64;\n"
    count += len(bench_rids)

print(count)

with open(Path(workdir/"uarch_Nugget_to_run.json"), "w") as f:
    json.dump(to_run, f, indent=4)

with open(Path(workdir/"build_uarch_Nugget_arm_gem5.sh"), "w") as f:
    f.write(arm_nugget_script)
