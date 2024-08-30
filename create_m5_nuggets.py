import subprocess
from pathlib import Path
import os
import argparse
import shutil
import random
import json

parser = argparse.ArgumentParser()

parser.add_argument("--region_size", type=int, default=1000_000_000)
parser.add_argument("--arch", type=str, default="aarch64")
parser.add_argument("--machine_name", type=str, default="saphir")
parser.add_argument("--thread", type=int, default=1)
parser.add_argument("--size", type=str, default="C")
parser.add_argument("--if_make_base", type=bool, default=False)
parser.add_argument("--if_make_final", type=bool, default=False)
parser.add_argument("--region_info", type=str, default="")

args = parser.parse_args()

def process_this(run_ball):
    command = run_ball["cmd"]
    env = run_ball["env"]
    dir = run_ball["dir"]
    if not Path(dir).exists():
        Path(dir).mkdir(exist_ok=False)
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

benchmarks = ["bt", "cg", "ep", "is", "ft", "lu", "mg", "sp"]
thread = args.thread
region_size = args.region_size
arch = args.arch
size = args.size

if thread == 1:
    program_type = "single_thread_c_m5_fs_measuring"
else:
    program_type = "c_m5_fs_measuring"

print("all input arguments are", args)

with open(args.region_info, "r") as f:
    region_info = json.load(f)

workdir = Path().cwd()

must_env = os.environ
must_env["LD_LIBRARY_PATH"] = f"{workdir.as_posix()}/common/{arch}-unknown-linux-gnu"
must_env["LD_LIBRARY_PATH"] += f":{workdir.as_posix()}/common/all_papi/{arch}/lib"

if args.if_make_base:
    for bench in benchmarks:
        output_log_dir = Path(workdir/f"{bench.upper()}/m5_output_logs")
        output_log_dir.mkdir(exist_ok=True)
        for rid in region_info[bench]:
            rid_env = must_env.copy()
            rid_env["REGION_ID"] = str(rid)
            rid_env["REGION_LENGTH"] = str(region_size)
            rid_env["TRHEAD_SIZE"] = str(thread)
            rid_env["SIZE"] = size
            rid_env["PROGRAM"] = bench
            rid_env["TARGET_ARCH"] = arch

            process_this({
                "cmd": ["make", program_type],
                "env": rid_env,
                "dir": workdir.as_posix(),
                "stdout": f"{output_log_dir.as_posix()}/make_{bench}_{rid}_stdout.txt",
                "stderr": f"{output_log_dir.as_posix()}/make_{bench}_{rid}_stderr.txt"
            })

if args.if_make_final:
    for bench in benchmarks:
        output_log_dir = Path(workdir/f"{bench.upper()}/m5_output_logs")
        output_log_dir.mkdir(exist_ok=True)
        for rid in region_info[bench]:
            rid_env = must_env.copy()
            rid_env["REGION_ID"] = str(rid)
            rid_env["REGION_LENGTH"] = str(region_size)
            rid_env["TRHEAD_SIZE"] = str(thread)
            rid_env["SIZE"] = size
            rid_env["PROGRAM"] = bench
            rid_env["TARGET_ARCH"] = arch
            
            process_this({
                "cmd": ["make", f"final_compile_{program_type}"],
                "env": rid_env,
                "dir": workdir.as_posix(),
                "stdout": f"{output_log_dir.as_posix()}/final_compile_{bench}_{rid}_stdout.txt",
                "stderr": f"{output_log_dir.as_posix()}/final_compile_{bench}_{rid}_stderr.txt"
            })

print("All done!")
