import json
from pathlib import Path
import shutil
import argparse

parser = argparse.ArgumentParser(description="Generate script to run all benchmarks with PAPI")
parser.add_argument("--target_k", type=int, default=10, help="Target number of clusters")
args = parser.parse_args()

print(f"Generating script for target_k = {args.target_k}")

target_k = args.target_k
benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
workdir = Path.cwd()
common_dir = Path(workdir/"common")
papi_lib_dir = Path(common_dir/"papi/install/lib")
arm_lib_dir = Path(common_dir/"aarch64-unknown-linux-gnu")
papi_cmds = [
    "export PAPI_EVENTS='PAPI_RES_STL,PAPI_TLB_DM,PAPI_L2_DCM,PAPI_L1_ICM,PAPI_L1_DCM, && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/0",
    "export PAPI_EVENTS='PAPI_TOT_CYC,PAPI_BR_MSP,PAPI_HW_INT,PAPI_STL_ICY,PAPI_L2_LDM, && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/1",
    "export PAPI_EVENTS='PAPI_SR_INS,PAPI_LD_INS,PAPI_FP_INS,PAPI_TOT_INS,PAPI_BR_PRC, && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/2",
    "export PAPI_EVENTS='PAPI_L1_DCR,PAPI_L1_DCA,PAPI_LST_INS,PAPI_VEC_INS,PAPI_BR_INS, && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/3",
    "export PAPI_EVENTS='PAPI_L2_DCW,PAPI_L1_DCW,PAPI_L2_DCR,PAPI_L2_DCA,PAPI_SYC_INS, && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/4",
    "export PAPI_EVENTS='PAPI_L2_TCA,PAPI_L1_ICA,PAPI_L1_ICH,PAPI_L2_DCA,PAPI_L1_DCA, && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/5"
]
setup_env = f"export LD_LIBRARY_PATH={arm_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export LD_LIBRARY_PATH={papi_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export OMP_NUM_THREADS=1"

with open(workdir/"clustering_data.json") as f:
    data = json.load(f)

runscript = ""

runscript += f"{setup_env};\n"

for bench in benchmarks:
    bench_data = data[bench]
    bench_dir = Path(workdir/bench.upper())
    rep_data = bench_data[str(target_k)]["rep_rid"]
    for rid in rep_data.values():
        rid_dir = Path(bench_dir/f"papi/{rid}")
        if Path(rid_dir/"data").exists():
            shutil.rmtree(rid_dir/"data")
        Path(rid_dir/"data").mkdir(parents=True, exist_ok=True)
        
        for papi_cmd in papi_cmds:
            runscript += f"cd {rid_dir.as_posix()} && {papi_cmd} && ./{bench}_papi_{rid};\n"

with open(f"run_all_{target_k}_papi_point.sh", "w") as f:
    f.write(runscript)

# for bench in benchmarks:
#     bench_dir = Path(workdir/bench.upper())
#     papi_naive_dir = Path(bench_dir/"papi_naive")
#     if Path(papi_naive_dir/"data").exists():
#         shutil.rmtree(papi_naive_dir/"data")
#     Path(papi_naive_dir/"data").mkdir(exist_ok=False)
#     for papi_cmd in papi_cmds:
#         runscript += f"cd {papi_naive_dir.as_posix()} && {papi_cmd} && ./{bench}_papi_naive;\n"

# with open(f"run_all_naive_papi_point.sh", "w") as f:
#     f.write(runscript)

