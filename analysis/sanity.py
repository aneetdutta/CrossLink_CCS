import os, sys
sys.path.append(os.getcwd())

import polars as pl
import numpy as np
from collections import defaultdict
import os.path
from modules.general import str_to_bool


SCENARIO_NAME = os.getenv("SCENARIO_NAME")

PARQUET_FILE_PATH = f"data/{SCENARIO_NAME}/aggregated_id_{SCENARIO_NAME}.parquet"
df = pl.read_parquet(PARQUET_FILE_PATH)
id_protocol_dict = {row["id"]: row["protocol"] for row in df.to_dicts()}
protocol_counts = df.group_by("protocol").agg(pl.count("id").alias("count")).to_dicts()
protocol_counts = {entry["protocol"]: entry["count"] for entry in protocol_counts}
total_count = sum(protocol_counts.values())



MAPPING_SOURCE = os.getenv("MAPPING_SOURCE")
ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))

def printer(mapper, st):
    print("\n" + "="*40)
    print(f"✨ Analysing individual mappings - {st} ✨")
    print("="*40)
    null_intra = set()
    null_intra_protocol = defaultdict(list)
    null_intra_dict = defaultdict(list)
    incorrectness = set()
    # if 'pedestrian_1-2_2875_W_PBH0C' in mapper:
    #     print(mapper['pedestrian_1-2_2875_W_PBH0C'])
    for i, item in mapper.items():
        user_id = '_'.join(i.split("_")[0:-2])
        if not item:
            null_intra.add(i)
            null_intra_protocol[id_protocol_dict[i]].append(i)
            null_intra_dict[user_id].append(i)
            continue
        
        matched_strings = list(filter(lambda s: user_id in s, item))
        if not matched_strings:
            incorrectness.add(i)    
    # print(incorrectness)        
    null_intra_protocol_len = {key: len(values) for key, values in null_intra_protocol.items()}

    # Please note: last timestep of the user id are not added to intra_data, so these are actual null intra mappings
    print(f"\n")
    print(f"Correctness in Intra mappings (contains atleast one correct mapping): {len(mapper) - len(incorrectness)} of {len(mapper)}")
    print(incorrectness)
    print(f"Total Null Intra mappings: {len(null_intra)} of {len(mapper)} mappings")
    print(f"{null_intra_protocol_len}")
    print("\n")
    
if ENABLE_BLUETOOTH and os.path.exists(f"data/{MAPPING_SOURCE}/intramap_Bluetooth.npy"):
    map = np.load(f"data/{MAPPING_SOURCE}/intramap_Bluetooth.npy", allow_pickle=True).item()
    printer(map, "Bluetooth map checking")

if ENABLE_LTE and os.path.exists(f"data/{MAPPING_SOURCE}/intramap_LTE.npy"):
    map = np.load(f"data/{MAPPING_SOURCE}/intramap_LTE.npy", allow_pickle=True).item()
    printer(map, "LTE map checking")

if ENABLE_WIFI and os.path.exists(f"data/{MAPPING_SOURCE}/intramap_WiFi.npy"):
    map = np.load(f"data/{MAPPING_SOURCE}/intramap_WiFi.npy", allow_pickle=True).item()
    printer(map, "WiFi map checking")





'''
INTER AND INTRA
'''

print("\n" + "="*40)
print("✨ Analysing intra and intermap ✨")
print("="*40)

INTRA_NPY_FILE_PATH = f"data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
INTER_NPY_FILE_PATH = f"data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path

if os.path.exists(INTRA_NPY_FILE_PATH) and os.path.exists(INTER_NPY_FILE_PATH):
    intra_data = np.load(INTRA_NPY_FILE_PATH, allow_pickle=True).item()
    inter_data = np.load(INTER_NPY_FILE_PATH, allow_pickle=True).item()


    null_intra = set()
    null_intra_protocol = defaultdict(list)
    null_intra_dict = defaultdict(list)
    incorrectness = set()
    for i, item in intra_data.items():
        user_id = '_'.join(i.split("_")[0:-2])
        if not item:
            null_intra.add(i)
            null_intra_protocol[id_protocol_dict[i]].append(i)
            null_intra_dict[user_id].append(i)
            continue
        
        matched_strings = list(filter(lambda s: user_id in s, item))
        if not matched_strings:
            incorrectness.add(i)    
    # print(incorrectness)        
    null_intra_protocol_len = {key: len(values) for key, values in null_intra_protocol.items()}

    # Please note: last timestep of the user id are not added to intra_data, so these are actual null intra mappings
    print(f"\n")
    print(f"Total Ids: {total_count}")
    print(f"{protocol_counts}")
    print(f"Total Counted Intra Ids: {len(intra_data)} \nTotal Uncounted (ending) Intra Ids: {total_count - len(intra_data)} of {total_count} for all protocols")
    print(f"Correctness in Intra mappings (contains atleast one correct mapping): {total_count - len(incorrectness)} of {total_count}")
    print(f"Total Null Intra mappings: {len(null_intra)} of {len(intra_data)} mappings")
    print(f"{null_intra_protocol_len}")
    print("\n")

    null_inter = set()
    null_inter_protocol = defaultdict(list)
    null_inter_dict = defaultdict(list)
    single_size = 0

    incorrectness = set()
    for i, item in inter_data.items():

        user_id = '_'.join(i.split("_")[0:-2])
        for protocol, k in item.items():
            if not k:
                null_inter.add(i)
                null_inter_protocol[id_protocol_dict[i]].append(i)
                null_inter_dict[user_id].append(i)
                continue
            if len(k) == 1:
                single_size+=1
            matched_strings = list(filter(lambda s: user_id in s, k))
            if not matched_strings:
                incorrectness.add(i)
                
    null_inter_protocol_len = {key: len(values) for key, values in null_inter_protocol.items()}

    print(f"Total Counted Inter Ids: {len(inter_data)} \nTotal Uncounted (ending) Intra Ids: {total_count - len(inter_data)} of {total_count} for all protocols")
    print(f"Correctness in Inter mappings (contains atleast one correct mapping): {total_count - len(incorrectness)} of {total_count}")
    print(f"Intermapping size of 1: {single_size}")
    print(f"Total Null Inter mappings: {len(null_inter)} of {len(inter_data)} mappings")
    print(f"{null_inter_protocol_len}")

    common_null = null_inter.intersection(null_intra)

    print(f"{len(common_null)} common null intra & inter mappings")







