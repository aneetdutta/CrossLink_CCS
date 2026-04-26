import os, sys
sys.path.append(os.getcwd())

import pandas as pd
from itertools import combinations
from collections import defaultdict
import numpy as np
import math
from collections import defaultdict
from tqdm import tqdm

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAX_MOBILITY_FACTOR = float(os.getenv('MAX_MOBILITY_FACTOR'))

MAX_TRANSMIT_TIME=60
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

# =========================================================
# Step 2: Finding Overlapping IDs from Different Protocols Efficiently
#
# Condition for overlap: not (max1+60 < min2 or max2+60 < min1)
# We'll do interval comparisons between different protocol groups.
# =========================================================

# Separate IDs by protocol
def intervals_overlap(min1, max1, min2, max2):
    return not (max1+MAX_TRANSMIT_TIME < min2 or max2+MAX_TRANSMIT_TIME < min1)

# Find overlapping ids from different protocols
overlapping_pairs = []
id_list = id_info.to_dict('records')

for i in range(len(id_list)):
    id_a = id_list[i]
    for j in range(len(id_list)):
        
        id_b = id_list[j]
        #print(id_a)
        #print(id_b)
        
        # Check if protocols differ
        if id_a['protocol'] != id_b['protocol']:
            # Check time overlap
            if intervals_overlap(id_a['min'], id_a['max'], id_b['min'], id_b['max']):
                overlapping_pairs.append((id_a['id'], id_b['id']))

overlap_df = pd.DataFrame(overlapping_pairs, columns=['id1', 'id2'])
# overlap_df.to_csv('overlapping_ids.csv', index=False)

# =========================================================
# Step 3: Vectorized Compatibility Check
# =========================================================

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

grouped = df.groupby('id')

for _, row in tqdm(overlap_df.iterrows(), total=overlap_df.shape[0]):
    id1 = row['id1']
    id2 = row['id2']

    if id1 not in grouped.groups or id2 not in grouped.groups:
        continue

    subset1 = grouped.get_group(id1)[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']]
    subset2 = grouped.get_group(id2)[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']]
    #sniffer1=subset1[['sniffer_id']] where timestep 
    #sniffer2=subset2[['sniffer_id']]
    
    
    
    if subset1.empty or subset2.empty:
        continue

    compatible = check_compatibility_vectorized(subset1, subset2, protocol_errors)
    if compatible:
        # Get the protocol name of id2
        proto_id2 = subset2['protocol'].iloc[0]
        # If proto_id2 is a code, convert back; if already a category str, just use it
        if not isinstance(proto_id2, str):
            proto_id2 = subset2['protocol'].cat.categories[proto_id2]
        intermap[id1][proto_id2].update(set(subset2['id'].unique()))
        #print(intermap)
    else:
        visited_intermap[id1].add(id2)

def to_regular_dict(d):
    if isinstance(d, defaultdict):
        return {k: to_regular_dict(v) for k, v in d.items()}
    elif isinstance(d, set):
        return d
    return d

intermap_dict = to_regular_dict(intermap)
visited_intermap_dict = to_regular_dict(visited_intermap)

print(intermap_dict)

np.save(f'data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.npy', intermap_dict, allow_pickle=True)
np.save(f'data/{SCENARIO_NAME}/visited_intermap_{SCENARIO_NAME}.npy', visited_intermap_dict, allow_pickle=True)

print("intermap and visited_intermap saved successfully.")
