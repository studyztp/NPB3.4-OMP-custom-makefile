import json
from pathlib import Path
import shutil

target_k = 10
benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
workdir = Path.cwd()
common_dir = Path(workdir/"common")
papi_lib_dir = Path(common_dir/"papi/install/lib")
arm_lib_dir = Path(common_dir/"aarch64-unknown-linux-gnu")
papi_cmds = [
    "export PAPI_EVENTS='PAPI_TOT_INS,PAPI_TOT_CYC' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/papi_basic",
    "export PAPI_EVENTS='PAPI_L1_DCR,PAPI_L1_DCW,PAPI_L1_DCM,PAPI_L1_DCA,PAPI_TLB_DM' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/backend0",
    "export PAPI_EVENTS='PAPI_L2_TCR,PAPI_L2_TCW,PAPI_L2_TCM,PAPI_L2_TCA,PAPI_L3_DCM,PAPI_L3_TCA' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/backend1",
    "export PAPI_EVENTS='PAPI_L1_ICM,PAPI_L1_ICH,PAPI_L1_ICA,PAPI_TLB_IM' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/frontend",
    "export PAPI_EVENTS='PAPI_TOT_INS,PAPI_INT_INS,PAPI_FP_INS,PAPI_LD_INS' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/inst0",
    "export PAPI_EVENTS='PAPI_SR_INS,PAPI_BR_INS,PAPI_VEC_INS' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/inst1",
    "export PAPI_EVENTS='PAPI_STL_ICY,PAPI_STL_CCY,PAPI_BR_MSP,PAPI_BR_PRC,PAPI_RES_STL,PAPI_TOT_CYC,PAPI_LST_INS' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/pipe0",
    "export PAPI_EVENTS='PAPI_SYC_INS,PAPI_FP_OPS,PAPI_REF_CYC' && export PAPI_OUTPUT_DIRECTORY=${PWD}/data/pipe1",
]
setup_env = f"export LD_LIBRARY_PATH={arm_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export LD_LIBRARY_PATH={papi_lib_dir.as_posix()}:$LD_LIBRARY_PATH && export OMP_NUM_THREADS=1"

# with open(workdir/"clustering_data.json") as f:
#     data = json.load(f)

runscript = ""

runscript += f"{setup_env};\n"

# for bench in benchmarks:
#     bench_data = data[bench]
#     bench_dir = Path(workdir/bench.upper())
#     rep_data = bench_data[str(target_k)]["rep_rid"]
#     for rid in rep_data.values():
#         rid_dir = Path(bench_dir/f"papi/{rid}")
#         if Path(rid_dir/"data").exists():
#             shutil.rmtree(rid_dir/"data")
#         Path(rid_dir/"data").mkdir(parents=True, exist_ok=True)
        
#         for papi_cmd in papi_cmds:
#             runscript += f"cd {rid_dir.as_posix()} && {papi_cmd} && ./{bench}_papi_{rid};\n"

# with open(f"run_all_{target_k}_papi_point.sh", "w") as f:
#     f.write(runscript)

for bench in benchmarks:
    bench_dir = Path(workdir/bench.upper())
    papi_naive_dir = Path(bench_dir/"papi_naive")
    if Path(papi_naive_dir/"data").exists():
        shutil.rmtree(papi_naive_dir/"data")
    Path(papi_naive_dir/"data").mkdir(exist_ok=False)
    for papi_cmd in papi_cmds:
        runscript += f"cd {papi_naive_dir.as_posix()} && {papi_cmd} && ./{bench}_papi_naive;\n"

with open(f"run_all_naive_papi_point.sh", "w") as f:
    f.write(runscript)

