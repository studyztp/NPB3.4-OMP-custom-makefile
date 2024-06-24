import os
import glob
import subprocess
from pathlib import Path
from multiprocessing import Pool


def process_this(run_ball):
    thread = run_ball["thread"]
    rid = run_ball["rid"]
    cmd = run_ball["cmd"]
    env = run_ball["env"]
    dir = run_ball["dir"]
    stdout_path = Path(f"{dir}/timing_{thread}_threads_{rid}.log")
    stderr_path = Path(f"{dir}/timing_{thread}_threads_{rid}.err")
    with open(stdout_path, "w") as stdout:
        with open(stderr_path, "w") as stderr:
            process = subprocess.run(cmd, cwd=dir ,env=env, stdout=stdout, stderr=stderr)
    print(f"{cmd} finished with return code {process.returncode}")
    return process

workdir = Path().cwd()
sizes = ["B", "C"]
region_length = 100_000_000
benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
rid = 0
thread_num = 8

runs = []

must_env = os.environ.copy()
if "LD_LIBRARY_PATH" in must_env:
    must_env["LD_LIBRARY_PATH"] += f"{workdir.as_posix()}/common/x86_64-unknown-linux-gnu"
else:
    must_env["LD_LIBRARY_PATH"] = f"{workdir.as_posix()}/common/x86_64-unknown-linux-gnu"

for size in sizes:
    for bench in benchmarks:
        bench_dir = Path(workdir / bench.upper())

        run_env = must_env.copy()
        run_env["OMP_NUM_THREADS"] = str(thread_num)
    
        run_dir = Path(bench_dir / f"naive/{size}")
        files = glob.glob(f"{run_dir.as_posix()}/*.naive")
        run = ["time", f"{files[0]}"]

        run_ball = {
            "thread" : thread_num,
            "rid" : rid,
            "cmd" : run,
            "env" : run_env,
            "dir" : run_dir.as_posix()
        }

        runs.append(run_ball)

        
        run_dir = Path(bench_dir / f"cpp_atomic_profiling/{size}/{region_length}")
        files = glob.glob(f"{run_dir.as_posix()}/*.cpp_atomic_profiling")
        run = ["time", f"{files[0]}"]

        run_ball = {
            "thread" : thread_num,
            "rid" : rid,
            "cmd" : run,
            "env" : run_env,
            "dir" : run_dir.as_posix()
        }

        runs.append(run_ball)

        
        run_dir = Path(bench_dir / f"cpp_parallel_profiling/{size}/{region_length}")
        files = glob.glob(f"{run_dir.as_posix()}/*.cpp_parallel_profiling")
        run = ["time", f"{files[0]}"]

        run_ball = {
            "thread" : thread_num,
            "rid" : rid,
            "cmd" : run,
            "env" : run_env,
            "dir" : run_dir.as_posix()
        }

        runs.append(run_ball)

        
        run_dir = Path(bench_dir / f"c_atomic_profiling/{size}/{region_length}")
        files = glob.glob(f"{run_dir.as_posix()}/*.c_atomic_profiling")
        run = ["time", f"{files[0]}"]

        run_ball = {
            "thread" : thread_num,
            "rid" : rid,
            "cmd" : run,
            "env" : run_env,
            "dir" : run_dir.as_posix()
        }

        runs.append(run_ball)

        
        run_dir = Path(bench_dir / f"c_parallel_profiling/{size}/{region_length}")
        files = glob.glob(f"{run_dir.as_posix()}/*.c_parallel_profiling")
        run = ["time", f"{files[0]}"]

        run_ball = {
            "thread" : thread_num,
            "rid" : rid,
            "cmd" : run,
            "env" : run_env,
            "dir" : run_dir.as_posix()
        }

        runs.append(run_ball)

with Pool(4) as p:
    p.map(process_this, runs)