'''
REFINED INTER AND INTRA
'''
print("\n" + "="*40)
print("✨ Analysing Refined Intra and Intermap ✨")
print("="*40)


INTRA_NPY_FILE_PATH = f"data/{SCENARIO_NAME}/refined_intramap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
INTER_NPY_FILE_PATH = f"data/{SCENARIO_NAME}/refined_intermap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path

if os.path.exists(INTRA_NPY_FILE_PATH) and os.path.exists(INTER_NPY_FILE_PATH):
    refined_intra_data = np.load(INTRA_NPY_FILE_PATH, allow_pickle=True).item()
    refined_inter_data = np.load(INTER_NPY_FILE_PATH, allow_pickle=True).item()


    refined_null_intra = set()
    refined_null_intra_protocol = defaultdict(list)
    refined_null_intra_dict = defaultdict(list)
    incorrectness = set()
    for i, item in refined_intra_data.items():
        user_id = '_'.join(i.split("_")[0:-2])
        matched_strings = list(filter(lambda s: user_id in s, item))
        if not matched_strings:
            incorrectness.add(i)
        if not item: 
            refined_null_intra.add(i)
            refined_null_intra_protocol[id_protocol_dict[i]].append(i)
            refined_null_intra_dict[user_id].append(i)
            
    refined_null_intra_protocol_len = {key: len(values) for key, values in refined_null_intra_protocol.items()}

    # Please note: last timestep of the user id are not added to intra_data, so these are actual null intra mappings
    print(f"\n")
    print(f"Total Ids: {total_count}")
    print(f"{protocol_counts}")
    print(f"Total Counted Intra Ids: {len(refined_intra_data)} \nTotal Uncounted (ending) Intra Ids: {total_count - len(refined_intra_data)} of {total_count} for all protocols")
    print(f"Correctness in Intra mappings (contains atleast one correct mapping): {total_count - len(incorrectness)} of {total_count}")
    print(f"Total Null Intra mappings: {len(refined_null_intra)} of {len(refined_intra_data)} mappings")
    print(f"{refined_null_intra_protocol_len}")
    print("\n")

    refined_null_inter = set()
    refined_null_inter_protocol = defaultdict(list)
    refined_null_inter_dict = defaultdict(list)
    incorrectness = set()
    for i, item in refined_inter_data.items():
        user_id = '_'.join(i.split("_")[0:-2])
        for j, k in item.items():
            matched_strings = list(filter(lambda s: user_id in s, k))
            if not matched_strings:
                incorrectness.add(i)
            if not k:
                refined_null_inter.add(i)
                refined_null_inter_protocol[id_protocol_dict[i]].append(i)
                refined_null_inter_dict[user_id].append(i)
                
    refined_null_inter_protocol_len = {key: len(values) for key, values in refined_null_inter_protocol.items()}

    print(f"Total Counted Inter Ids: {len(refined_inter_data)} \nTotal Uncounted (ending) Intra Ids: {total_count - len(refined_inter_data)} of {total_count} for all protocols")
    print(f"Correctness in Inter mappings (contains atleast one correct mapping): {total_count - len(incorrectness)} of {total_count}")
    print(f"Total Null Inter mappings: {len(refined_null_inter)} of {len(refined_inter_data)} mappings")
    print(f"{refined_null_inter_protocol_len}")

    common_null = refined_null_inter.intersection(refined_null_intra)

    print(f"{len(common_null)} common null intra & inter mappings")



