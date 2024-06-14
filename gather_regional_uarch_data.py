from pathlib import Path
import subprocess
import argparse
import json


parser = argparse.ArgumentParser(description='Gather regional uarch data')
parser.add_argument('--output-filename', type=str, help='Path to output file')

args = parser.parse_args()

output_filename = Path(args.output_filename)

workdir = Path().cwd()

benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
region_size = 100000000

uarch_data = {}

architecture = subprocess.check_output(['uname', '-m']).decode().strip()
print(f"Machine architecture: {architecture}")

for bench in benchmarks:
    bench_dir = Path(workdir/bench.upper())
    bench_papi_profiling_dir = Path(bench_dir/f"papi_profiling/{region_size}/{architecture}/data")
    uarch_data[bench] = {}
    for batch in bench_papi_profiling_dir.iterdir():
        data_dir = Path(batch/"papi_hl_output/")
        file_path = data_dir.iterdir()[0]
        with open(file_path, 'r') as f:
            data = json.load(f)
        data = data["threads"]["0"]["regions"]
        for region, events in data.items():
            if region not in uarch_data[bench]:
                uarch_data[bench][region] = {}
            if "runtime" not in uarch_data[bench][region]:
                uarch_data[bench][region]["runtime"] = []
            for event, value in events.items():
                if "real_time_nsec" in event:
                    uarch_data[bench][region]["runtime"].append(int(value))
                elif "PAPI" in event:
                    uarch_data[bench][region][event] = int(value)

with open(output_filename, 'w') as f:
    json.dump(uarch_data, f, indent=4)
        

