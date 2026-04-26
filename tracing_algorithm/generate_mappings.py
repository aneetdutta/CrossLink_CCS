import os, sys
sys.path.append(os.getcwd())
from modules.general import *
import numpy as np
import copy
from modules.general import merge_nested_dicts

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAPPING_SOURCE = os.getenv("MAPPING_SOURCE")

ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))

''' This code combines the inter and intra mappings of each protocols to give final set of mappings '''

# Step 1: Combine Intra mappings

intramap = {}
map_len = 0
if ENABLE_BLUETOOTH:
    map = np.load(f"data/{MAPPING_SOURCE}/intramap_Bluetooth.npy", allow_pickle=True).item()
    map_len += len(map)
    intramap = intramap | map
if ENABLE_LTE:
    map = np.load(f"data/{MAPPING_SOURCE}/intramap_LTE.npy", allow_pickle=True).item()
    map_len += len(map)
    intramap = intramap | map
#if ENABLE_WIFI:
 #   map = np.load(f"data/{MAPPING_SOURCE}/intramap_WiFi.npy", allow_pickle=True).item()
 #   map_len += len(map)
 #   intramap = intramap | map

print(len(intramap) == map_len)

np.save(f'data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.npy', intramap, allow_pickle=True)
np.save(f'data/{SCENARIO_NAME}/intramap_single_{SCENARIO_NAME}.npy', intramap, allow_pickle=True)

print("Saved Intramap and intramap single")

intermap = defaultdict(lambda: defaultdict(set))

if ENABLE_BLUETOOTH and ENABLE_LTE:
    print("LTE - BLE")
    map = np.load(f"data/{MAPPING_SOURCE}/intermap_LTE_Bluetooth.npy", allow_pickle=True).item()
    intermap = merge_nested_dicts(intermap, map)
    
if ENABLE_BLUETOOTH and ENABLE_WIFI:
    print("BLE - WiFi")
    map = np.load(f"data/{MAPPING_SOURCE}/intermap_Bluetooth_WiFi.npy", allow_pickle=True).item()
    intermap = merge_nested_dicts(intermap, map)
    
if ENABLE_LTE and ENABLE_WIFI:
    print("LTE - WiFi")
    map = np.load(f"data/{MAPPING_SOURCE}/intermap_LTE_WiFi.npy", allow_pickle=True).item()
    intermap = merge_nested_dicts(intermap, map)

intermap_dict = to_regular_dict(intermap)

# print(intermap_dict)
np.save(f'data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.npy', intermap_dict, allow_pickle=True)

print("Saved Intermap")
