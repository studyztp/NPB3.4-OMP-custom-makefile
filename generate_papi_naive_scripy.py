import json
from pathlib import Path

workdir = Path().cwd()  

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]

size = "B"

base_script = ""
x86_64_script = ""
aarch64_script = ""

for bench in benchmarks:
    base_script += f"make papi_naive PROGRAM={bench} SIZE={size};\n"
    x86_64_script += f"make final_compile_papi_naive PROGRAM={bench} SIZE={size} TARGET_ARCH=x86_64;\n"
    aarch64_script += f"make final_compile_papi_naive PROGRAM={bench} SIZE={size} TARGET_ARCH=aarch64;\n"

with open("build_papi_naive_base.sh", "w") as f:
    f.write(base_script)

with open("build_papi_naive_x86_64.sh", "w") as f:
    f.write(x86_64_script)

with open("build_papi_naive_aarch64.sh", "w") as f:
    f.write(aarch64_script)

