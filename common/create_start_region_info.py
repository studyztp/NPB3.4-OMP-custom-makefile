import argparse
from pathlib import Path

current_dir = Path().cwd()

parser = argparse.ArgumentParser(description="Create start region info")

parser.add_argument(
    "original_file",
    type=str,
    help="Path to the original file",
)

args = parser.parse_args()

marker_info = []

with open(args.original_file, "r") as f:
    for line in f:
        marker_info.append(line)

with open(current_dir / "start_region_info.txt", "w") as f:
    for _ in range(3):
        f.write("0\n")
    for i in range(6):
        f.write(marker_info[i])

