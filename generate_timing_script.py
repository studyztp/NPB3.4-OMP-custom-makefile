from pathlib import Path 

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
region_length = 100_000_000

script = ""
sizes = ["B"]

workdir = Path().cwd()

for bench in benchmarks:
    script += f"make clean_all_testing PROGRAM={bench};\n"
    script += f"make all PROGRAM={bench} SIZE={size};\n"

    script += f"make test_use_naive PROGRAM={bench} SIZE={size};\n"
    script += f"make cpp_atomic_profiling PROGRAM={bench} SIZE={size};\n"
    script += f"make cpp_parallel_profiling PROGRAM={bench} SIZE={size};\n"
    script += f"make c_atomic_profiling PROGRAM={bench} SIZE={size};\n"
    script += f"make c_parallel_profiling PROGRAM={bench} SIZE={size};\n"
