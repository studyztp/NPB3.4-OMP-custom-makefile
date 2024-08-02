import subprocess
from multiprocessing import Pool
from pathlib import Path
import os
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--region_size", type=int, default=1000_000_000)
parser.add_argument("--arch", type=str, default="aarch64")
parser.add_argument("--machine_name", type=str, default="saphir")
parser.add_argument("--threads", type=int, default=8)
parser.add_argument("--size", type=str, default="C")
parser.add_argument("--if_make_base", type=bool, default=False)
parser.add_argument("--if_make_final", type=bool, default=False)
parser.add_argument("--if_run", type=bool, default=False)
parser.add_argument("--pool_size", type=int, default=1)

args = parser.parse_args()

def process_this(run_ball):
    command = run_ball["cmd"]
    env = run_ball["env"]
    dir = run_ball["dir"]
    if "stdout" in run_ball:
        stdout_path = run_ball["stdout"]
    else:
        stdout_path = None
    if "stderr" in run_ball:
        stderr_path = run_ball["stderr"]
    else:
        stderr_path = None
    if "OMP_NUM_THREADS" in env:
        num_threads = env["OMP_NUM_THREADS"]
    else: 
        num_threads = 0
    if stdout_path is not None:
        with open(stdout_path, "w") as stdout, open(stderr_path, "w") as stderr:
            process_code = subprocess.run(command, cwd=dir, env=env, stdout=stdout, stderr=stderr)
        print("finished", dir, command, f"{num_threads} threads", process_code)
    else:
        process_code = subprocess.run(command, cwd=dir, env=env)
        print("finished", dir, command, process_code)
    return process_code

benchmarks = ["bt", "cg", "ep", "ft", "lu", "mg", "sp"]
threads = args.threads
region_size = args.region_size
arch = args.arch
size = args.size
pool_size = args.pool_size

workdir = Path().cwd()
overhead_marker_info_dir = Path("/home/studyztp/test_ground/experiments/hardware-profiling/nugget-paper")
num_markers = 10

must_env = os.environ
must_env["LD_LIBRARY_PATH"] = f"{workdir.as_posix()}/common/{arch}-unknown-linux-gnu"
must_env["LD_LIBRARY_PATH"] += f":{workdir.as_posix()}/common/all_papi/{arch}/lib"

if args.if_make_base:
    for bench in benchmarks:
        bench_env = must_env.copy()
        bench_env["PROGRAM"] = bench
        bench_env["SIZE"] = size
        bench_env["REGION_LENGTH"] = str(region_size)
        bench_env["TARGET_ARCH"] = arch
        for i in range(num_markers):
            bench_marker_dir = Path(overhead_marker_info_dir/f"{bench}-overhead-test-marker-info-dir")
            marker_file = Path(bench_marker_dir/f"{bench}_{i}_info.txt")
            print(marker_file.as_posix())
            found_files = bench_marker_dir.glob(f"basic_block_info_output_*")
            for f in found_files:
                basic_block_info_file = Path(bench_marker_dir/f.name)
            marker_env = bench_env.copy()
            marker_env["OVERHEAD_MEASURING_BB_ORDER_FILE"] = basic_block_info_file.as_posix()
            marker_env["OVERHEAD_MEASURING_INPUT_FILE"] = marker_file.as_posix()
            marker_env["OVERHEAD_MEASURING_OUTPUT_NAME"] = f"{region_size}_{threads}_{i}"
            if threads == 1:
                subprocess.run(["make", "single_thread_c_marker_overhead_measuring"], cwd=workdir.as_posix(), env=marker_env)
            else:    
                subprocess.run(["make", "c_marker_overhead_measuring"], cwd=workdir.as_posix(), env=marker_env)

if args.if_make_final:
    for bench in benchmarks:
        bench_env = must_env.copy()
        bench_env["PROGRAM"] = bench
        bench_env["SIZE"] = size
        bench_env["REGION_LENGTH"] = str(region_size)
        bench_env["TARGET_ARCH"] = arch
        bench_env["OMP_NUM_THREADS"] = str(threads)
        for i in range(num_markers):
            bench_marker_dir = Path(overhead_marker_info_dir/f"{bench}-overhead-test-marker-info-dir")
            marker_file = Path(bench_marker_dir/f"{bench}_{i}_info.txt")
            found_files = bench_marker_dir.glob(f"basic_block_info_output_*")
            for f in found_files:
                basic_block_info_file = Path(bench_marker_dir/f.name)
            marker_env = bench_env.copy()
            marker_env["OVERHEAD_MEASURING_BB_ORDER_FILE"] = basic_block_info_file.as_posix()
            marker_env["OVERHEAD_MEASURING_INPUT_FILE"] = marker_file.as_posix()
            marker_env["OVERHEAD_MEASURING_OUTPUT_NAME"] = f"{region_size}_{threads}_{i}"
            if threads == 1:
                subprocess.run(["make", "final_compile_single_thread_c_marker_overhead_measuring"], cwd=workdir.as_posix(), env=marker_env)
            else:
                subprocess.run(["make", "final_compile_c_marker_overhead_measuring"], cwd=workdir.as_posix(), env=marker_env)

if args.if_run:
    runs = []

    papi_evnet = None

    if args.machine_name == "saphir":
        papi_event = [['PAPI_TOT_CYC', 'PAPI_TOT_INS', 'PAPI_BR_MSP', 'PAPI_L1_DCA', 'PAPI_L2_DCA'],]
    elif args.machine_name == "challenger":
        papi_event = [['PAPI_TOT_CYC', 'PAPI_TOT_INS', 'PAPI_BR_MSP', 'PAPI_L1_DCA', 'PAPI_L2_DCR'],]
    elif args.machine_name == "saaz":
        papi_event = [['PAPI_TOT_CYC', 'PAPI_TOT_INS', 'PAPI_BR_MSP', 'PAPI_L1_DCA', 'PAPI_L2_DCR'],]

    for bench in benchmarks:
        if threads == 1:
            bench_dir = Path(workdir/f"{bench.upper()}/{size}/single_thread_c_marker_overhead_measuring")
        else:
            bench_dir = Path(workdir/f"{bench.upper()}/{size}/c_marker_overhead_measuring")
        for i in range(num_markers):
            run_dir = Path(bench_dir/f"{region_size}_{threads}_{i}/{arch}")
            if threads == 1:
                for f in run_dir.glob("*.single_thread_c_marker_overhead_measuring"):
                    filename = f.name
            else:
                for f in run_dir.glob("*.c_marker_overhead_measuring"):
                    filename = f.name
            run_env = must_env.copy()
            run_env["OMP_NUM_THREADS"] = str(threads)
            run_env["PAPI_EVENT"] = " ".join(papi_event[0])
            runs.append(
                {
                    "cmd": [f"./{filename}"],
                    "env": run_env.copy(),
                    "dir": run_dir.as_posix(),
                    "stdout": run_dir/"stdout.log",
                    "stderr": run_dir/"stderr.log"
                }
            )
    
    with Pool(pool_size) as p:
        p.map(process_this, runs)

print("All done!")
