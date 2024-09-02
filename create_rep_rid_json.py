import json
from pathlib import Path
import argparse

parser = argparse.ArgumentParser(description='Create a JSON file with the rep_rid data')

parser.add_argument('--input', type=str, help='Path to the input file')
parser.add_argument('--output', type=str, help='Path to the output file')
parser.add_argument("--k", type=int, help="Number of k")

args = parser.parse_args()

print(args)

input_file = Path(args.input)
output_file = Path(args.output)
k = args.k

with open(input_file, 'r') as f:
    input_data = json.load(f)

output_data = {}

for bench, bench_data in input_data.items():
    output_data[bench] = list(bench_data[str(k)]["rep_rid"].values())

with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=4)

