import os, sys
sys.path.append(os.getcwd())
from modules.general import *

import pandas as pd
import polars as pl
from tqdm import tqdm
from modules.logger import MyLogger

def ensure_rchain_list(x):
    
    if isinstance(x, str):
        return ast.literal_eval(x)
    return x


def merge_intervals(intervals):
   
    if not intervals:
        return []

    intervals = sorted(intervals, key=lambda t: t[0])
    merged = [list(intervals[0])]

    for start, end in intervals[1:]:
        last_start, last_end = merged[-1]

        # overlap or touching
        if start <= last_end + 1:
            merged[-1][1] = max(last_end, end)
        else:
            merged.append([start, end])

    return [(s, e) for s, e in merged]


def interval_length(intervals):
   
    return sum(e - s + 1 for s, e in intervals)


def tracking_fraction_from_rchain(rchain, id_data):
    """
    Compute BLE/LTE tracking stats from the selected rchain for one user.

    Returns:
    - BLE tracked time
    - LTE tracked time
    - union tracked time by BLE or LTE
    - protocol-normalized shares that sum to 1:
        ble_share_of_protocol_time
        lte_share_of_protocol_time
    - raw coverage shares over the tracked timeline:
        ble_total_share
        lte_total_share
    """
    rchain = ensure_rchain_list(rchain)

    if not rchain:
        return pd.Series({
            "ble_id_count": 0,
            "lte_id_count": 0,
            "ble_tracked_time": 0,
            "lte_tracked_time": 0,
            "any_tracking_time": 0,
            "ble_total_share": np.nan,
            "lte_total_share": np.nan,
            "ble_share_of_protocol_time": np.nan,
            "lte_share_of_protocol_time": np.nan
        })

    chain_df = id_data[id_data["id"].isin(rchain)].copy()

    ble_df = chain_df[chain_df["protocol"] == "Bluetooth"].copy()
    lte_df = chain_df[chain_df["protocol"] == "LTE"].copy()
    tracked_df = chain_df[chain_df["protocol"].isin(["Bluetooth", "LTE"])].copy()

    ble_intervals = merge_intervals(
        list(zip(ble_df["start_timestep"], ble_df["last_timestep"]))
    )
    lte_intervals = merge_intervals(
        list(zip(lte_df["start_timestep"], lte_df["last_timestep"]))
    )
    tracked_intervals = merge_intervals(
        list(zip(tracked_df["start_timestep"], tracked_df["last_timestep"]))
    )

    ble_time = interval_length(ble_intervals)
    lte_time = interval_length(lte_intervals)
    any_time = interval_length(tracked_intervals)

    protocol_sum = ble_time + lte_time

    return pd.Series({
        "ble_id_count": ble_df["id"].nunique(),
        "lte_id_count": lte_df["id"].nunique(),
        "ble_tracked_time": ble_time,
        "lte_tracked_time": lte_time,
        "any_tracking_time": any_time,

        # raw coverage over the tracked timeline
        "ble_total_share": ble_time / any_time if any_time > 0 else np.nan,
        "lte_total_share": lte_time / any_time if any_time > 0 else np.nan,

        # normalized shares that sum to 1
        "ble_share_of_protocol_time": ble_time / protocol_sum if protocol_sum > 0 else np.nan,
        "lte_share_of_protocol_time": lte_time / protocol_sum if protocol_sum > 0 else np.nan
    })

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))

ml = MyLogger(f"reconstruction_multi_{SCENARIO_NAME}")

df = pl.read_parquet(f"data/{SCENARIO_NAME}/aggregated_id_{SCENARIO_NAME}.parquet")
id_data = df.to_pandas()
id_protocol = {row['id']: row['protocol'] for _, row in id_data.iterrows()}
id_user_data = {row['id']: row['user_id'] for _, row in id_data.iterrows()}
id_timestep_data = {row['id']: (row['start_timestep'], row['last_timestep'])     for _, row in id_data.iterrows()
}

inter_data = np.load(f'data/{SCENARIO_NAME}/refined_intermap_{SCENARIO_NAME}.npy', allow_pickle=True).item()
intra_data = np.load(f'data/{SCENARIO_NAME}/filtered_intramap_{SCENARIO_NAME}.npy', allow_pickle=True).item()


