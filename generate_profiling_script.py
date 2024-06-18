from pathlib import Path

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
size = "B"
region_size = 100000000

current_location = Path.cwd()

output_build_profiling_script = Path("build_profiling_base.sh")
output_bash_aarch64_script = Path("build_n_run_aarch64_profiling.sh")
output_bash_x86_64_script = Path("build_n_run_x86_64_profiling.sh")
diff_script = Path("diff.sh")

aarch64_environment_setup = f"export LD_LIBRARY_PATH={current_location}/common/" \
    + "aarch64-unknown-linux-gnu:" \
    + f"{current_location}/common/all_papi/aarch64/lib:$LD_LIBRARY_PATH;\n" \
    + "export OMP_NUM_THREADS=2;"
x86_64_environment_setup = f"export LD_LIBRARY_PATH={current_location}/common/" \
    + "x86_64-unknown-linux-gnu:" \
    + f"{current_location}/common/all_papi/x86_64/lib:$LD_LIBRARY_PATH;\n" \
    + "export OMP_NUM_THREADS=2;"

with output_build_profiling_script.open("w") as base_script:
    with output_bash_aarch64_script.open("w") as arm_script:
        with output_bash_x86_64_script.open("w") as x86_script:
            with diff_script.open("w") as diff_f:
                arm_script.write(aarch64_environment_setup + "\n")
                x86_script.write(x86_64_environment_setup + "\n")
                for bench in benchmarks:
                    base_script.write(f"make clean_all PROGRAM={bench};\n")
                    base_script.write(f"make profiling PROGRAM={bench} SIZE={size};\n")
                    arm_script.write(f"cd {current_location} && make final_compile_profiling PROGRAM={bench} SIZE={size} TARGET_ARCH=aarch64;\n")
                    x86_script.write(f"cd {current_location} && make final_compile_profiling PROGRAM={bench} SIZE={size} TARGET_ARCH=x86_64;\n")
                for bench in benchmarks:
                    arm_script.write(f"cd {current_location}/{bench.upper()}/profiling/{region_size}/aarch64 && ./$(ls {bench}_aarch64_*.profiling);\n")
                    x86_script.write(f"cd {current_location}/{bench.upper()}/profiling/{region_size}/x86_64 && ./$(ls {bench}_x86_64_*.profiling);\n")
                    diff_f.write(f"echo diff {bench.upper()};\n")
                    diff_f.write(f"diff {current_location}/{bench.upper()}/profiling/{region_size}/aarch64/profiler_output.txt {current_location}/{bench.upper()}/profiling/{region_size}/x86_64/profiler_output.txt;\n")
