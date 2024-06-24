from pathlib import Path 

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
region_length = 100_000_000

script = ""
testing_script = ""
size = "B"
repeat_testing = 2

workdir = Path().cwd()

testing_script += f"export LD_LIBRARY_PATH={workdir.as_posix()}/common/x86_64-unknown-linux-gnu:$LD_LIBRARY_PATH;\n"

for bench in benchmarks:
    script += f"make clean_all_testing PROGRAM={bench};\n"
    script += f"make all PROGRAM={bench} SIZE={size};\n"

    script += f"make test_use_naive PROGRAM={bench} SIZE={size};\n"
    script += f"make cpp_atomic_profiling PROGRAM={bench} SIZE={size};\n"
    script += f"make cpp_parallel_profiling PROGRAM={bench} SIZE={size};\n"
    script += f"make c_atomic_profiling PROGRAM={bench} SIZE={size};\n"
    script += f"make c_parallel_profiling PROGRAM={bench} SIZE={size};\n"

thread_num = 1

while thread_num < 17:
    testing_script += f"cd {workdir.as_posix()};\n"
    testing_script += f"export OMP_NUM_THREADS={thread_num};\n"
    
    for bench in benchmarks:
        testing_script += f"echo Testing {bench} for {thread_num} threads;\n"
        bench_dir = Path(workdir / bench.upper())
        for test_num in range(repeat_testing):
            testing_script += f"echo start timing naive for {thread_num} threads for {test_num} times;\n"
            testing_script += f"cd {bench_dir.as_posix()}/naive && (time ./*.naive) > timing_{thread_num}_threads_{test_num}.log 2>> timing_{thread_num}_threads_{test_num}.err;\n"
            testing_script += f"echo start timing cpp_atomic_profiling for {thread_num} threads for {test_num} times;\n"
            testing_script += f"cd {bench_dir.as_posix()}/cpp_atomic_profiling/{region_length} && (time ./*.cpp_atomic_profiling) > timing_{thread_num}_threads_{test_num}.log 2>> timing_{thread_num}_threads_{test_num}.err;\n"
            testing_script += f"echo start timing cpp_parallel_profiling for {thread_num} threads for {test_num} times;\n"
            testing_script += f"cd {bench_dir.as_posix()}/cpp_parallel_profiling/{region_length} && (time ./*.cpp_parallel_profiling) > timing_{thread_num}_threads_{test_num}.log 2>> timing_{thread_num}_threads_{test_num}.err;\n"
            testing_script += f"echo start timing c_atomic_profiling for {thread_num} threads for {test_num} times;\n"
            testing_script += f"cd {bench_dir.as_posix()}/c_atomic_profiling/{region_length} && (time ./*.c_atomic_profiling) > timing_{thread_num}_threads_{test_num}.log 2>> timing_{thread_num}_threads_{test_num}.err;\n"
            testing_script += f"echo start timing c_parallel_profiling for {thread_num} threads for {test_num} times;\n"
            testing_script += f"cd {bench_dir.as_posix()}/c_parallel_profiling/{region_length} && (time ./*.c_parallel_profiling) > timing_{thread_num}_threads_{test_num}.log 2>> timing_{thread_num}_threads_{test_num}.err;\n"
    thread_num *= 2

with open(workdir / "timing_script.sh", "w") as f:
    f.write(script)

with open(workdir / "testing_timing_script.sh", "w") as f:
    f.write(testing_script)
