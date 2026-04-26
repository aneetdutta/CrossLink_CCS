import os, sys, time
sys.path.append(os.getcwd())
import pandas as pd
import numpy as np
from collections import defaultdict, deque
from tqdm import tqdm
from tracing_algorithm.mapping_functions import (
    check_compatibility_vectorized,
    compute_localization_error,
    intervals_overlap_inter,
    check_compatibility_parallel
)
from modules.general import to_regular_dict
import gc

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAX_MOBILITY_FACTOR = float(os.getenv('MAX_MOBILITY_FACTOR'))

# Read the CSV file
df = pd.read_csv(f'data/{SCENARIO_NAME}/user_data_{SCENARIO_NAME}.csv')
df['timestep'] = pd.to_numeric(df['timestep'], errors='coerce')
id_info = (df.groupby('id').agg(min=('timestep','min'), max=('timestep','max'), protocol=('protocol','first')).reset_index())
id_info['protocol'] = id_info['protocol'].astype('category')
df['protocol'] = df['protocol'].astype('category')
########################################

print("Precomputing")
id_info = id_info.sort_values('min').reset_index(drop=True)

bluetooth_df = id_info[id_info['protocol'] == 'Bluetooth']
lte_df = id_info[id_info['protocol'] == 'LTE']
wifi_df = id_info[id_info['protocol'] == 'WiFi']

# Convert each subset into a dictionary
comparison_list = {
    "Bluetooth" : bluetooth_df.to_dict('records'),
    "LTE": lte_df.to_dict('records'),
    "WiFi": wifi_df.to_dict('records'),
}

# Precompute protocol errors once
protocol_errors = compute_localization_error(df['protocol'])
grouped_dict = {id_val: group[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']] for id_val, group in df.groupby('id')}

del id_info, bluetooth_df, lte_df, wifi_df

gc.collect()
comparisons = [("LTE", "Bluetooth"), ("LTE", "WiFi"), ("Bluetooth", "WiFi")]
# comparisons = [("LTE", "WiFi"), ("Bluetooth", "WiFi")]
# comparisons = [("Bluetooth", "WiFi")]
# Checking between 2 protocols (Advantage over previous - We do not traverse into ids of same protocol)

print("Starting intermapping")

def tqdm_generator(generator, total=None):
    for item in tqdm(generator, total=total):
        yield item
        
def generate_pairs(c1, c2):
    for id_a in c1:
        for id_b in c2:
            if intervals_overlap_inter(id_a['min'], id_a['max'], id_b['min'], id_b['max']):
                yield (id_a['id'], id_b['id'])


for p1, p2 in comparisons:
    intermap = defaultdict(lambda: defaultdict(set))
    # visited_intermap = defaultdict(set)
    print(p1, p2)
    now = time.time()
    # for id_a in comparison_list[p1]:
    #     for id_b in comparison_list[p2]:
    #         if intervals_overlap_inter(id_a['min'], id_a['max'], id_b['min'], id_b['max']):
    #             pairs.append((id_a['id'], id_b['id']))
    pairs = generate_pairs(comparison_list[p1], comparison_list[p2])
    count = sum(1 for i in pairs)
    print("Generating pairs again as generator counted")
    pairs = generate_pairs(comparison_list[p1], comparison_list[p2])
    print(f"Completed computing overlapping pairs for ({p1}, {p2}) in {time.time() - now}")
    print(f"Computing intermap and visited intermap for ({p1}, {p2})")
    gc.collect()
    
    print(count)
    
    for id1, id2 in tqdm(pairs, total=count):
        if id1 not in grouped_dict or id2 not in grouped_dict:
            continue
        
        subset1 = grouped_dict[id1]
        subset2 = grouped_dict[id2]
        if subset1.empty or subset2.empty:
            continue
        compatible = check_compatibility_vectorized(subset1, subset2, protocol_errors)
        #compatible= check_compatibility_parallel(subset1, subset2, protocol_errors)
        if compatible:
            proto_id2 = subset2['protocol'].iloc[0]
            if not isinstance(proto_id2, str):
                proto_id2 = subset2['protocol'].cat.categories[proto_id2]
            intermap[id1][proto_id2].update(set(subset2['id'].unique()))

            proto_id1 = subset1['protocol'].iloc[0]
            if not isinstance(proto_id1, str):
                proto_id1 = subset2['protocol'].cat.categories[proto_id1]
            intermap[id2][proto_id1].update(set(subset1['id'].unique()))
        # else:
        #     visited_intermap[id1].add(id2)
        #     visited_intermap[id2].add(id1)
        # gc.collect()

    intermap_dict = to_regular_dict(intermap)
    # visited_intermap_dict = to_regular_dict(visited_intermap)
    np.save(f'data/{SCENARIO_NAME}/intermap_{p1}_{p2}.npy', intermap_dict, allow_pickle=True)
    # np.save(f'data/{SCENARIO_NAME}/visited_intermap_{p1}_{p2}.npy', visited_intermap_dict, allow_pickle=True)
    print(f"Saved intermap for {p1} and {p2}")
    gc.collect()

print("intermap saved successfully.")
