import os, sys
sys.path.append(os.getcwd())
from modules.general import *
from collections import defaultdict
''' Load the sumo_simulation result from mongodb '''
from modules.general import UnionFind
import pandas as pd
from modules.logger import MyLogger
import polars as pl
from tqdm import tqdm
import re

pattern="_B_"

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))


ml = MyLogger(f"reconstruction_single_{SCENARIO_NAME}")

df = pl.read_parquet(f"data/{SCENARIO_NAME}/aggregated_id_{SCENARIO_NAME}.parquet")
id_data = df.to_pandas()
id_protocol = {row['id']: row['protocol'] for _, row in id_data.iterrows()}
id_user_data = {row['id']: row['user_id'] for _, row in id_data.iterrows()}
id_timestep_data = {row['id']: (row['start_timestep'], row['last_timestep'])     for _, row in id_data.iterrows()
}

intra_data = np.load(f'data/{SCENARIO_NAME}/filtered_intramap_single_{SCENARIO_NAME}.npy', allow_pickle=True).item()

user_df = pl.read_parquet(f"data/{SCENARIO_NAME}/aggregated_users_{SCENARIO_NAME}.parquet")
user_df = user_df.to_pandas()
user_data = {row['user_id']: row['ids'] for _, row in user_df.iterrows()}
user_time_data = {row['user_id']: row['last_timestep'] for _, row in user_df.iterrows()}

#print(intra_data)


''' TO change below - form chains without user_id'''
# intra_data_user = {}
# for id, mapping in intra_data.items():
#     user_id = id_user_data[id]
#     checker = True
#     for id_ in list(mapping):
#         if id_user_data[id_] != user_id:
#             checker = False
#     if checker:
#         if len(mapping) == 1:
#             intra_data_user[id] = mapping[0]
#         else:
#             intra_data_user[id] = ''
#     else:
#         intra_data_user[id] = ''

# chained_intra = find_all_possible_chains(intra_data_user)

intra_single = {}
# c=0
# total=0
# total_b=0
# c_b=0
# mix=set()
for id, mapping in intra_data.items():
    # total=total+1
    # if re.search(pattern,id):
    #     total_b=total_b+1
    if len(mapping) > 1:
        intra_single[id] = ''
        # if re.search(pattern,id):
        #     index=id.find(pattern)
        #     mix.add(id[:index])
    elif len(mapping)==1:
        
        intra_single[id] = mapping[0]
        # c=c+1
        
        # if re.search(pattern,id):
        #     c_b=c_b+1
    else:
        intra_single[id] = ''
        #print(id)
# print("Aneet")
# print(c/total)
# print(mix)
# print(c_b/total_b)
print("Computing all possible chains")
'''  Generate all possible chains in form of list of lists of intra mappings '''
chained_intra = find_all_possible_chains(intra_single)


single_protocol = []
incorrectness = defaultdict(set)
corresponding_users = set()

print("Reconstruction single started")

for index, row in tqdm(id_data.iterrows(), total=id_data.shape[0]):
    min_start_timestep, max_last_timestep = None, None
    id = row["id"]
    user_id = row["user_id"]
        
    min_start_timestep = row["start_timestep"]
    max_last_timestep = row["last_timestep"]
    
    if id in intra_data:
        chain = get_list_containing_value(chained_intra, id)
        if not set(chain).issubset(user_data[user_id]):
            incorrectness[id].update(set(chain))
            corresponding_users.add(user_id)
        else:
            id_df = id_data[id_data['id'].isin(chain)]
            min_start_timestep = min(min_start_timestep, id_df['start_timestep'].min())
            max_last_timestep = max(max_last_timestep, id_df['last_timestep'].max())     

    duration = max_last_timestep - min_start_timestep + 1
    
    single_protocol.append({"id": id, "start_timestep": min_start_timestep, "last_timestep": max_last_timestep, "total_time": duration, "user_id": row["user_id"], "protocol": row["protocol"]})

single_protocol_df = pd.DataFrame(single_protocol)

ml.logger.info(f"{len(incorrectness)} total incorrectness and {len(corresponding_users)} incorrect users")
print(f"{len(incorrectness)} total incorrectness and {len(corresponding_users)} incorrect users")
ml.logger.info(f"{incorrectness} incorrect mappings, {corresponding_users} incorrect users")


if ENABLE_WIFI:
    wifi_df = single_protocol_df[single_protocol_df['protocol'] == 'WiFi'].reset_index(drop=True)
    wifi_df = pd.merge(wifi_df, user_df[['user_id', 'wifi_duration']], left_on='user_id', right_on='user_id', how='left')
    wifi_df['privacy_score'] = wifi_df.apply(
        lambda row: calculate_privacy_score_single(row, 'wifi_duration'), axis=1
    )
    idx = wifi_df.groupby('user_id')['privacy_score'].idxmax()
    wifi_df = wifi_df.loc[idx].reset_index(drop=True)
else:
    wifi_df = None

if ENABLE_LTE:
    lte_df = single_protocol_df[single_protocol_df['protocol'] == 'LTE'].reset_index(drop=True)
    lte_df = pd.merge(lte_df, user_df[['user_id', 'lte_duration']], left_on='user_id', right_on='user_id', how='left')
    lte_df['privacy_score'] = lte_df.apply(
        lambda row: calculate_privacy_score_single(row, 'lte_duration'), axis=1
    )
    # print(lte_df[lte_df["user_id"] == "pedestrian_1-1-pt_2770"])
    idx = lte_df.groupby('user_id')['privacy_score'].idxmax()
    lte_df = lte_df.loc[idx].reset_index(drop=True)
else:
    lte_df = None

if ENABLE_BLUETOOTH:
    bluetooth_df = single_protocol_df[single_protocol_df['protocol'] == 'Bluetooth'].reset_index(drop=True)
    bluetooth_df = pd.merge(bluetooth_df, user_df[['user_id', 'ble_duration']], left_on='user_id', right_on='user_id', how='left')
    bluetooth_df['privacy_score'] = bluetooth_df.apply(
        lambda row: calculate_privacy_score_single(row, 'ble_duration'), axis=1
    )
    idx = bluetooth_df.groupby('user_id')['privacy_score'].idxmax()
    bluetooth_df = bluetooth_df.loc[idx].reset_index(drop=True)
else:
    bluetooth_df = None


folder_path = f'output/data/{SCENARIO_NAME}/'
os.makedirs(folder_path, exist_ok=True)

if ENABLE_WIFI:
    wifi_df.to_csv(f'{folder_path}single_wifi_{SCENARIO_NAME}.csv', index=False)
if ENABLE_BLUETOOTH:
    bluetooth_df.to_csv(f'{folder_path}single_ble_{SCENARIO_NAME}.csv', index=False)
if ENABLE_LTE:
    lte_df.to_csv(f'{folder_path}single_lte_{SCENARIO_NAME}.csv', index=False)
    
ml.logger.info("Baseline Privacy score calculated")
