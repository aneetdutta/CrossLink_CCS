import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.user import User
from collections import deque
from modules.general import str_to_bool
from modules.general import random_identifier
from modules.general import calculate_distance_l
import polars as pd
from modules.logger import MyLogger
from collections import defaultdict
import json
import time

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
DATA_SOURCE = os.getenv("DATA_SOURCE")
PROXIMITY_DISTANCE = float(os.getenv("PROXIMITY_DISTANCE", 20))
TOTAL_NUMBER_OF_USERS = int(os.getenv("TOTAL_NUMBER_OF_USERS"))
USER_TIMESTEPS = int(os.getenv("USER_TIMESTEPS"))
ml = MyLogger(f"generate_user_data_proximity_{SCENARIO_NAME}")
num_users=TOTAL_NUMBER_OF_USERS

#df = pd.read_csv(f"data/raw_user_data_{DATA_SOURCE}_{TOTAL_NUMBER_OF_USERS}_{num_users}.csv")

df = pd.read_csv(f"data/raw_user_data_{SCENARIO_NAME}_{num_users}.csv")
df_sorted = df.sort('timestep')

user_dict = dict()
user_data = deque()
    
# Group by 'timestep'
timestep_groups = df_sorted.group_by(['timestep'])

user_proximity_dict_old = dict()

from scipy.spatial import KDTree
import numpy as np

def optimized_proximity_check(user_list, user_loc, PROXIMITY_DISTANCE, timestep):
    locations = [user_loc[user] for user in user_list]
    kd_tree = KDTree(locations)
    user_proximity_dict = {user: set() for user in user_list}

    for i, user1 in enumerate(user_list):
        loc1 = user_loc[user1]
        indices = kd_tree.query_ball_point(loc1, PROXIMITY_DISTANCE)
        for j in indices:
            if i != j:
                user2 = user_list[j]
                dist = np.linalg.norm(np.array(loc1) - np.array(user_loc[user2]))
                if dist <= PROXIMITY_DISTANCE:
                    # ml.logger.info(f"{user1}, {user2}, {dist}, {PROXIMITY_DISTANCE}, {timestep}")
                    user_proximity_dict[user1].add(user2)
                    user_proximity_dict[user2].add(user1)

    return user_proximity_dict


def generate_user_data(ti_dict, user_id, user_loc: dict, user_dict: dict, timestep, reset_timers=False):
    location = user_loc[user_id]
    user:User
    if user_id in list(user_dict):
        user = user_dict[user_id]
        user.location = location
        # print(reset_timers, timestep, user_id)
        if timestep == USER_TIMESTEPS:
            user.transmit_identifiers_force()
        else:
            user.randomize_identifiers(reset_timers=reset_timers)
            if not ti_dict[user_id]:
                user.transmit_identifiers(timestep_checker = timestep)
                ti_dict[user_id] = True
        # print(user.identifier_counter, user.next_bluetooth_transmit, user.next_wifi_transmit, user.next_lte_transmit)
        # print(user.identifier_counter, user.next_protocol_refresh)
        # print(user.transmit_lte, user.transmit_wifi, user.transmit_wifi)
    else:
        bluetooth_id=f"{user_id}_B_{random_identifier()}"
        wifi_id=f"{user_id}_W_{random_identifier()}"
        lte_id=f"{user_id}_L_{random_identifier()}"
        user = User(user_id,location,bluetooth_id=bluetooth_id, wifi_id=wifi_id, lte_id=lte_id) 
        user.timestep = timestep
        user_dict[user_id] = user
    
    user_gen_data_ = {
        "timestep": timestep,
        "user_id": user.user_id,
        "loc_x": user.location[0],
        "loc_y": user.location[1],
        "bluetooth_id": user.bluetooth_id,
        "wifi_id": user.wifi_id,
        "lte_id": user.lte_id,
        "transmit_ble": user.transmit_bluetooth,
        "transmit_wifi": user.transmit_wifi,
        "transmit_lte": user.transmit_lte,
        "randomized_ble": user.randomized_bluetooth,
        "randomized_wifi": user.randomized_wifi,
        "randomized_lte": user.randomized_lte,
    }
    
    return user_dict, user_gen_data_, ti_dict

