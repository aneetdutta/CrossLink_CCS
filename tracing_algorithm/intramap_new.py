import os, sys
sys.path.append(os.getcwd())
from scipy.spatial import KDTree
import pandas as pd
import numpy as np
import pandas as pd
from tqdm import tqdm
import time
from tracing_algorithm.mapping_functions import (
    check_compatibility_vectorized,
    check_compatibility_vectorized_ids,
    compute_localization_error,
    intervals_overlap_intra,
   
    check_compatibility_grid,
    check_compatibility_parallel
)

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAX_MOBILITY_FACTOR = float(os.getenv("MAX_MOBILITY_FACTOR"))
MAX_TRANSMIT_TIME = 180

df = pd.read_csv(f"data/{SCENARIO_NAME}/sniffed_data_{SCENARIO_NAME}.csv")
df["timestep"] = pd.to_numeric(df["timestep"], errors="coerce")

''' Group by "id" to find min and max timestep and extract the protocol '''
id_info = (
    df.groupby("id")
    .agg(
        min=("timestep", "min"), max=("timestep", "max"), protocol=("protocol", "first")
    )
    .reset_index()
)

id_info["protocol"] = id_info["protocol"].astype("category")
df["protocol"] = df["protocol"].astype("category")

# -------------------------------------------------------------------------- #

bluetooth_df = id_info[id_info["protocol"] == "Bluetooth"]
lte_df = id_info[id_info["protocol"] == "LTE"]
wifi_df = id_info[id_info["protocol"] == "WiFi"]

''' Convert each subset into a dictionary '''
comparison_list = {
    "Bluetooth": bluetooth_df.to_dict("records"),
    "LTE": lte_df.to_dict("records"),
    "WiFi": wifi_df.to_dict("records"),
}

del id_info, bluetooth_df, lte_df, wifi_df

protocol_errors = compute_localization_error(df["protocol"])
grouped_dict = {
    id_val: group[
        ["timestep", "id", "sniffer_id", "sl_x", "sl_y", "dist_S_U", "protocol"]
    ]
    for id_val, group in df.groupby("id")
}
comparisons = ["LTE", "Bluetooth", "WiFi"]
# comparisons = ["LTE", "Bluetooth"]
# comparisons = ["Bluetooth"]
# comparisons = ['WiFi']

print("Starting intramapping")

for p1 in comparisons:
    print(p1)
    protocol_pairs = []
    intramap = dict()
    a = time.time()
    for id_a in tqdm(comparison_list[p1], total=len(comparison_list[p1])):
        for id_b in comparison_list[p1]:
            if id_a["id"] != id_b["id"]:
                if intervals_overlap_intra(id_a["max"], id_b["min"]):
                    protocol_pairs.append((id_a["id"], id_b["id"]))
    print(p1, time.time() - a)

    for id1, id2 in tqdm(protocol_pairs, total=len(protocol_pairs)):
        subset1 = grouped_dict[id1]
        subset2 = grouped_dict[id2]
        #compatible = check_compatibility_vectorized(subset1, subset2, protocol_errors)
        compatible = check_compatibility_parallel(subset1, subset2, protocol_errors)
        # compatible = check_compatibility_vectorized_ids(id1, id2, subset1, subset2, protocol_errors)
        
        # if id2 == "P_1-1-pt_1238_B_PMI7T2WI" and id1 == "P_1-1-pt_1226_B_PRMKCCP7":
        #     print(id1, id2, compatible)
        if compatible:
            if id1 not in intramap.keys():
                intramap[id1] = [id2]
            else:
                intramap[id1].append(id2)

    np.save(f"data/{SCENARIO_NAME}/intramap_{p1}.npy", intramap, allow_pickle=True)
    print(f"{p1} completed")

print("Intramap completed")
