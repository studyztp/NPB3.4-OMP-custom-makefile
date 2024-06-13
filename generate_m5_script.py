import json
from pathlib import Path
import shutil
import argparse

all_rid = {}

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]

workdir = Path.cwd()
common_dir = Path(workdir/"common")

with open(workdir/"clustering_data.json") as f:
    data = json.load(f)

for bench in benchmarks:
    rep_rid = set()
    for k in range(10, 31, 10):
        rep_rid.update(data[bench][str(k)]["rep_rid"].values())
    all_rid[bench] = rep_rid

base_runscript = ""
arm_runscript = ""
x86_runscript = ""

for bench in benchmarks:
    rep_rid = all_rid[bench]
    for rid in rep_rid:
        base_runscript += f"make m5_fs PROGRAM={bench} REGION={rid};\n"
        arm_runscript += f"make final_compile_m5_fs PROGRAM={bench} REGION={rid} TARGET_ARCH=aarch64;\n"
        x86_runscript += f"make final_compile_m5_fs PROGRAM={bench} REGION={rid} TARGET_ARCH=x86_64;\n"

with open("build_all_base_m5_fs.sh", "w") as f:
    f.write(base_runscript)

with open("build_all_arm_m5_fs.sh", "w") as f:
    f.write(arm_runscript)

with open("build_all_x86_m5_fs.sh", "w") as f:
    f.write(x86_runscript)