i=0
timestep_:pd.DataFrame
for timestep, timestep_data in timestep_groups:
    print(timestep)
    raw_user_data = timestep_data.to_dicts()
    ml.logger.info(f"timestep - {timestep}")
    temp_timestep_user_data = dict()
    user_proximity_refresh_checker = defaultdict()
    
    user_loc = defaultdict(list, {user_["user_id"]: [user_["loc_x"], user_["loc_y"]] for user_ in raw_user_data})
    user_list = list(user_loc)
    user_proximity_dict = defaultdict(tuple, {user_["user_id"]: set() for user_ in raw_user_data})
    ti_dict = defaultdict(bool, {user_["user_id"]: False for user_ in raw_user_data})
    user_proximity_refresh_checker = defaultdict(tuple, {user_["user_id"]: False for user_ in raw_user_data})
    
    transmit_timer = defaultdict(list, {user_["user_id"]: [False, False, False] for user_ in raw_user_data})
    # l= False
    if len(raw_user_data) > 1:
        user_proximity_dict = optimized_proximity_check(user_list, user_loc, PROXIMITY_DISTANCE, timestep)

    if int(timestep[0]) == 25141:
        print("Hello")
        print(user_proximity_dict["pedestrian_2-1_3376"])
        print(user_proximity_dict["pedestrian_1-2_3908"])
        
    for user_id in user_list:
        
        if user_proximity_dict_old and user_id in user_proximity_dict_old and (user_proximity_dict[user_id] - user_proximity_dict_old[user_id]):
            ml.logger.info(f" 1 - {user_id}, {timestep}")
            # if not user_proximity_refresh_checker[user_id]:
                # ml.logger.info(f"Case 1- user id {user_id}")
            user_dict, user_gen_data, ti_dict = generate_user_data(ti_dict, user_id, user_loc, user_dict, timestep[0], reset_timers=True)
            if transmit_timer[user_id][0]:
                user_gen_data["transmit_ble"] = True
            if transmit_timer[user_id][1]:
                user_gen_data["transmit_wifi"] = True
            if transmit_timer[user_id][2]:
                user_gen_data["transmit_lte"] = True
                
            if user_gen_data["transmit_ble"]:
                transmit_timer[user_id][0] = True
            if user_gen_data["transmit_wifi"]:
                transmit_timer[user_id][1] = True
            if user_gen_data["transmit_lte"]:
                transmit_timer[user_id][2] = True
                
            temp_timestep_user_data[user_id] = user_gen_data
            user_proximity_refresh_checker[user_id] = True
            
            for other_user_id in user_proximity_dict[user_id]:
                # if not user_proximity_refresh_checker[other_user_id]:
                ml.logger.info(other_user_id)
                # ml.logger.info(f"Case 1- other user id {other_user_id}")
                user_dict, user_gen_data, ti_dict = generate_user_data(ti_dict, other_user_id, user_loc, user_dict, timestep[0], reset_timers=True)
                # print("other user id", other_user_id)
                if transmit_timer[other_user_id][0]:
                    user_gen_data["transmit_ble"] = True
                if transmit_timer[other_user_id][1]:
                    user_gen_data["transmit_wifi"] = True
                if transmit_timer[other_user_id][2]:
                    user_gen_data["transmit_lte"] = True
                    
                if user_gen_data["transmit_ble"]:
                    transmit_timer[other_user_id][0] = True
                if user_gen_data["transmit_wifi"]:
                    transmit_timer[other_user_id][1] = True
                if user_gen_data["transmit_lte"]:
                    transmit_timer[other_user_id][2] = True
                    
                temp_timestep_user_data[other_user_id] = user_gen_data
                user_proximity_refresh_checker[other_user_id] = True
        else:
            is_randomized = False
            generated_data_temp = []
            if not user_proximity_refresh_checker[user_id]:
                user_dict, user_gen_data, ti_dict = generate_user_data(ti_dict, user_id, user_loc, user_dict, timestep[0])  
                generated_data_temp.append((user_id, user_gen_data))                  
            else:
                generated_data_temp.append((user_id, None))
                
            if user_id in user_dict:
                user: User = user_dict[user_id]
                is_randomized = is_randomized or user.randomized
                if is_randomized:
                    ml.logger.info(f"2 - {user_id}, {timestep}, {is_randomized}")

            for other_user_id in user_proximity_dict[user_id]:
                if not user_proximity_refresh_checker[other_user_id]:
                    user_dict, user_gen_data, ti_dict = generate_user_data(ti_dict, other_user_id, user_loc, user_dict, timestep[0])
                    generated_data_temp.append((other_user_id, user_gen_data))
                else:
                    generated_data_temp.append((other_user_id, None))
                    
                if other_user_id in user_dict:
                    user: User = user_dict[other_user_id]
                    is_randomized = is_randomized or user.randomized
                    if is_randomized:
                        ml.logger.info(f"3 - {user_id}, {other_user_id}, {timestep}, {is_randomized}")
                        
            if is_randomized:# and len(generated_data_temp) > 1:
                p = set()
                for uid, _ in generated_data_temp:
                    p.add(uid)
                    user_dict, user_gen_data, ti_dict = generate_user_data(ti_dict, uid, user_loc, user_dict, timestep[0], reset_timers=True)
                    if transmit_timer[uid][0]:
                        user_gen_data["transmit_ble"] = True
                    if transmit_timer[uid][1]:
                        user_gen_data["transmit_wifi"] = True
                    if transmit_timer[uid][2]:
                        user_gen_data["transmit_lte"] = True
                    temp_timestep_user_data[uid] = user_gen_data
                    user_proximity_refresh_checker[uid] = True
                    
                ml.logger.info(f"{p} - All randomized")
            else:
                # ml.logger.info("Users not randomizing")
                for uid, user_gen_data in generated_data_temp:
                    if uid not in temp_timestep_user_data:
                        if transmit_timer[uid][0]:
                            user_gen_data["transmit_ble"] = True
                        if transmit_timer[uid][1]:
                            user_gen_data["transmit_wifi"] = True
                        if transmit_timer[uid][2]:
                            user_gen_data["transmit_lte"] = True
                            
                        temp_timestep_user_data[uid] = user_gen_data
                    user_proximity_refresh_checker[uid] = True
    # if timestep[0] == 18114.0:
    #     print(temp_timestep_user_data)
    user_data.extend(temp_timestep_user_data.values())

    i+=1
    
    # if i> 500:
    #     break
    
    user_proximity_dict_old = user_proximity_dict



folder_path = f'data/{SCENARIO_NAME}/'
file_path = os.path.join(folder_path, f'user_data_{SCENARIO_NAME}.csv')
os.makedirs(folder_path, exist_ok=True)

# user_file = f"data/user_data_{SCENARIO_NAME}.csv"
print("Saved file to the directory")
df = pd.DataFrame(list(user_data))
df = df.sort('timestep')
columns_to_replace = ['randomized_ble', 'randomized_wifi', 'randomized_lte']

for col_name in columns_to_replace:
    df = df.with_columns(
        pd.when(pd.col(col_name) == False)
        .then(None)
        .otherwise(pd.col(col_name))
        .alias(col_name)
    )
# print(df['randomized_ble'])
df.write_csv(file_path)