'''
FILTER INTRA
'''
print("\n" + "="*40)
print("✨ Analysing Filtered Intra and Intermap ✨")
print("="*40)


INTRA_NPY_FILE_PATH = f"data/{SCENARIO_NAME}/filtered_intramap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if INTRA_NPY_FILE_PATH:
    filtered_intra_data = np.load(INTRA_NPY_FILE_PATH, allow_pickle=True).item()

    filtered_null_intra = set()
    filtered_null_intra_protocol = defaultdict(list)
    filtered_null_intra_dict = defaultdict(list)
    incorrectness = set()
    len_single = 0
    for i, item in filtered_intra_data.items():
        user_id = '_'.join(i.split("_")[0:-2])
        matched_strings = list(filter(lambda s: user_id in s, item))
        if len(item) == 1:
            len_single+=1
        if not matched_strings:
            incorrectness.add(i)
        if not item:
            filtered_null_intra.add(i)
            filtered_null_intra_protocol[id_protocol_dict[i]].append(i)
            filtered_null_intra_dict[user_id].append(i)
            
    filtered_null_intra_protocol_len = {key: len(values) for key, values in filtered_null_intra_protocol.items()}

    # Please note: last timestep of the user id are not added to intra_data, so these are actual null intra mappings
    print(f"\n")
    print(f"Total Ids: {total_count}")
    print(f"{protocol_counts}")
    print(f"Total Counted Intra Ids: {len(filtered_intra_data)} \nTotal Uncounted (ending) Intra Ids: {total_count - len(filtered_intra_data)} of {total_count} for all protocols")
    print(f"Correctness in Intra mappings (contains atleast one correct mapping): {total_count - len(incorrectness)} of {total_count}")
    print(f"Total Null Intra mappings: {len(filtered_null_intra)} of {len(filtered_intra_data)} mappings")
    # print(filtered_null_intra)
    print(f"{filtered_null_intra_protocol_len}")
    print(f"Total single mappings: {len_single}")
    print("\n")
    
    
print("Single Protocol")
INTRA_NPY_FILE_PATH = f"data/{SCENARIO_NAME}/filtered_intramap_single_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if INTRA_NPY_FILE_PATH:
    filtered_single_intra_data = np.load(INTRA_NPY_FILE_PATH, allow_pickle=True).item()

    filtered_single_null_intra = set()
    filtered_single_null_intra_protocol = defaultdict(list)
    filtered_single_null_intra_dict = defaultdict(list)
    incorrectness = set()
    for i, item in filtered_single_intra_data.items():
        user_id = '_'.join(i.split("_")[0:-2])
        matched_strings = list(filter(lambda s: user_id in s, item))
        if not matched_strings:
            incorrectness.add(i)
        if not item: 
            filtered_single_null_intra.add(i)
            filtered_single_null_intra_protocol[id_protocol_dict[i]].append(i)
            filtered_single_null_intra_dict[user_id].append(i)
            
    filtered_single_null_intra_protocol_len = {key: len(values) for key, values in filtered_single_null_intra_protocol.items()}

    # Please note: last timestep of the user id are not added to intra_data, so these are actual null intra mappings
    print(f"\n")
    print(f"Total Ids: {total_count}")
    print(f"{protocol_counts}")
    print(f"Total Counted Intra Ids: {len(filtered_single_intra_data)} \nTotal Uncounted (ending) Intra Ids: {total_count - len(filtered_single_intra_data)} of {total_count} for all protocols")
    print(f"Correctness in Intra mappings (contains atleast one correct mapping): {total_count - len(incorrectness)} of {total_count}")
    print(f"Total Null Intra mappings: {len(filtered_single_null_intra)} of {len(filtered_single_intra_data)} mappings")
    # print(filtered_single_null_intra)
    print(f"{filtered_single_null_intra_protocol_len}")
    print("\n")

try:
    '''
    Computing Inter changes
    '''
    print("\n" + "="*40)
    print("✨ Computing changes from Intermap to Refined Intermap ✨")
    print("="*40)

    mappings_changes = set()
    for i, item in inter_data.items():
        user_id = '_'.join(i.split("_")[0:-2])
        for protocol, k in item.items():
            if len(refined_inter_data[i][protocol]) != len(k):
                mappings_changes.add(i)

    print(f"Total Mappings of Id changed from Inter to Refine Inter - {len(mappings_changes)} of {len(inter_data)}")
    #print(f"{mappings_changes}")

    mappings_changes = set()
    for i, item in intra_data.items():
        if len(refined_intra_data[i]) != len(item):
            mappings_changes.add(i)

    print(f"Total Mappings of Id changed from Intra to Refine Intra - {len(mappings_changes)} of {len(intra_data)}")

    mappings_changes = set()
    for i, item in refined_intra_data.items():
        if len(filtered_intra_data[i]) != len(item):
            mappings_changes.add(i)
            
    print(f"Total Mappings of Id changed from Refine Intra to Filter Intra - {len(mappings_changes)} of {len(refined_intra_data)}")
    
except Exception:
    print("some files do not exists")