user_df = pl.read_parquet(f"data/{SCENARIO_NAME}/aggregated_users_{SCENARIO_NAME}.parquet")
user_df = user_df.to_pandas()
user_data = {row['user_id']: row['ids'] for _, row in user_df.iterrows()}
user_time_data = {row['user_id']: row['last_timestep'] for _, row in user_df.iterrows()}
# user_df = user_df.drop(['sniffer_list', '_id', 'trace'])

'''

        Baseline Below 

'''

if ENABLE_WIFI:
    wifi_df = id_data[id_data['protocol'] == 'WiFi'].reset_index(drop=True)
    wifi_df = pd.merge(wifi_df, user_df[['user_id', 'wifi_duration']], left_on='user_id', right_on='user_id', how='left')
    wifi_df['privacy_score'] = wifi_df.apply(
        lambda row: calculate_privacy_score_single(row, 'wifi_duration'), axis=1
    )
    idx = wifi_df.groupby('user_id')['privacy_score'].idxmax()
    wifi_df = wifi_df.loc[idx].reset_index(drop=True)
else:
    wifi_df = None

if ENABLE_LTE:
    lte_df = id_data[id_data['protocol'] == 'LTE'].reset_index(drop=True)
    lte_df = pd.merge(lte_df, user_df[['user_id', 'lte_duration']], left_on='user_id', right_on='user_id', how='left')
    lte_df['privacy_score'] = lte_df.apply(
        lambda row: calculate_privacy_score_single(row, 'lte_duration'), axis=1
    )
    idx = lte_df.groupby('user_id')['privacy_score'].idxmax()
    lte_df = lte_df.loc[idx].reset_index(drop=True)
else:
    lte_df = None

if ENABLE_BLUETOOTH:
    bluetooth_df = id_data[id_data['protocol'] == 'Bluetooth'].reset_index(drop=True)
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
    file_path = os.path.join(folder_path, f'baseline_wifi_{SCENARIO_NAME}.csv')
    wifi_df.to_csv(file_path, index=False)
if ENABLE_LTE:
    file_path = os.path.join(folder_path, f'baseline_lte_{SCENARIO_NAME}.csv')
    lte_df.to_csv(file_path, index=False)
if ENABLE_BLUETOOTH:
    file_path = os.path.join(folder_path, f'baseline_ble_{SCENARIO_NAME}.csv')
    bluetooth_df.to_csv(file_path, index=False)

ml.logger.info("Baseline Privacy score calculated")

''' 
        Multi Protocol Mapping Below 
'''

print("Loaded and Multiprotocol reconstruction started")
intra_single = {}
for id, mapping in intra_data.items():
    if len(mapping) > 1:
        intra_single[id] = ''
    elif mapping:
        intra_single[id] = mapping[0]
    else:
        intra_single[id] = ''

print("Computing all possible chains")
'''  Generate all possible chains in form of list of lists of intra mappings '''
chained_intra = find_all_possible_chains(intra_single)

chained_dict = {char: lst for lst in chained_intra for char in lst}
corresponding_users = set()
multi_protocol = []

ml.logger.info("Reconstruction started")
print("Reconstruction started")
incorrectness = defaultdict(set)
total_rows = len(inter_data)
reconstructed_inter = {}

''' Iterate through all inter mappings assuming that inter consists of all ids '''
for inter_id in tqdm(inter_data, total=len(inter_data)):
    mapping = inter_data[inter_id]
    u = id_user_data[inter_id]
    min_start_timestep, max_last_timestep = id_timestep_data[inter_id][0], id_timestep_data[inter_id][1]
    
    ''' Get the intra chain for that inter id '''
    if inter_id in chained_dict:
        chain1 = chained_dict[inter_id]
    else:
        chain1 = []
    # user_id_match = inter_row["user_id_match"]
    ''' Get the chain for every protocol mapping of the inter id '''
    chain_ = inter_intra_mapper(mapping, chained_intra)

    ''' Append all these chains so that we have now chain of each protocol mapping to ideally same user id '''
    chain_.append(chain1)
    
    user_id_ = None
    lchain = []
    
    '''Due to computation this becomes slower, so we directly use the user_id available with the inter to verify the corrcetness'''
    ids = user_data[id_user_data[inter_id]]
    ''' Considering all protocols ids matching the user id (finally verification) '''
    total=0
    inc=0
    for i, c in enumerate(chain_):
        total=total+1
        if not c:
            continue
        if set(c).issubset(ids):
            lchain.extend(c)
        else:
            inc=inc+1
            incorrectness[inter_id].update(c)
            corresponding_users.add(u)
    
    if not lchain:
        ''' Consider baseline'''
        reconstructed_inter[inter_id] = [inter_id]
        continue
    
    ''' Deriving final longest chain of ids (contains all protocol ids) '''
    reconstructed_inter[inter_id] = lchain
    

