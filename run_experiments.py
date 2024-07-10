import subprocess
from multiprocessing import Pool
from pathlib import Path
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--region_size_list", nargs="+", type=int, default=[1000_000_000])
parser.add_argument("--arch", type=str, default="aarch64")
parser.add_argument("--size_list", nargs="+", type=str, default=["B"])
parser.add_argument("--exp_list", nargs="+", type=str, default=["naive"])
parser.add_argument("--threads", nargs="+", type=int, default=[1, 8])
parser.add_argument("--benchmarks", nargs="+", type=str, default=["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"])
parser.add_argument("--ifclean", type=bool, default=False)

args = parser.parse_args()

def run_this(run_ball):
    command = run_ball["cmd"]
    env = run_ball["env"]
    dir = run_ball["dir"]
    stdout_path = run_ball["stdout"]
    stderr_path = run_ball["stderr"]
    num_threads = env["OMP_NUM_THREADS"]
    with open(stdout_path, "w") as stdout, open(stderr_path, "w") as stderr:
        process_code = subprocess.run(command, cwd=dir, env=env, stdout=stdout, stderr=stderr)
    print("finished", dir, command, f"{num_threads} threads", process_code)
    return process_code

workdir = Path().cwd()
benchmarks = args.benchmarks
threads = args.threads
region_size_list = args.region_size_list
arch = args.arch
size_list = args.size_list
exp_list = args.exp_list

must_env = os.environ
must_env["LD_LIBRARY_PATH"] = f"{workdir.as_posix()}/common/{arch}-unknown-linux-gnu"

print(f"region_size_list: {region_size_list} arch: {arch} size_list: {size_list} exp_list: {exp_list}")
print(f"threads: {threads} benchmarks: {benchmarks} workdir: {workdir}")

# make all benchmarks
for benchmark in benchmarks:
    must_env["PROGRAM"] = benchmark
    if args.ifclean:
        subprocess.run(["make", "clean_all"], cwd=workdir.as_posix(), env=must_env)
        subprocess.run(["make", "-B", "all"], cwd=workdir.as_posix(), env=must_env)
    for size in size_list:
        for region_size in region_size_list:
            must_env["REGION_LENGTH"] = str(region_size)
            must_env["SIZE"] = size
            must_env["TARGET_ARCH"] = arch

            for exp_type in exp_list:
                subprocess.run(["make", exp_type], cwd=workdir.as_posix(), env=must_env)
                subprocess.run(["make", f"final_compile_{exp_type}"], cwd=workdir.as_posix(), env=must_env)

runs = []

for benchmark in benchmarks:
    benchdir = Path(workdir/benchmark.upper())
    for size in size_list:
        for region_size in region_size_list:
            for exp_type in exp_list:
                if exp_type == "naive":
                    exp_dir = Path(benchdir/f"{size}/{exp_type}/{arch}")
                else:
                    exp_dir = Path(benchdir/f"{size}/{exp_type}/{region_size}/{arch}")
                file = exp_dir.glob(f"*.{exp_type}")
                for f in file:
                    print(f)
                    cmd = ["time", f"./{f.name}"]
                for thread in threads:
                    run_env = must_env.copy()
                    run_env["OMP_NUM_THREADS"] = str(thread)
                    stdout = Path(exp_dir/f"{benchmark}_{thread}.stdout")
                    stderr = Path(exp_dir/f"{benchmark}_{thread}.stderr")
                    runs.append({"cmd": cmd, "env": run_env, "dir": exp_dir, "stdout": stdout, "stderr": stderr})

with Pool(16) as p:
    p.map(run_this, runs)

