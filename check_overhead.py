import subprocess
from multiprocessing import Pool
from pathlib import Path
import os
import argparse

# benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
benchmarks = ["cg", "ep", "ft", "is", "mg", "sp"]

workdir = Path().cwd()
num_thread = 8
region_size = 1000_000_000

must_env = os.environ
must_env["LD_LIBRARY_PATH"] = f"{workdir.as_posix()}/common/aarch64-unknown-linux-gnu"
must_env["LD_LIBRARY_PATH"].append(f"{workdir.as_posix()}/common/all_")