ml.logger.info("Processing now")
print("Processing now")
for inter_id in tqdm(reconstructed_inter, total=len(reconstructed_inter)):
    rchain = reconstructed_inter[inter_id]
    #print("-----")
    #print(inter_id)
    #print(rchain)

    min_start_timestep, max_last_timestep, protocol_ = id_timestep_data[inter_id][0], id_timestep_data[inter_id][1], id_protocol[inter_id]
    u = id_user_data[inter_id]
    #print(u)

    fetch_inter_mapping_timesteps = id_data[id_data['id'].isin(rchain)]
    #print(fetch_inter_mapping_timesteps)
    #print("------")
    min_start_timestep = min(fetch_inter_mapping_timesteps['start_timestep'].min(), min_start_timestep)
    max_last_timestep = max(fetch_inter_mapping_timesteps['last_timestep'].max(), max_last_timestep)

    duration = max_last_timestep - min_start_timestep + 1
    ''' Fetch min and max of rchain and process it '''
   # multi_protocol.append({"id": inter_id, "start_timestep": min_start_timestep, "last_timestep": max_last_timestep, "total_time": duration, "user_id": u, "protocol": protocol_},"rchain": list(dict.fromkeys(rchain)))
    multi_protocol.append({
    "id": inter_id,
    "start_timestep": min_start_timestep,
    "last_timestep": max_last_timestep,
    "total_time": duration,
    "user_id": u,
    "protocol": protocol_,
    "rchain": list(dict.fromkeys(rchain))
})

ml.logger.info(f"{len(incorrectness)} total incorrectness and {len(corresponding_users)} incorrect users")
print(f"{len(incorrectness)} total incorrectness and {len(corresponding_users)} incorrect users")
print(total)
print(inc)
ml.logger.info(f"{incorrectness} incorrect mappings, {corresponding_users} incorrect users")

print("completed")
multi_protocol_df = pd.DataFrame(multi_protocol)
ml.logger.info(multi_protocol_df)
multi_protocol_df = pd.merge(multi_protocol_df, user_df[['user_id', 'ideal_duration']], left_on='user_id', right_on='user_id', how='left')
multi_protocol_df = pd.merge(multi_protocol_df, user_df[['user_id']], left_on='user_id', right_on='user_id', how='left')

multi_protocol_df['privacy_score'] = multi_protocol_df.apply(calculate_privacy_score, axis=1)
idx = multi_protocol_df.groupby('user_id')['privacy_score'].idxmax()
multi_protocol_df = multi_protocol_df.loc[idx].reset_index(drop=True)

multi_data = multi_protocol_df.to_dict(orient='records')

folder_path = f'output/data/{SCENARIO_NAME}/'
os.makedirs(folder_path, exist_ok=True)

multi_protocol_df.to_csv(f'{folder_path}multi_protocol_{SCENARIO_NAME}.csv', index=False)


idx = multi_protocol_df.groupby('user_id')['privacy_score'].idxmax()
multi_protocol_df = multi_protocol_df.loc[idx].reset_index(drop=True)



    
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# =========================
# Configure paths
# =========================

#SCENARIO_NAME = "scenario_result_512_sumo_all1"

# Update these paths if needed

INTRAMAP_SINGLE_PATH = f"data/{SCENARIO_NAME}/filtered_intramap_single_{SCENARIO_NAME}.npy"
INTRAMAP_FILTERED_PATH = f"data/{SCENARIO_NAME}/filtered_intramap_{SCENARIO_NAME}.npy"

# Optional: exact ground-truth user mapping from your project data
AGG_ID_PARQUET = f"data/{SCENARIO_NAME}/aggregated_id_{SCENARIO_NAME}.parquet"

OUT_PNG = f"correct_linkings_by_mapping_protocol_{SCENARIO_NAME}.png"
OUT_PDF = f"correct_linkings_by_mapping_protocol_{SCENARIO_NAME}.pdf"
OUT_CSV = f"correct_linkings_summary_{SCENARIO_NAME}.csv"


# =========================
# Helpers
# =========================

def load_npy_dict(path):
    """Load a dict saved in .npy format."""
    obj = np.load(path, allow_pickle=True)
    try:
        return obj.item()
    except Exception:
        return obj


