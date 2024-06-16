import json
from pathlib import Path

workdir = Path().cwd()  

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]

size = "B"
region_length = 100000000

x86_64_script = ""
aarch64_script = ""

# setup enviornment
x86_64_script += "export OMP_NUM_THREADS=1;\n" \
    f"export LD_LIBRARY_PATH={workdir.as_posix()}/common/x86_64-unknown-linux-gnu:" \
    f"{workdir.as_posix()}/common/all_papi/x86_64/lib:$LD_LIBRARY_PATH;\n"
aarch64_script += "export OMP_NUM_THREADS=1;\n" \
    f"export LD_LIBRARY_PATH={workdir.as_posix()}/common/aarch64-unknown-linux-gnu:" \
    f"{workdir.as_posix()}/common/all_papi/aarch64/lib:$LD_LIBRARY_PATH;\n"

for bench in benchmarks:
    # measure naive time
    x86_64_script += f"cd {workdir.as_posix()}/{bench.upper()}/papi_naive/x86_64 &&  time ./{bench}_x86_64_*.papi_naive > time.log 2>> time.err;\n"
    aarch64_script += f"cd {workdir.as_posix()}/{bench.upper()}/papi_naive/aarch64 &&  time ./{bench}_aarch64_*.papi_naive > time.log 2>> time.err;\n"
    # measure profiling time with bbv
    x86_64_script += f"cd {workdir.as_posix()}/{bench.upper()}/profiling/{region_length}/x86_64 &&  time ./{bench}_x86_64_*.profiling > time.log 2>> time.err;\n"
    aarch64_script += f"cd {workdir.as_posix()}/{bench.upper()}/profiling/{region_length}/aarch64 &&  time ./{bench}_aarch64_*.profiling > time.log 2>> time.err;\n"
    # measure papi profiling time
    x86_64_script += f"cd {workdir.as_posix()}/{bench.upper()}/papi_profiling/x86_64 &&  time ./{bench}_x86_64_*.papi_profiling > time.log 2>> time.err;\n"
    aarch64_script += f"cd {workdir.as_posix()}/{bench.upper()}/papi_profiling/aarch64 &&  time ./{bench}_aarch64_*.papi_profiling > time.log 2>> time.err;\n"

with open("measure_overhead_x86_64.sh", "w") as f:
    f.write(x86_64_script)

with open("measure_overhead_aarch64.sh", "w") as f:
    f.write(aarch64_script) 
