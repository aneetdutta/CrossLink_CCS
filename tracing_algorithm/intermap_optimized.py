import os, sys
sys.path.append(os.getcwd())

import pandas as pd
from itertools import combinations
from collections import defaultdict
import numpy as np
import math
from collections import defaultdict, deque
from tqdm import tqdm
from multiprocessing import Pool, Manager
import multiprocessing as mp
import time

from modules.general import to_regular_dict

import polars as pl

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAX_MOBILITY_FACTOR = float(os.getenv('MAX_MOBILITY_FACTOR'))
MAX_TRANSMIT_TIME=60


def intervals_overlap(min1, max1, min2, max2):
    return not (max1+MAX_TRANSMIT_TIME < min2 or max2+MAX_TRANSMIT_TIME < min1)



# Read the CSV file
df = pd.read_csv(f'data/{SCENARIO_NAME}/sniffed_data_{SCENARIO_NAME}.csv')

df['timestep'] = pd.to_numeric(df['timestep'], errors='coerce')

# Group by 'id' to find min and max timestep and extract the protocol
id_info = (df.groupby('id')
             .agg(min=('timestep','min'), 
                  max=('timestep','max'),
                  protocol=('protocol','first'))
             .reset_index())

# id_info.to_csv('id_info.csv', index=False)

# Convert protocol to category for faster operations
id_info['protocol'] = id_info['protocol'].astype('category')
df['protocol'] = df['protocol'].astype('category')


print("1")

########################################

overlapping_pairs = deque()
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

# time.sleep(10)
# id_list = id_info.to_dict('records')
# sys.exit()

del id_info, bluetooth_df, lte_df, wifi_df

# for p1, p2 in comparision:
#     print(p1, p2)
#     for id_a in comparison_list[p1]:
#         for id_b in comparison_list[p2]:
#             # if ( (id_a['id'], id_b['id']) not in overlapping_pairs):
#             if intervals_overlap(id_a['min'], id_a['max'], id_b['min'], id_b['max']):
#                 overlapping_pairs.append((id_a['id'], id_b['id']))

import time

a = time.time()

manager = Manager()
overlapping_pairs = manager.list()

comparisons = [("LTE", "Bluetooth"), ("LTE", "WiFi"), ("Bluetooth", "WiFi")]
# Checking between 2 protocols (Advantage over previous - We do not traverse into ids of same protocol)

def process_pair_yield(p1, p2, max_transmit_time):
    for id_a in comparison_list[p1]:
        for id_b in comparison_list[p2]:
            if not (id_a['max'] + max_transmit_time < id_b['min'] or 
                    id_b['max'] + max_transmit_time < id_a['min']):
                yield (id_a['id'], id_b['id'])

# Function for multiprocessing wrapper
def process_pair_wrapper(args):
    p1, p2, max_transmit_time = args
    print(p1, p2)
    l = time.time()
    g = list(process_pair_yield(p1, p2, max_transmit_time))
    print(p1, p2, time.time() - l)
    return g

# Prepare arguments for multiprocessing
args = [(p1, p2, MAX_TRANSMIT_TIME) for p1, p2 in comparisons]

# Start multiprocessing with optimized memory usage
with Pool(processes=len(comparisons)) as pool:
    # Use an iterator to minimize memory usage
    results = pool.imap_unordered(process_pair_wrapper, args)
    
    for result in results:
        overlapping_pairs.extend(result)
        
del results


# # =========================================================
# # Step 3: Vectorized Compatibility Check
# # =========================================================

def compute_localization_error(protocols):
    # protocols is a Categorical series
    unique_cats = protocols.cat.categories
    errors = np.zeros(len(unique_cats), dtype=np.int8)
    # Assign errors by category
    for i, cat in enumerate(unique_cats):
        if cat == 'Bluetooth':
            errors[i] = 1
        elif cat == 'WiFi':
            errors[i] = 5
        else:
            errors[i] = 10
    return errors

def check_compatibility_vectorized(subset1, subset2, protocol_errors):
   
    arr1_x = subset1['sl_x'].values
    arr1_y = subset1['sl_y'].values
    arr1_t = subset1['timestep'].values
    arr1_d = subset1['dist_S_U'].values
    arr1_p = subset1['protocol'].cat.codes.values
    arr1_sniffer = subset1['sniffer_id'].values

    # --- 2) Extract arrays from subset2
    arr2_x = subset2['sl_x'].values
    arr2_y = subset2['sl_y'].values
    arr2_t = subset2['timestep'].values
    arr2_d = subset2['dist_S_U'].values
    arr2_p = subset2['protocol'].cat.codes.values
    arr2_sniffer = subset2['sniffer_id'].values
    
    r1 = arr1_d + protocol_errors[arr1_p]
    r2 = arr2_d + protocol_errors[arr2_p]

    dx = arr1_x[:, None] - arr2_x[None, :]
    dy = arr1_y[:, None] - arr2_y[None, :]
    d_xy = np.sqrt(dx**2 + dy**2)

    R = r1[:, None] + r2[None, :]
    min_distance = d_xy - R
    min_distance[min_distance < 0] = 0
    
    delta_t = np.abs(arr1_t[:, None] - arr2_t[None, :])
    compatible_matrix = (min_distance <= (delta_t * MAX_MOBILITY_FACTOR))

    # --- 8) Return True only if *all* pairs pass
    return compatible_matrix.all() 



# Precompute protocol errors once
protocol_errors = compute_localization_error(df['protocol'])

# =========================================================
# Step 4: Check Compatibility for Each Overlapping Pair
#
# For each (id1, id2) pair, get all rows and check compatibility in a vectorized manner.
# =========================================================

intermap = defaultdict(lambda: defaultdict(set))
visited_intermap = defaultdict(set)
grouped_dict = {id_val: group[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']] for id_val, group in df.groupby('id')}

a = time.time()
for id1, id2 in tqdm(overlapping_pairs, total=len(overlapping_pairs)):
    if id1 not in grouped_dict or id2 not in grouped_dict:
        continue
    
    subset1 = grouped_dict[id1]
    subset2 = grouped_dict[id2]

    if subset1.empty or subset2.empty:
        continue

    compatible = check_compatibility_vectorized(subset1, subset2, protocol_errors)
    
    if compatible:
        # Mapping id1 with id2
        # Get the protocol name of id2
        proto_id2 = subset2['protocol'].iloc[0]
        # If proto_id2 is a code, convert back; if already a category str, just use it
        if not isinstance(proto_id2, str):
            proto_id2 = subset2['protocol'].cat.categories[proto_id2]
        intermap[id1][proto_id2].update(set(subset2['id'].unique()))

        # Mapping id2 with id1 (vice-versa)
        # Get the protocol name of id1
        proto_id1 = subset1['protocol'].iloc[0]
        # If proto_id2 is a code, convert back; if already a category str, just use it
        if not isinstance(proto_id1, str):
            proto_id1 = subset2['protocol'].cat.categories[proto_id1]
        intermap[id2][proto_id1].update(set(subset1['id'].unique()))
    else:
        visited_intermap[id1].add(id2)
        visited_intermap[id2].add(id1)


print(time.time() - a)
intermap_dict = to_regular_dict(intermap)
visited_intermap_dict = to_regular_dict(visited_intermap)

# print(intermap_dict)

np.save(f'data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.npy', intermap_dict, allow_pickle=True)
np.save(f'data/{SCENARIO_NAME}/visited_intermap_{SCENARIO_NAME}.npy', visited_intermap_dict, allow_pickle=True)

print("intermap and visited_intermap saved successfully.")