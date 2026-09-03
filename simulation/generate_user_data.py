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
from tqdm import tqdm
import json
import time

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
DATA_SOURCE = os.getenv("DATA_SOURCE")
LTE_RANDOMIZATION_MODE = os.getenv("LTE_RANDOMIZATION_MODE", "time").lower()

ml = MyLogger(f"generate_user_data_{SCENARIO_NAME}")

TOTAL_NUMBER_OF_USERS = int(os.getenv("TOTAL_NUMBER_OF_USERS"))
USER_TIMESTEPS = int(os.getenv("USER_TIMESTEPS"))
num_users=TOTAL_NUMBER_OF_USERS
df = pd.read_csv(f"data/raw_user_data_{SCENARIO_NAME}_{num_users}.csv")

raw_user_data = df.to_dicts()

same_userset: set = set()

user_dict = dict()
user_data = deque()

user_proximity_dict = defaultdict(set)
user_proximity_refresh_checker = defaultdict()

BS_XY_CSV = os.getenv(
    "BS_XY_CSV",
    f"data/opencellid_cells_demo_LTE_212_10_uniqueLoc_XY.csv"
)

bs_df = pd.read_csv(BS_XY_CSV)

stations = []
stations_by_id = {}
for r in bs_df.select(["cellid", "x", "y", "range"]).to_dicts():
    cellid = str(r["cellid"])
    x = float(r["x"])
    y = float(r["y"])
    rng = float(r["range"]) if r.get("range") not in (None, "", "nan") else 0.0
    s = {"cellid": cellid, "x": x, "y": y, "r": rng}
    stations.append(s)
    stations_by_id[cellid] = s
#print(stations)
def serving_cellid_xy(ux, uy, prev_cellid=None, hysteresis_m=20.0):
    best_cellid = None
    best_d2 = float("inf")

    for s in stations:
        dx = ux - s["x"]
        dy = uy - s["y"]
        d2 = dx*dx + dy*dy
        if d2 <= (s["r"] * s["r"]):
            if d2 < best_d2:
                best_d2 = d2
                best_cellid = s["cellid"]

    if best_cellid is None:
        return None

    if prev_cellid and prev_cellid in stations_by_id:
        cur = stations_by_id[prev_cellid]
        dx = ux - cur["x"]
        dy = uy - cur["y"]
        cur_d2 = dx*dx + dy*dy
        if cur_d2 <= (cur["r"] * cur["r"]):
            if cur_d2 <= best_d2:
                return prev_cellid

    return best_cellid



for user_ in tqdm(raw_user_data,total=len(raw_user_data)):
    # print(user_)
    user_id = user_["user_id"]
    timestep = user_["timestep"]
    loc_x = user_["loc_x"]
    loc_y = user_["loc_y"]
    

    user:User
    if user_id in list(user_dict):
        user = user_dict[user_id]
        user.location = [loc_x, loc_y]
        
        #print(new_cell)
        if timestep == USER_TIMESTEPS:
            user.transmit_identifiers_force()
        else:
            if LTE_RANDOMIZATION_MODE == "handover":
                #print("handover randomization LTE")
                prev_cellid = getattr(user, "serving_cellid", None)
                new_cellid = serving_cellid_xy(loc_x, loc_y, prev_cellid=prev_cellid)
                user.randomize_identifiers(serving_cellid=new_cellid)
                user.serving_cellid = new_cellid
            else:
                user.randomize_identifiers()
            user.transmit_identifiers()
    else:
        bluetooth_id=f"{user_id}_B_{random_identifier()}"
        wifi_id=f"{user_id}_W_{random_identifier()}"
        lte_id=f"{user_id}_L_{random_identifier()}"
        user = User(user_id,[loc_x,loc_y],bluetooth_id=bluetooth_id, wifi_id=wifi_id, lte_id=lte_id) 
        user_dict[user_id] = user
        #if LTE_RANDOMIZATION_MODE == "handover":
        user.serving_cellid = serving_cellid_xy(loc_x, loc_y, prev_cellid=None)
    
    user_data.append({
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
        "serving_cell_id":user.serving_cellid,
    })


folder_path = f'data/{SCENARIO_NAME}/'
file_path = os.path.join(folder_path, f'user_data_{SCENARIO_NAME}.csv')
os.makedirs(folder_path, exist_ok=True)

print("Saved file to the directory")
df = pd.DataFrame(list(user_data))
columns_to_replace = ['randomized_ble', 'randomized_wifi', 'randomized_lte']

for col_name in columns_to_replace:
    df = df.with_columns(
        pd.when(pd.col(col_name) == False)
        .then(None)
        .otherwise(pd.col(col_name))
        .alias(col_name)
    )

df.write_csv(file_path)
