import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import polars as pl
import numpy as np
import pandas as pd
from tqdm import tqdm
from multiprocessing import Pool
from collections import defaultdict

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAX_MOBILITY_FACTOR = float(os.getenv('MAX_MOBILITY_FACTOR'))

df = pd.read_csv(f'data/{SCENARIO_NAME}/sniffed_data_{SCENARIO_NAME}.csv')

df['timestep'] = pd.to_numeric(df['timestep'], errors='coerce')

# Group by 'id' to find min and max timestep and extract the protocol
id_info = (df.groupby('id')
             .agg(min=('timestep','min'), 
                  max=('timestep','max'),
                  protocol=('protocol','first'))
             .reset_index())

# id_info.to_csv('id_info.csv', index=False)
MAX_TRANSMIT_TIME=60
# Convert protocol to category for faster operations
id_info['protocol'] = id_info['protocol'].astype('category')
df['protocol'] = df['protocol'].astype('category')

# Function to check interval overlap
def intervals_overlap(max1, min2):
    if max1<min2:
        if (min2-max1)<=MAX_TRANSMIT_TIME:
            return True 
        #((min2-max1)<=60)
    else:
        return False

# Find overlapping ids from different protocols
intramapping_pairs = []
id_list = id_info.to_dict('records')

protocols = df.groupby('id')['protocol'].apply(lambda x: x.iloc[0]).reset_index()
for i in range(len(id_list)):
    id_a = id_list[i]
    for j in range(len(id_list)):
        
        id_b = id_list[j]
        
        # Check if protocols differ
        if id_a['protocol'] == id_b['protocol']:
            # Check time overlap
            if intervals_overlap(id_a['max'], id_b['min']):
                #print(id_a['max'])
                #print(id_b['min'])
                intramapping_pairs.append((id_a['id'], id_b['id']))

# Print or store the result
print("Intramapping ids with same protocol:")


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
    d = np.sqrt(dx*dx + dy*dy)

    R = r1[:, None] + r2[None, :]
    
    
    
   
    
    
    
    min_distance = d - R
   
   
    min_distance[min_distance < 0] = 0
    
    
    delta_t = np.abs(arr1_t[:, None] - arr2_t[None, :])
    
    compatible_matrix = (
    (min_distance <= (delta_t * MAX_MOBILITY_FACTOR)) 
)
    
    return compatible_matrix.all()


intramap=dict() 
df['protocol'] = df['protocol'].astype('category')
protocol_errors = compute_localization_error(df['protocol'])
grouped = df.groupby('id')
for id1, id2 in tqdm(intramapping_pairs, total=len(intramapping_pairs)):
    if id1=='pedestrian_1-1-pt_1296_CV4XS':
        print(id2)
    subset1 = grouped.get_group(id1)[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']]
    #protocol1=subset1['protocol'].values
    #protocol1=protocol1[0]

    subset2 = grouped.get_group(id2)[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']]
    protocol2=subset2['protocol'].values
    protocol2=protocol2[0]

    compatible = check_compatibility_vectorized(subset1, subset2,protocol_errors)

   
    if compatible:
        if id1 not in intramap.keys():
            intramap[id1]=[id2]
        else:
            intramap[id1].append(id2)
        if id1=='pedestrian_1-1-pt_255_CD9P2':
            print(intramap[id1])
            
   # if protocol2=='Bluetooth':
    #    print(intramap)       
    

# print(intramap)

# def process_batch(batch):
#     local_map = {}
#     for id1, id2, id1_max, id2_min in batch:

#         subset1 = grouped.get_group(id1)[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']]
#         protocol1 = subset1['protocol'].values
#         protocol1=protocol1[0]

#         subset2 = grouped.get_group(id2)[['timestep', 'id', 'sniffer_id', 'sl_x', 'sl_y', 'dist_S_U', 'protocol']]
#         protocol2 = subset2['protocol'].values
#         protocol2=protocol2[0]

#         compatible = check_compatibility_vectorized(subset1, subset2, protocol1, protocol2)

#         # if id1 == "P0_0EHCH" and id2 == "P12_JC4UR":
#         #     print("ninja rocks", compatible)
            
#         if compatible:
#             if id1 not in local_map:
#                 local_map[id1] = [id2]
#             else:
#                 local_map[id1].append(id2)
#     return local_map

# def merge_dicts(dicts):
#     """Merge a list of dictionaries, ensuring no data is lost."""
#     result = defaultdict(list)
#     for d in dicts:
#         for key, value in d.items():
#             result[key].extend(value)
#     return dict(result)

# def batchify(data, batch_size):
#     """Divide data into batches of size `batch_size`."""
#     for i in range(0, len(data), batch_size):
#         print(len(data))
#         print(i)
#         yield data[i:i + batch_size]


# BATCH_SIZE = 128  # Adjust batch size based on your workload
# batches = list(batchify(intramapping_pairs, BATCH_SIZE))

# with Pool() as pool:
#     results = list(tqdm(pool.imap(process_batch, batches), total=len(batches)))

# # Merge results from all processes
# intramap = merge_dicts(results)
# intramap = dict(sorted(intramap.items()))
# print(intramap)
np.save(f'data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.npy', intramap, allow_pickle=True)
np.save(f'data/{SCENARIO_NAME}/intramap_single_{SCENARIO_NAME}.npy', intramap, allow_pickle=True)
