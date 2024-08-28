import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import math
import re
import shutil
from sklearn.cluster import KMeans
import random
from scipy.spatial import distance
from sklearn.metrics import pairwise_distances

def get_bbv_info(bbv_file, num_threads):
    all_info = {}
    with open(bbv_file, "r") as f:
        line = f.readline()
        while line:
            if "Region:" in line:
                region = int(line.split()[1])
                line = f.readline()
                line = f.readline()
                regional_ir_inst = int(line.split()[5])
                regional_bbv = None
                for _ in range(num_threads):
                    line = f.readline()
                    bbv_list = line.split()[5]
                    bbv_list = bbv_list[1:-2].split(",")
                    bbv_list = [int(x.split(":")[0]) for x in bbv_list]
                    if regional_bbv is None:
                        regional_bbv = bbv_list
                    else:
                        regional_bbv = [x + y for x, y in zip(regional_bbv, bbv_list)]
                all_info[region] = {
                    "ir_inst": regional_ir_inst,
                    "bbv": regional_bbv
                }
            line = f.readline()
    return all_info

def get_static_info(path):
    info = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                function_match = re.match(r'\[(\d+):([^\]]+)\]', line)
                if function_match:
                    function_id, function_name = function_match.groups()
                    basic_blocks = re.findall(r'\[(\d+):([^\]]*):(\d+)\]', line)
                    for basic_block in basic_blocks:
                        basic_block_id, basic_block_name, basic_block_ir_inst_count = basic_block
                        info[int(basic_block_id)] = {
                            "basic_block_name": basic_block_name,
                            "basic_block_ir_inst_count": int(basic_block_ir_inst_count),
                            "function_name": function_name,
                            "function_id": int(function_id)
                        }
    return info

def form_bbv(static_info, bbv_info):
    all_bbv = []
    for _, rdata in bbv_info.items():
        regional_ir = rdata["ir_inst"]
        raw_bbv = rdata["bbv"]
        processed_bbv = []
        for bid, bdata in enumerate(raw_bbv):
            bb_ir_inst = int(static_info[bid]["basic_block_ir_inst_count"])
            weight = float(float(bb_ir_inst) / float(regional_ir))
            processed_bbv.append(float(bdata) * weight)
        all_bbv.append(processed_bbv)

    return all_bbv

def find_rep_rid(data, labels, centers):
    rep_rid = {}
    for i, center in enumerate(centers):
        min = float('inf')
        min_rid = -1
        count = 0
        for j, label in enumerate(labels):
            if label == i:
                count += 1
                dist = distance.euclidean(center, data[j])
                if dist < min:
                    min = dist
                    min_rid = j
        if min_rid != -1:
            rep_rid[i] = min_rid
        else:
            print("Error: No representative RID found for cluster")
            print(f"There are {count} RIDs in cluster {i}")

    return rep_rid
def find_cluster_rid(labels):
    clusters = {}
    for i, label in enumerate(labels):
        if str(label) not in clusters.keys():
            clusters[str(label)] = []
        clusters[str(label)].append(i)
    return clusters

def clustering(data, k, min_k=10):
    all_clusters = {}
    for i in range(min_k, k+1, 10):
        kmeans = KMeans(n_clusters=i, random_state=random_seed)
        kmeans.fit(data)

        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        inertia = kmeans.inertia_
        n_iter = kmeans.n_iter_
        print(i)
        rep_rid = find_rep_rid(data, labels.tolist(), centers.tolist())
        clusters = find_cluster_rid(labels.tolist())
        all_clusters[i] = {
            "centers": centers.tolist(),
            "labels": labels.tolist(),
            "inertia": inertia,
            "n_iter": n_iter,
            "rep_rid": rep_rid,
            "clusters": clusters
        }

    return all_clusters

random_seed = 627
np.random.seed(random_seed)
random.seed(random_seed)

workdir = Path().cwd()
benchmarks = ["bt", "cg", "ep", "ft", "is", "lu", "mg", "sp"]
# benchmarks = ["is"]

num_k = 30
min_k = 30
region_length = 1000_000_000
num_threads = 8
target_run_num = 0
size = "C"
arch = "aarch64"

all_clusters = {}
for bench in benchmarks:
    print(f"Processing {bench}")
    bench_dir = Path(workdir/f"{bench.upper()}/{size}/c_profiling/{region_length}")
    raw_bbv_info = get_bbv_info(Path(bench_dir/f"{arch}/run_{num_threads}_{target_run_num}/all_output_{num_threads}_threads.txt"), 8)
    static_info_file = None
    for f in bench_dir.glob("basic_block_info_output_*.txt"):
        static_info_file = Path(bench_dir/f.name)
    if static_info_file is None:
        print(f"Error: No static info file found for {bench}")
        print(Path(bench_dir).as_posix())
        continue
    static_info = get_static_info(static_info_file)
    print(f"Found {len(static_info)} basic blocks")
    bbv = form_bbv(static_info, raw_bbv_info)
    print(f"Found {len(bbv)} regions")
    bbv = np.array(bbv)
    distance_matrix = pairwise_distances(bbv, metric='euclidean')
    print(f"Distance matrix shape: {distance_matrix.shape}")
    all_clusters[bench] = clustering(bbv, num_k, min_k=min_k)

with open(workdir/"all_clusters.json", "w") as f:
    json.dump(all_clusters, f, indent=4)



