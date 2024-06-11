from pathlib import Path

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
size = "B"

current_location = Path.cwd()

output_bash_aarch64_script = Path("build_n_run_aarch64_profiling.sh")
output_bash_x86_64_script = Path("build_n_run_x86_64_profiling.sh")

aarch64_environment_setup = f"export LD_LIBRARY_PATH={current_location}/common/" \
    + "aarch64-unknown-linux-gnu:" \
    + f"{current_location}/common/all_papi/aarch64/lib:$LD_LIBRARY_PATH;\n" \
    + "export OMP_NUM_THREADS=1;"
x86_64_environment_setup = f"export LD_LIBRARY_PATH={current_location}/common/" \
    + "x86_64-unknown-linux-gnu:" \
    + f"{current_location}/common/all_papi/x86_64/lib:$LD_LIBRARY_PATH;\n" \
    + "export OMP_NUM_THREADS=1;"

with output_bash_aarch64_script.open("w") as f:
    with output_bash_x86_64_script.open("w") as f2:
        f.write(aarch64_environment_setup + "\n")
        f2.write(x86_64_environment_setup + "\n")
        for bench in benchmarks:
            f.write(f"make clean_all PROGRAM={bench};\n")
            f.write(f"make profiling PROGRAM={bench} SIZE={size} TARGET_ARCH=aarch64;\n")
            f2.write(f"make cross_compile_profiling PROGRAM={bench} SIZE={size} TARGET_ARCH=x86_64;\n")
        for bench in benchmarks:
            f.write(f"cd {current_location}/{bench.upper()}/profiling && ./$(ls {bench}_aarch64_*.profiling);\n")
            f2.write(f"cd {current_location}/{bench.upper()}/profiling/x86_64 && ./$(ls {bench}_x86_64_*.profiling);\n")
