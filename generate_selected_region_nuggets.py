import subprocess
from multiprocessing import Pool
from pathlib import Path
import os
import argparse
import json

parser = argparse.ArgumentParser()  
parser.add_argument("--ifclean", type=bool, default=False)
parser.add_argument("--arch", type=str, default="x86_64")
args = parser.parse_args()

selected_region_info_file = Path("/home/studyztp/test_ground/experiments/hardware-profiling/hardware_tunning/NPB3.4-OMP-custom-makefile/randomly_selected_region_B_1000000000_1.json")

size = "B"
region_size = 1000_000_000
thread = 1
workdir = Path().cwd()
arch = args.arch


with open(selected_region_info_file, "r") as f:
    all_info = json.load(f)

must_env = os.environ

for bench, bench_info in all_info.items():
    bench_env = must_env.copy()
    bench_env["PROGRAM"] = bench
    bench_env["REGION_LENGTH"] = str(region_size)
    bench_env["SIZE"] = size
    bench_env["TARGET_ARCH"] = arch
    bench_env["THREAD_SIZE"] = str(thread)
    for region_id in bench_info:
        region_env = bench_env.copy()
        region_env["REGION_ID"] = region_id
        if args.ifclean:
            subprocess.run(["make", "single_thread_c_m5_fs_measuring"], cwd=workdir.as_posix(), env=region_env)
            subprocess.run(["make", "single_thread_c_papi_measuring"], cwd=workdir.as_posix(), env=region_env)
        subprocess.run(["make", "final_compile_single_thread_c_m5_fs_measuring"], cwd=workdir.as_posix(), env=region_env)
        subprocess.run(["make", "final_compile_single_thread_c_papi_measuring"], cwd=workdir.as_posix(), env=region_env)
        

