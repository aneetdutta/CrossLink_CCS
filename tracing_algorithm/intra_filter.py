import os, sys
sys.path.append(os.getcwd())
from modules.general import *
# from collections import defaultdict
''' Load the sumo_simulation result from mongodb '''
import pandas as pd
import polars as pl
from modules.logger import MyLogger
# remove_subsets_from_dict

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
# ml = MyLogger(f"reconstruction_baseline_{SCENARIO_NAME}")
ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))
ENABLE_PARTIAL_COVERAGE = str_to_bool(os.getenv("ENABLE_PARTIAL_COVERAGE", "False"))


ml = MyLogger(f"intra_filter_{SCENARIO_NAME}")

intra_data = np.load(f'data/{SCENARIO_NAME}/refined_intramap_{SCENARIO_NAME}.npy', allow_pickle=True).item()

# # Filter 1
#print(intra_data["pedestrian_1-1-pt_8545_1AT82"], "a")
#intra_data = remove_subsets_from_dict(intra_data)
#print(intra_data["pedestrian_1-1-pt_8545_1AT82"], "b")

# Filter 2
if not ENABLE_PARTIAL_COVERAGE:
    intra_data = clean_mappings(intra_data)
#intra_data = remove_subsets_from_dict(intra_data)
#print(intra_data["pedestrian_1-1-pt_8545_1AT82"], "c")

np.save(f'data/{SCENARIO_NAME}/filtered_intramap_{SCENARIO_NAME}.npy', intra_data, allow_pickle=True)
print(intra_data)

intra_data = np.load(f'data/{SCENARIO_NAME}/intramap_single_{SCENARIO_NAME}.npy', allow_pickle=True).item()

# # Filter 1
#intra_data = remove_subsets_from_dict(intra_data)
# Filter 2
if not ENABLE_PARTIAL_COVERAGE:
    intra_data = clean_mappings(intra_data)
    
for key in intra_data.keys():
    if "_W_" not in key:
        print(key)
        print(intra_data[key])

np.save(f'data/{SCENARIO_NAME}/filtered_intramap_single_{SCENARIO_NAME}.npy', intra_data, allow_pickle=True)
