import subprocess
from multiprocessing import Pool
from pathlib import Path
import os
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("--region_size_list", nargs="+", type=int, default=[1000_000_000])
parser.add_argument("--arch", type=str, default="aarch64")
parser.add_argument("--machine_name", type=str, default="saphir")
parser.add_argument("--threads", nargs="+", type=int, default=[1, 8])
parser.add_argument("--size_list", nargs="+", type=str, default=["D"])
parser.add_argument("--if_make_base", type=bool, default=False)
parser.add_argument("--if_make_final", type=bool, default=False)
parser.add_argument("--if_run", type=bool, default=False)
parser.add_argument("--pool_size", type=int, default=16)

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
region_size_list = args.region_size_list
arch = args.arch
size_list = args.size_list
pool_size = args.pool_size

workdir = Path().cwd()

must_env = os.environ
must_env["LD_LIBRARY_PATH"] = f"{workdir.as_posix()}/common/{arch}-unknown-linux-gnu"
must_env["LD_LIBRARY_PATH"] += f":{workdir.as_posix()}/common/all_papi/{arch}/lib"

if args.if_make_base:
    for bench in benchmarks:
        bench_env = must_env.copy()
        bench_env["PROGRAM"] = bench
        for size in size_list:
            size_env = bench_env.copy()
            size_env["SIZE"] = size
            for region_size in region_size_list:
                region_size_env = size_env.copy()
                region_size_env["REGION_LENGTH"] = str(region_size)
                region_size_env["TARGET_ARCH"] = arch
                # c_papi_naive
                process_this(
                    {
                        "cmd": ["make", "c_time_naive"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/make_base_c_time_naive_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/make_base_c_time_naive_{size}_{region_size}.err").as_posix()
                    }
                )
                                # c_papi_naive
                process_this(
                    {
                        "cmd": ["make", "c_papi_naive"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/make_base_c_papi_naive_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/make_base_c_papi_naive_{size}_{region_size}.err").as_posix()
                    }
                )

if args.if_make_final:
    for bench in benchmarks:
        bench_env = must_env.copy()
        bench_env["PROGRAM"] = bench
        for size in size_list:
            size_env = bench_env.copy()
            size_env["SIZE"] = size
            for region_size in region_size_list:
                region_size_env = size_env.copy()
                region_size_env["REGION_LENGTH"] = str(region_size)
                region_size_env["TARGET_ARCH"] = arch
                # final_compile_c_papi_naive
                process_this(
                    {
                        "cmd": ["make", "final_compile_c_time_naive"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/final_compile_c_time_naive_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/final_compile_c_time_naive_{size}_{region_size}.err").as_posix()
                    }
                )
                # final_compile_c_papi_naive
                process_this(
                    {
                        "cmd": ["make", "final_compile_c_papi_naive"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/final_compile_c_papi_naive_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/final_compile_c_papi_naive_{size}_{region_size}.err").as_posix()
                    }
                )

if args.if_run:
    runs = []
    num_runs = 10

    papi_event = ['PAPI_TOT_CYC', 'PAPI_TOT_INS', 'PAPI_BR_MSP', 'PAPI_L1_DCA', 'PAPI_L2_DCA']

    for bench in benchmarks:
        for size in size_list:
            for thread in threads:
                for exp_name in ["c_time_naive", "c_papi_naive"]:
                    must_env["OMP_NUM_THREADS"] = str(thread)
                    if thread == 1:
                        cpu_list = "0"
                    else:
                        cpu_list = f"0-{thread-1}"
                    for index in range(num_runs):
                        event_env = must_env.copy()
                        event_env["PAPI_EVENTS"] = ",".join(papi_event)
                        # c_papi_naive
                        exp_name = "c_time_naive"
                        exp_dir = Path(workdir/f"{bench.upper()}/{size}/{exp_name}/{arch}")
                        file = exp_dir.glob(f"*.{exp_name}")
                        filename = None
                        for f in file:
                            print(f)
                            filename = f.name
                        run_env = event_env.copy()
                        run_env["PAPI_OUTPUT_DIRECTORY"] = Path(exp_dir/f"papi_output_{thread}_{index}").as_posix()
                        runs.append(
                            {
                                "cmd": ["taskset", "--cpu-list", cpu_list, f"./{filename}"],
                                "env": run_env.copy(),
                                "dir": exp_dir.as_posix(),
                                "stdout": Path(exp_dir/f"{thread}_{index}.stdout"),
                                "stderr": Path(exp_dir/f"{thread}_{index}.stderr")
                            }
                        )

    with Pool(pool_size) as pool:
        pool.map(process_this, runs)

print("All done!")