def normalize_mapping(mapping):
    """
    Convert mapping into a clean Python list of target IDs.
    Handles list / tuple / set / numpy array / scalar / empty-string cases.
    """
    if mapping is None:
        return []

    if isinstance(mapping, str):
        return [mapping] if mapping != "" else []

    if isinstance(mapping, np.ndarray):
        if mapping.ndim == 0:
            return normalize_mapping(mapping.item())
        mapping = mapping.tolist()

    if isinstance(mapping, (list, tuple, set)):
        out = []
        for x in mapping:
            if x is None:
                continue
            if isinstance(x, np.generic):
                x = x.item()
            if isinstance(x, float) and np.isnan(x):
                continue
            if x == "":
                continue
            out.append(str(x))
        return out

    return [str(mapping)]


def get_protocol(identifier):
    """
    Infer protocol from identifier structure like:
    P_1-3_2278_L_CG60EI  -> LTE
    P_1-3_2278_B_XYZ123  -> BLE
    """
    identifier = str(identifier)
    parts = identifier.split("_")

    # Common pattern: protocol token is the penultimate piece
    if len(parts) >= 2:
        code = parts[-2].upper()
        if code in {"L", "LTE"}:
            return "LTE"
        if code in {"B", "BLE", "BT", "BLUETOOTH"}:
            return "BLE"
        if code in {"W", "WIFI"}:
            return "WiFi"

    return "Unknown"


def infer_user_from_identifier(identifier):
    """
    Fallback heuristic when aggregated_id parquet is unavailable.
    Assumes the stable user/entity part is everything except the last two tokens:
    e.g. P_1-3_2278_L_CG60EI -> P_1-3_2278
    """
    identifier = str(identifier)
    parts = identifier.split("_")
    if len(parts) >= 3:
        return "_".join(parts[:-2])
    return identifier


def build_id_to_user_map(parquet_path):
    """
    Use exact id -> user_id mapping if parquet exists.
    Falls back to None if unavailable.
    """
    if not os.path.exists(parquet_path):
        return None

    # Prefer polars if available, otherwise pandas
    try:
        import polars as pl
        df = pl.read_parquet(parquet_path).to_pandas()
    except Exception:
        df = pd.read_parquet(parquet_path)

    return dict(zip(df["id"].astype(str), df["user_id"].astype(str)))


def same_user(src_id, dst_id, id_to_user=None):
    """
    Check whether src and dst belong to the same user.
    Uses exact parquet mapping if available; otherwise fallback heuristic.
    """
    src_id = str(src_id)
    dst_id = str(dst_id)

    if id_to_user is not None:
        return id_to_user.get(src_id) == id_to_user.get(dst_id)

    return infer_user_from_identifier(src_id) == infer_user_from_identifier(dst_id)


def summarize_mapping(mapping_dict, mapping_name, id_to_user=None):
    """
    Build per-link detail table and per-protocol summary.
    A link is correct iff:
      - singleton
      - same-user
    """
    rows = []

    for src, raw_mapping in mapping_dict.items():
        src = str(src)
        protocol = get_protocol(src)

        # We only plot BLE and LTE here
        if protocol not in {"BLE", "LTE", "WiFi"}:
            continue

        targets = normalize_mapping(raw_mapping)
        is_singleton = len(targets) == 1
        is_same_user = is_singleton and same_user(src, targets[0], id_to_user=id_to_user)
        is_correct = is_singleton and is_same_user

        rows.append({
            "mapping_type": mapping_name,
            "source_id": src,
            "protocol": protocol,
            "targets": targets,
            "n_targets": len(targets),
            "is_singleton": is_singleton,
            "is_same_user": is_same_user,
            "is_correct": is_correct
        })

    detail_df = pd.DataFrame(rows)

    summary_df = (
        detail_df.groupby(["mapping_type", "protocol"], as_index=False)
        .agg(
            total_links=("source_id", "size"),
            correct_links=("is_correct", "sum"),
        )
    )
    summary_df["pct_correct"] = 100 * summary_df["correct_links"] / summary_df["total_links"]

    return detail_df, summary_df


# =========================
# Load files
# =========================

intramap_single = load_npy_dict(INTRAMAP_SINGLE_PATH)
intramap_filtered = load_npy_dict(INTRAMAP_FILTERED_PATH)

id_to_user = build_id_to_user_map(AGG_ID_PARQUET)

