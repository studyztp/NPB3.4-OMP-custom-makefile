import json
from pathlib import Path
import shutil
import argparse

all_rid = {}

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]

region_size = 100000000

workdir = Path.cwd()
common_dir = Path(workdir/"common")
arm_papi_lib_dir = Path(common_dir/"all_papi/aarch64/lib")
x86_papi_lib_dir = Path(common_dir/"all_papi/x86_64/lib")
arm_lib_dir = Path(common_dir/"aarch64-unknown-linux-gnu")
x86_lib_dir = Path(common_dir/"x86_64-unknown-linux-gnu")

challenger_papi_cmds = [
    "export PAPI_EVENTS='PAPI_TLB_IM,PAPI_TLB_DM,PAPI_L2_DCM,PAPI_L1_ICM' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/0",
    "export PAPI_EVENTS='PAPI_TOT_INS,PAPI_BR_MSP,PAPI_BR_TKN,PAPI_L2_ICM' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/1",
    "export PAPI_EVENTS='PAPI_L2_DCH,PAPI_TOT_CYC,PAPI_BR_INS,PAPI_FP_INS' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/2",
    "export PAPI_EVENTS='PAPI_L2_ICR,PAPI_L2_ICH,PAPI_L2_DCR,PAPI_L1_DCA' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/3",
    "export PAPI_EVENTS='PAPI_FP_OPS,PAPI_L2_ICH,PAPI_L2_DCR,PAPI_L1_DCA' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/4"
]

azacca_papi_cmds = [
    "export PAPI_EVENTS='PAPI_RES_STL,PAPI_TLB_DM,PAPI_L2_DCM,PAPI_L1_ICM,PAPI_L1_DCM' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/0",
    "export PAPI_EVENTS='PAPI_TOT_CYC,PAPI_BR_MSP,PAPI_HW_INT,PAPI_STL_ICY,PAPI_L2_LDM' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/1",
    "export PAPI_EVENTS='PAPI_SR_INS,PAPI_LD_INS,PAPI_FP_INS,PAPI_TOT_INS,PAPI_BR_PRC' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/2",
    "export PAPI_EVENTS='PAPI_L1_DCR,PAPI_L1_DCA,PAPI_LST_INS,PAPI_VEC_INS,PAPI_BR_INS' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/3",
    "export PAPI_EVENTS='PAPI_L2_DCW,PAPI_L1_DCW,PAPI_L2_DCR,PAPI_L2_DCA,PAPI_SYC_INS' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/4",
    "export PAPI_EVENTS='PAPI_L2_TCA,PAPI_L1_ICA,PAPI_L1_ICH,PAPI_L2_DCA,PAPI_L1_DCA' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/5"
]

arm_setup_env = f"export LD_LIBRARY_PATH={arm_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export LD_LIBRARY_PATH={arm_papi_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export OMP_NUM_THREADS=1"
x86_setup_env = f"export LD_LIBRARY_PATH={x86_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export LD_LIBRARY_PATH={x86_papi_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export OMP_NUM_THREADS=1"


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

arm_runscript += f"{arm_setup_env};\n"
x86_runscript += f"{x86_setup_env};\n"

for bench in benchmarks:
    rep_rid = all_rid[bench]
    bench_dir = Path(workdir/bench.upper())
    for rid in rep_rid:
        base_runscript += f"make papi PROGRAM={bench} REGION={rid};\n"
        arm_runscript += f"cd {workdir} && make final_compile_papi PROGRAM={bench} REGION={rid} ARCH=aarch64;\n"
        x86_runscript += f"cd {workdir} && make final_compile_papi PROGRAM={bench} REGION={rid} ARCH=x86_64;\n"
    for rid in rep_rid:
        arm_runscript += f"cd {bench_dir.as_posix()}/papi/{region_size}/{rid}/aarch64 && rm -r data;\n"
        arm_runscript += f"cd {bench_dir.as_posix()}/papi/{region_size}/{rid}/aarch64 && mkdir -p data;\n"
        x86_runscript += f"cd {bench_dir.as_posix()}/papi/{region_size}/{rid}/x86_64 && rm -r data;\n"
        x86_runscript += f"cd {bench_dir.as_posix()}/papi/{region_size}/{rid}/x86_64 && mkdir -p data;\n"
        for papi_cmd in azacca_papi_cmds:
            arm_runscript += f"cd {bench_dir.as_posix()}/papi/{region_size}/{rid}/aarch64 && {papi_cmd} && ./{bench}_aarch64_*.papi;\n"
        for papi_cmd in challenger_papi_cmds:
            x86_runscript += f"cd {bench_dir.as_posix()}/papi/{region_size}/{rid}/x86_64 && {papi_cmd} && ./{bench}_x86_64_*.papi;\n"

with open(f"build_all_base_papi.sh", "w") as f:
    f.write(base_runscript)

with open(f"build_n_run_all_arm_papi.sh", "w") as f:
    f.write(arm_runscript)

with open(f"build_n_run_all_x86_papi.sh", "w") as f:
    f.write(x86_runscript)
