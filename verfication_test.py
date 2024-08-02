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
parser.add_argument("--if_make_source", type=bool, default=False)
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

if args.if_make_source:
    make_source_proc_list = []
    for bench in benchmarks:
        bench_env = must_env.copy()
        bench_env["PROGRAM"] = bench
        subprocess.run(["make", "clean_all"], cwd=workdir.as_posix(), env=bench_env)
        stdout = Path(workdir/f"{bench.upper()}/make_source.log")
        stderr = Path(workdir/f"{bench.upper()}/make_source.err")
        process_this({
            "cmd": ["make", "-B", "all"],
            "env": bench_env,
            "dir": workdir.as_posix(),
            "stdout": stdout.as_posix(),
            "stderr": stderr.as_posix()
        })

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
                        "cmd": ["make", "c_papi_naive"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/make_base_c_papi_naive_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/make_base_c_papi_naive_{size}_{region_size}.err").as_posix()
                    }
                )
                # c_profiling
                process_this(
                    {
                        "cmd": ["make", "c_profiling"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/make_base_c_profiling_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/make_base_c_profiling_{size}_{region_size}.err").as_posix()
                    }
                )
                # c_papi_profiling
                process_this(
                    {
                        "cmd": ["make", "c_papi_profiling"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/make_base_c_papi_profiling_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/make_base_c_papi_profiling_{size}_{region_size}.err").as_posix()
                    }
                )
                # single_thread_c_profiling
                process_this(
                    {
                        "cmd": ["make", "single_thread_c_profiling"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/make_base_single_thread_c_profiling_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/make_base_single_thread_c_profiling_{size}_{region_size}.err").as_posix()
                    }
                )
                # single_thread_c_papi_profiling
                process_this(
                    {
                        "cmd": ["make", "single_thread_c_papi_profiling"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/make_base_single_thread_c_papi_profiling_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/make_base_single_thread_c_papi_profiling_{size}_{region_size}.err").as_posix()
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
                        "cmd": ["make", "final_compile_c_papi_naive"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/final_compile_c_papi_naive_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/final_compile_c_papi_naive_{size}_{region_size}.err").as_posix()
                    }
                )
                # final_compile_c_profiling
                process_this(
                    {
                        "cmd": ["make", "final_compile_c_profiling"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/final_compile_c_profiling_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/final_compile_c_profiling_{size}_{region_size}.err").as_posix()
                    }
                )
                # final_compile_c_papi_profiling
                process_this(
                    {
                        "cmd": ["make", "final_compile_c_papi_profiling"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/final_compile_c_papi_profiling_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/final_compile_c_papi_profiling_{size}_{region_size}.err").as_posix()
                    }
                )
                # final_compile_single_thread_c_profiling
                process_this(
                    {
                        "cmd": ["make", "final_compile_single_thread_c_profiling"],
                        "env": region_size_env,
                        "dir": workdir.as_posix(),
                        "stdout": Path(workdir/f"{bench.upper()}/final_compile_single_thread_c_profiling_{size}_{region_size}.log").as_posix(),
                        "stderr": Path(workdir/f"{bench.upper()}/final_compile_single_thread_c_profiling_{size}_{region_size}.err").as_posix()
                    }
                )
                # final_compile_single_thread_c_papi_prof

if args.if_run:
    runs = []
    num_runs = 3

    papi_evnet = None

    if args.machine_name == "saphir":
        papi_event = [['PAPI_TOT_CYC', 'PAPI_TOT_INS', 'PAPI_BR_MSP', 'PAPI_L1_DCA', 'PAPI_L2_DCA'],]
    elif args.machine_name == "challenger":
        papi_event = [['PAPI_TOT_CYC', 'PAPI_TOT_INS', 'PAPI_BR_MSP', 'PAPI_L1_DCA', 'PAPI_L2_DCR'],]
    elif args.machine_name == "saaz":
        papi_event = [['PAPI_TOT_CYC', 'PAPI_TOT_INS', 'PAPI_BR_MSP', 'PAPI_L1_DCA', 'PAPI_L2_DCR'],]

    for bench in benchmarks:
        for size in size_list:
            for thread in threads:
                must_env["OMP_NUM_THREADS"] = str(thread)
                # c_papi_naive
                # c_papi_profiling
                for index in range(num_runs):
                    for event in papi_event:
                        event_env = must_env.copy()
                        event_env["PAPI_EVENTS"] = ",".join(event)
                        # c_papi_naive
                        exp_name = "c_papi_naive"
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
                                "cmd": [f"./{filename}"],
                                "env": run_env.copy(),
                                "dir": exp_dir.as_posix(),
                                "stdout": Path(exp_dir/f"{thread}_{index}.stdout"),
                                "stderr": Path(exp_dir/f"{thread}_{index}.stderr")
                            }
                        )
                        for region_size in region_size_list:
                            # c_papi_profiling
                            if thread == 1:
                                exp_name = "singe_thread_c_papi_profiling"
                            else:
                                exp_name = "c_papi_profiling"
                            exp_dir = Path(workdir/f"{bench.upper()}/{size}/{exp_name}/{region_size}/{arch}")
                            run_dir = Path(exp_dir/f"run_{thread}_{index}")
                            if run_dir.exists():
                                shutil.rmtree(run_dir)
                            run_dir.mkdir()
                            file = exp_dir.glob(f"*.{exp_name}")
                            filename = None
                            for f in file:
                                print(f)
                                filename = f.name
                            shutil.copy(Path(exp_dir/filename), Path(run_dir/filename))
                            run_env = event_env.copy()
                            run_env["PAPI_OUTPUT_DIRECTORY"] = Path(exp_dir/f"papi_output_{thread}_{index}").as_posix()
                            runs.append(
                                {
                                    "cmd": [f"./{filename}"],
                                    "env": run_env.copy(),
                                    "dir": run_dir.as_posix(),
                                    "stdout": Path(exp_dir/f"{thread}_{index}.stdout"),
                                    "stderr": Path(exp_dir/f"{thread}_{index}.stderr")
                                }
                            )
                            if thread == 1:
                                exp_name = "single_thread_c_profiling"
                            else:
                                exp_name = "c_profiling"
                            exp_dir = Path(workdir/f"{bench.upper()}/{size}/{exp_name}/{region_size}/{arch}")
                            file = exp_dir.glob(f"*.{exp_name}")
                            filename = None
                            for f in file:
                                print(f)
                                filename = f.name
                            run_dir = Path(exp_dir/f"run_{thread}_{index}")
                            if run_dir.exists():
                                shutil.rmtree(run_dir)
                            run_dir.mkdir()
                            shutil.copy(Path(exp_dir/filename), Path(run_dir/filename))
                            runs.append(
                                {
                                    "cmd": [f"./{filename}"],
                                    "env": run_env.copy(),
                                    "dir": run_dir.as_posix(),
                                    "stdout": Path(run_dir/f"{thread}_{index}.stdout"),
                                    "stderr": Path(run_dir/f"{thread}_{index}.stderr")
                                }
                            )

    with Pool(pool_size) as pool:
        pool.map(process_this, runs)

print("All done!")

