import os, sys
sys.path.append(os.getcwd())
import numpy as np
from scipy.spatial import KDTree
from collections import defaultdict
from multiprocessing import Pool, cpu_count
from joblib import Parallel, delayed
SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAX_MOBILITY_FACTOR = float(os.getenv('MAX_MOBILITY_FACTOR'))

BLUETOOTH_LOCALIZATION_ERROR = int(os.getenv('BLUETOOTH_LOCALIZATION_ERROR'))
WIFI_LOCALIZATION_ERROR = int(os.getenv('WIFI_LOCALIZATION_ERROR'))
LTE_LOCALIZATION_ERROR = int(os.getenv('LTE_LOCALIZATION_ERROR'))

MAX_TRANSMIT_TIME=int(os.getenv('MAX_TRANSMIT_TIME', 60))
MAX_TRANSMIT_TIME=60
def compute_localization_error(protocols):
    # protocols is a Categorical series
    unique_cats = protocols.cat.categories
    errors = np.zeros(len(unique_cats), dtype=np.int8)
    # Assign errors by category
    for i, cat in enumerate(unique_cats):
        if cat == 'Bluetooth':
            errors[i] = BLUETOOTH_LOCALIZATION_ERROR
        elif cat == 'WiFi':
            errors[i] = WIFI_LOCALIZATION_ERROR
        else:
            errors[i] = LTE_LOCALIZATION_ERROR
    return errors

def check_compatibility_grid(subset1, subset2, protocol_errors,GRID_SIZE=50):
    grid = defaultdict(list)

    arr2_x = subset2['sl_x'].values
    arr2_y = subset2['sl_y'].values
    arr2_t = subset2['timestep'].values
    arr2_d = subset2['dist_S_U'].values
    arr2_p = subset2['protocol'].cat.codes.values
    arr2_r = arr2_d + protocol_errors[arr2_p]

    # Populate the spatial grid with subset2
    for x, y, t, r in zip(arr2_x, arr2_y, arr2_t, arr2_r):
        cell = (int(x // GRID_SIZE), int(y // GRID_SIZE))
        grid[cell].append((x, y, t, r))

    arr1_x = subset1['sl_x'].values
    arr1_y = subset1['sl_y'].values
    arr1_t = subset1['timestep'].values
    arr1_d = subset1['dist_S_U'].values
    arr1_p = subset1['protocol'].cat.codes.values
    arr1_r = arr1_d + protocol_errors[arr1_p]

    for x1, y1, t1, r1 in zip(arr1_x, arr1_y, arr1_t, arr1_r):
        cell_x, cell_y = int(x1 // GRID_SIZE), int(y1 // GRID_SIZE)

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                neighbors = grid.get((cell_x + dx, cell_y + dy), [])

                for x2, y2, t2, r2 in neighbors:
                    delta_t = abs(t1 - t2)
                    d_xy = np.hypot(x1 - x2, y1 - y2)
                    min_distance = max(d_xy - (r1 + r2), 0)

                    if min_distance > (delta_t * MAX_MOBILITY_FACTOR):
                        return False  # Early exit on incompatibility

    return True


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

    return compatible_matrix.all() 

def compatibility_worker(arr1_x, arr1_y, arr1_t, arr1_d, arr1_p, arr2_x, arr2_y, arr2_t, arr2_d, arr2_p, protocol_errors):
    r1 = arr1_d + protocol_errors[arr1_p]
    r2 = arr2_d + protocol_errors[arr2_p]

    dx = arr1_x[:, None] - arr2_x[None, :]
    dy = arr1_y[:, None] - arr2_y[None, :]
    d_xy = np.sqrt(dx**2 + dy**2)

    R = r1[:, None] + r2[None, :]
    min_distance = np.maximum(d_xy - R, 0)

    delta_t = np.abs(arr1_t[:, None] - arr2_t[None, :])
    compatible_matrix = (min_distance <= (delta_t * MAX_MOBILITY_FACTOR))

    return compatible_matrix.all()

def check_compatibility_parallel(subset1, subset2, protocol_errors):
    num_chunks = 8  # Tune as per CPU
    chunk_size = len(subset1) // num_chunks + 1

    results = Parallel(n_jobs=num_chunks)(
        delayed(compatibility_worker)(
            subset1['sl_x'].values[i:i+chunk_size],
            subset1['sl_y'].values[i:i+chunk_size],
            subset1['timestep'].values[i:i+chunk_size],
            subset1['dist_S_U'].values[i:i+chunk_size],
            subset1['protocol'].cat.codes.values[i:i+chunk_size],
            subset2['sl_x'].values,
            subset2['sl_y'].values,
            subset2['timestep'].values,
            subset2['dist_S_U'].values,
            subset2['protocol'].cat.codes.values,
            protocol_errors)
        for i in range(0, len(subset1), chunk_size))

    return all(results)

def check_compatibility_vectorized_ids(id1, id2, subset1, subset2, protocol_errors):
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
    # if id2 == "P_1-1-pt_1238_B_PMI7T2WI" and id1 == "P_1-1-pt_1226_B_PRMKCCP7":
    #     print(id1, id2, compatible_matrix.all(), (min_distance <= (delta_t * MAX_MOBILITY_FACTOR)))
    #     print(arr1_d, protocol_errors[arr1_p], arr2_d, protocol_errors[arr2_p])
    #     print(R)
    return compatible_matrix.all() 


# Function to check interval overlap
def intervals_overlap_intra(max1, min2):
    if max1 < min2:
        if (min2 - max1) <= MAX_TRANSMIT_TIME:
            return True
        # ((min2-max1)<=60)
    else:
        return False
    
def intervals_overlap_inter(min1, max1, min2, max2):
    return not (max1+MAX_TRANSMIT_TIME < min2 or max2+MAX_TRANSMIT_TIME < min1)
