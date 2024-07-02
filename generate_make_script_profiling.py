import subprocess
from multiprocessing import Pool
from pathlib import Path
import os

def run_this(run_ball):
    command = run_ball["cmd"]
    env = run_ball["env"]
    dir = run_ball["dir"]
    stdout_path = run_ball["stdout"]
    stderr_path = run_ball["stderr"]
    with open(stdout_path, "w") as stdout, open(stderr_path, "w") as stderr:
        process_code = subprocess.run(command, cwd=dir, env=env, stdout=stdout, stderr=stderr)
    print("finished", command, process_code)
    return process_code

workdir = Path().cwd()
benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
threads = [1, 2, 8]
region_size = 100000000
arch = "aarch64"
size = "B"

must_env = os.environ
must_env["LD_LIBRARY_PATH"] = f"{workdir.as_posix()}/common/aarch64-unknown-linux-gnu"

# clean all current benchmark directories
for benchmark in benchmarks:
    must_env["PROGRAM"] = benchmark
    subprocess.run(["make", "clean_all"], cwd=workdir.as_posix(), env=must_env)

# make all benchmarks
for benchmark in benchmarks:
    must_env["PROGRAM"] = benchmark
    subprocess.run(["make", "-B", "all"], cwd=workdir.as_posix(), env=must_env)
    subprocess.run(["make", "naive"], cwd=workdir.as_posix(), env=must_env)
    subprocess.run(["make", "final_compile_naive"], cwd=workdir.as_posix(), env=must_env)
    subprocess.run(["make", "c_profiling"], cwd=workdir.as_posix(), env=must_env)
    subprocess.run(["make", "final_compile_c_profiling"], cwd=workdir.as_posix(), env=must_env)

runs = []

for benchmark in benchmarks:
    benchdir = Path(workdir/benchmark.upper())
    profiling_dir = Path(benchdir/f"{size}/c_profiling/{region_size}/{arch}")
    file = profiling_dir.glob("*.profiling")
    for f in file:
        cmd = [f"./{f.name}"]
    for thread in threads:
        run_env = must_env.copy()
        run_env["OMP_NUM_THREADS"] = str(thread)
        stdout = Path(profiling_dir/f"{benchmark}_{thread}.stdout")
        stderr = Path(profiling_dir/f"{benchmark}_{thread}.stderr")
        runs.append({"cmd": cmd, "env": run_env, "dir": profiling_dir, "stdout": stdout, "stderr": stderr})

with Pool(8) as p:
    p.map(run_this, runs)