# =========================
# Compute summaries
# =========================

detail_single, summary_single = summarize_mapping(
    intramap_single,
    mapping_name="intramap_single",
    id_to_user=id_to_user
)

detail_filtered, summary_filtered = summarize_mapping(
    intramap_filtered,
    mapping_name="filtered_intramap",
    id_to_user=id_to_user
)

summary_df = pd.concat([summary_single, summary_filtered], ignore_index=True)

# Save summary table
summary_df.to_csv(OUT_CSV, index=False)
#print(summary_df)


# =========================
# Plot
# =========================

# Make grouped bar plot:
# x-axis = mapping type
# bars = BLE vs LTE
# Make grouped bar plot:
# x-axis = mapping type
# bars = BLE vs LTE vs WiFi
plot_df = summary_df.copy()

mapping_order = ["intramap_single", "filtered_intramap"]
protocol_order = ["BLE", "LTE", "WiFi"]

# Optional normalization in case protocol names vary upstream
plot_df["protocol"] = plot_df["protocol"].replace({
    "Bluetooth": "BLE",
    "Wi-Fi": "WiFi",
    "wifi": "WiFi",
    "WiFi": "WiFi"
})

plot_df["mapping_type"] = pd.Categorical(
    plot_df["mapping_type"],
    categories=mapping_order,
    ordered=True
)
plot_df["protocol"] = pd.Categorical(
    plot_df["protocol"],
    categories=protocol_order,
    ordered=True
)

plot_df = plot_df.sort_values(["mapping_type", "protocol"]).reset_index(drop=True)

available_protocols = [p for p in protocol_order if (plot_df["protocol"] == p).any()]
print(available_protocols)
if not available_protocols:
    raise ValueError("No BLE/LTE/WiFi rows found in summary_df.")

pivot = (
    plot_df.pivot(index="mapping_type", columns="protocol", values="pct_correct")
    .reindex(index=mapping_order, columns=available_protocols)
)
count_pivot = (
    plot_df.pivot(index="mapping_type", columns="protocol", values="correct_links")
    .reindex(index=mapping_order, columns=available_protocols)
)
total_pivot = (
    plot_df.pivot(index="mapping_type", columns="protocol", values="total_links")
    .reindex(index=mapping_order, columns=available_protocols)
)

fig, ax = plt.subplots(figsize=(9, 5.5))

x = np.arange(len(pivot.index))

group_width = 0.72
n_protocols = len(available_protocols)

slot_width = group_width / n_protocols
bar_width = slot_width * 0.55
offsets = (np.arange(n_protocols) - (n_protocols - 1) / 2) * slot_width

#for offset, protocol in zip(offsets, available_protocols):
   # values = pivot[protocol].to_numpy(dtype=float)
   # bars = ax.bar(x + offset, values, bar_width, label=protocol)

for offset, protocol in zip(offsets, available_protocols):
    values = pivot[protocol].to_numpy(dtype=float)
    bars = ax.bar(x + offset, values, bar_width, label=protocol)

    for i, bar in enumerate(bars):
        mapping_name = pivot.index[i]
        pct = pivot.loc[mapping_name, protocol]
        correct = count_pivot.loc[mapping_name, protocol]
        total = total_pivot.loc[mapping_name, protocol]

        if pd.isna(pct) or pd.isna(correct) or pd.isna(total):
            continue

        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"{pct:.1f}%\n({int(correct)}/{int(total)})",
            ha="center",
            va="bottom",
            fontsize=12
        )

ax.set_xticks(x)
ax.set_xticklabels(["Single Protocol Observation", "Cross-protocol Observation"])
ax.set_ylabel("Accuracy of identifier linkings")
#ax.set_title(f"Percentage of correct linkings by mapping and protocol\n{SCENARIO_NAME}")
ax.yaxis.set_major_formatter(PercentFormatter(xmax=100))
ax.set_ylim(0, np.nanmax(plot_df["pct_correct"].to_numpy()) + 12)
ax.legend(frameon=False)
ax.grid(axis="y", linestyle="--", alpha=0.35)

fig.tight_layout()
fig.savefig(OUT_PNG, dpi=300, bbox_inches="tight")
fig.savefig(OUT_PDF, bbox_inches="tight")
#plt.show()

print(f"Saved: {OUT_PNG}")
print(f"Saved: {OUT_PDF}")
print(f"Saved: {OUT_CSV}")

 
 
    



