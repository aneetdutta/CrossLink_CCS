import os, sys
sys.path.append(os.getcwd())
from modules.general import *
''' Load the sumo_simulation result from mongodb '''
import pandas as pd
import polars as pl
from tqdm import tqdm
from modules.logger import MyLogger

def ensure_rchain_list(x):
    """
    If rchain is read back from CSV, it may be a string representation of a list.
    Convert it back to a Python list.
    """
    if isinstance(x, str):
        return ast.literal_eval(x)
    return x


def merge_intervals(intervals):
    """
    Merge inclusive intervals.
    intervals: list of (start, end)
    returns: merged list of (start, end)
    """
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
    """
    Total inclusive length of merged intervals.
    """
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
    print("-----")
    print(inter_id)
    print(rchain)

    min_start_timestep, max_last_timestep, protocol_ = id_timestep_data[inter_id][0], id_timestep_data[inter_id][1], id_protocol[inter_id]
    u = id_user_data[inter_id]
    print(u)

    fetch_inter_mapping_timesteps = id_data[id_data['id'].isin(rchain)]
    print(fetch_inter_mapping_timesteps)
    print("------")
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


import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch
import numpy as np
import ast

def safe_filename(text):
    return "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in str(text))


def ensure_rchain_is_list(df):
    """
    If rchain was loaded from CSV, it may be a string like "['id1', 'id2']".
    Convert it back to a real Python list.
    """
    if "rchain" not in df.columns:
        raise ValueError("multi_protocol_df does not contain an 'rchain' column.")

    if len(df) == 0:
        return df

    sample = df["rchain"].iloc[0]
    if isinstance(sample, str):
        df = df.copy()
        df["rchain"] = df["rchain"].apply(ast.literal_eval)

    return df


def plot_rchain_timing_diagrams(multi_protocol_df, id_data, folder_path, scenario_name):
    """
    Create:
    1. one PNG timing diagram per user
    2. one combined PDF with one page per user
    """

    multi_protocol_df = ensure_rchain_is_list(multi_protocol_df)

    # Color map
    protocol_colors = {
        "LTE": "tab:blue",
        "Bluetooth": "tab:orange",   # BLE
        "WiFi": "lightgray"
    }

    pdf_path = os.path.join(folder_path, f"rchain_timing_diagrams_{scenario_name}.pdf")

    with PdfPages(pdf_path) as pdf:
        for _, user_row in multi_protocol_df.iterrows():
            user_id = user_row["user_id"]
            selected_id = user_row["id"]
            rchain = user_row["rchain"]

            if not rchain:
                continue

            # Fetch all rows for IDs inside rchain
            chain_df = id_data[id_data["id"].isin(rchain)].copy()

            if chain_df.empty:
                continue

            # Preserve rchain order in the plot
            order_map = {identifier: i for i, identifier in enumerate(rchain)}
            chain_df["chain_order"] = chain_df["id"].map(order_map)

            # Optional protocol sort inside same order
            protocol_sort_map = {"LTE": 0, "Bluetooth": 1, "WiFi": 2}
            chain_df["protocol_order"] = chain_df["protocol"].map(protocol_sort_map).fillna(99)

            chain_df = chain_df.sort_values(
                ["chain_order", "protocol_order", "start_timestep", "last_timestep"]
            ).reset_index(drop=True)

            # Dynamic height based on number of identifiers
            fig_height = max(3, 0.55 * len(chain_df) + 1.5)
            fig, ax = plt.subplots(figsize=(15, fig_height))

            y_positions = np.arange(len(chain_df))
            y_labels = []

            for y, (_, rec) in zip(y_positions, chain_df.iterrows()):
                identifier = rec["id"]
                protocol = rec["protocol"]
                start = int(rec["start_timestep"])
                end = int(rec["last_timestep"])
                width = end - start + 1

                color = protocol_colors.get(protocol, "gray")

                ax.barh(
                    y=y,
                    width=width,
                    left=start,
                    height=0.72,
                    color=color,
                    edgecolor="black",
                    linewidth=0.8
                )

                proto_short = "BLE" if protocol == "Bluetooth" else protocol
                anchor_text = " (selected)" if identifier == selected_id else ""
                y_labels.append(f"{identifier} [{proto_short}]{anchor_text}")

            ax.set_yticks(y_positions)
            ax.set_yticklabels(y_labels, fontsize=8)
            ax.invert_yaxis()

            ax.set_xlabel("Timestep")
            ax.set_ylabel("Identifiers in rchain")
            ax.set_title(
                f"User: {user_id} | Selected ID: {selected_id} | "
                f"Privacy score: {user_row['privacy_score']:.4f}"
                if "privacy_score" in user_row
                else f"User: {user_id} | Selected ID: {selected_id}"
            )

            ax.grid(axis="x", linestyle="--", alpha=0.35)

            legend_handles = [
                Patch(facecolor="tab:blue", edgecolor="black", label="LTE"),
                Patch(facecolor="tab:orange", edgecolor="black", label="Bluetooth (BLE)")
            ]

            if (~chain_df["protocol"].isin(["LTE", "Bluetooth"])).any():
                legend_handles.append(
                    Patch(facecolor="lightgray", edgecolor="black", label="Other / WiFi")
                )

            ax.legend(handles=legend_handles, loc="upper right")
            fig.tight_layout()

            # Save PNG for this user
            png_path = os.path.join(
                folder_path,
                f"timing_{safe_filename(user_id)}_{scenario_name}.png"
            )
            fig.savefig(png_path, dpi=300, bbox_inches="tight")

            # Add page to combined PDF
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"Timing diagrams saved to: {folder_path}")
    print(f"Combined PDF saved to: {pdf_path}")
    
    
    
plot_rchain_timing_diagrams(
    multi_protocol_df=multi_protocol_df,
    id_data=id_data,
    folder_path=folder_path,
    scenario_name=SCENARIO_NAME
)


# =========================
# BLE / LTE share per user
# =========================

share_stats = multi_protocol_df["rchain"].apply(
    lambda rc: tracking_fraction_from_rchain(rc, id_data)
)

multi_protocol_df = pd.concat([multi_protocol_df, share_stats], axis=1)

# Save per-user stats
per_user_share_cols = [
    "user_id",
    "id",
    "protocol",
    "ideal_duration",
    "start_timestep",
    "last_timestep",
    "total_time",
    "privacy_score",
    "ble_id_count",
    "lte_id_count",
    "ble_tracked_time",
    "lte_tracked_time",
    "any_tracking_time",
    "ble_total_share",
    "lte_total_share",
    "ble_share_of_protocol_time",
    "lte_share_of_protocol_time",
    "rchain"
]

per_user_share_df = multi_protocol_df[per_user_share_cols].copy()
per_user_share_df.to_csv(
    os.path.join(folder_path, f"per_user_ble_lte_share_{SCENARIO_NAME}.csv"),
    index=False
)

print(
    per_user_share_df[
        [
            "user_id",
            "ble_tracked_time",
            "lte_tracked_time",
            "any_tracking_time",
            "ble_total_share",
            "lte_total_share",
            "ble_share_of_protocol_time",
            "lte_share_of_protocol_time"
        ]
    ].sort_values("user_id").to_string(index=False)
)

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# --------------------------------------------------------
# Two-panel figure: histogram + boxplot for BLE share
# Assumes per_user_share_df has column: ble_share_of_protocol_time
# --------------------------------------------------------
plot_df = per_user_share_df.dropna(subset=["ble_share_of_protocol_time"]).copy()
x = plot_df["ble_share_of_protocol_time"].astype(float).to_numpy()
x = x[np.isfinite(x)]

if len(x) == 0:
    print("No valid BLE share values found.")
else:
    # Summary statistics
    q1, median, q3 = np.quantile(x, [0.25, 0.50, 0.75])
    mean_val = x.mean()
    iqr = q3 - q1

    # Freedman-Diaconis bin rule, clamped for readability
    if len(x) > 1 and iqr > 0:
        bin_width = 2 * iqr / (len(x) ** (1 / 3))
    else:
        bin_width = 0.05

    if x.max() > x.min():
        n_bins = int(np.ceil((x.max() - x.min()) / bin_width))
    else:
        n_bins = 10

    n_bins = max(8, min(n_bins, 16))
    bins = np.linspace(0, 1, n_bins + 1)

    # Histogram as share of users, not density
    weights = np.ones_like(x) / len(x)

    fig = plt.figure(figsize=(8.5, 6.5))
    gs = fig.add_gridspec(2, 1, height_ratios=[4, 1], hspace=0.05)

    ax_hist = fig.add_subplot(gs[0])
    ax_box = fig.add_subplot(gs[1], sharex=ax_hist)

    # Top panel: histogram
    ax_hist.hist(
        x,
        bins=bins,
        weights=weights,
        edgecolor="black",
        linewidth=0.8
    )

    # Shade IQR region
    ax_hist.axvspan(q1, q3, alpha=0.12, label="IQR")

    # Reference lines on both panels
    for ax in (ax_hist, ax_box):
        ax.axvline(0.50, linestyle="--", linewidth=1.2, label="BLE = LTE" if ax is ax_hist else None)
        ax.axvline(mean_val, linestyle=":", linewidth=1.5, label=f"Mean = {mean_val:.3f}" if ax is ax_hist else None)
        ax.axvline(median, linestyle="-.", linewidth=1.5, label=f"Median = {median:.3f}" if ax is ax_hist else None)

    # Bottom panel: horizontal boxplot
    ax_box.boxplot(
        x,
        vert=False,
        widths=0.5,
        showfliers=False
    )

    # Axis formatting
    ax_hist.set_xlim(0, 1)
    ax_box.set_xlim(0, 1)

    xticks = [0.0, 0.25, 0.50, 0.75, 1.0]
    ax_box.set_xticks(xticks)
    ax_hist.set_xticks(xticks)

    ax_box.xaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    ax_hist.xaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))
    ax_hist.yaxis.set_major_formatter(PercentFormatter(xmax=1.0, decimals=0))

    plt.setp(ax_hist.get_xticklabels(), visible=False)

    ax_hist.set_ylabel("Share of users")
    ax_box.set_xlabel("BLE share of total BLE+LTE tracking time")
    ax_box.set_yticks([])

    ax_hist.set_title(f"Distribution of BLE tracking share across users - {SCENARIO_NAME}")

    ax_hist.grid(axis="y", linestyle="--", alpha=0.35)
    ax_box.grid(axis="x", linestyle="--", alpha=0.25)

    # Summary box
    summary_text = (
        f"n = {len(x)}\n"
        f"mean = {mean_val:.3f}\n"
        f"median = {median:.3f}\n"
        f"IQR = [{q1:.3f}, {q3:.3f}]"
    )
    ax_hist.text(
        0.98, 0.98,
        summary_text,
        transform=ax_hist.transAxes,
        ha="right",
        va="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9)
    )

    ax_hist.legend(frameon=False)

    fig.tight_layout()

    out_path = os.path.join(folder_path, f"ble_share_hist_boxplot_{SCENARIO_NAME}.pdf")
    plt.savefig(out_path, bbox_inches="tight")
    plt.show()

    print(f"Saved plot to: {out_path}")
    
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
print(summary_df)


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
plt.show()

print(f"Saved: {OUT_PNG}")
print(f"Saved: {OUT_PDF}")
print(f"Saved: {OUT_CSV}")
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, ConnectionPatch
from matplotlib.lines import Line2D


def _short_id(text, max_len=32):
    text = str(text)
    if len(text) <= max_len:
        return text
    keep = max_len // 2 - 2
    return text[:keep] + "..." + text[-keep:]


def plot_selected_chain_faceted(
    selected_row,
    id_data,
    inter_data,
    chained_intra,
    chained_dict,
    intramap_single_raw,
    intramap_filtered_raw,
    id_user_data,
    user_data,
    folder_path,
    scenario_name
):
    """
    Cleaner faceted version of the reconstructed-chain plot.

    Requires:
        build_roles_and_edges_exact(...)
    from the previous code block.
    """
    user_id = selected_row["user_id"]
    selected_id = str(selected_row["id"])

    rchain, role_map, edges = build_roles_and_edges_exact(
        selected_row=selected_row,
        inter_data=inter_data,
        chained_intra=chained_intra,
        chained_dict=chained_dict,
        intramap_single_raw=intramap_single_raw,
        intramap_filtered_raw=intramap_filtered_raw,
        id_user_data=id_user_data,
        user_data=user_data
    )

    if not rchain:
        print(f"No rchain found for user {user_id}")
        return

    chain_df = id_data[id_data["id"].isin(rchain)].copy()
    if chain_df.empty:
        print(f"No matching rows in id_data for user {user_id}")
        return

    # Preserve exact rchain ordering from reconstruction
    order_map = {identifier: i for i, identifier in enumerate(rchain)}

    protocol_display_map = {
        "Bluetooth": "BLE",
        "LTE": "LTE",
        "WiFi": "WiFi"
    }
    protocol_order = {"BLE": 0, "LTE": 1, "WiFi": 2}
    role_order = {
        "selected": 0,
        "own_intra": 1,
        "crosslink_seed": 2,
        "crosslink_intra": 3
    }

    chain_df["protocol_display"] = chain_df["protocol"].map(protocol_display_map).fillna(chain_df["protocol"])
    chain_df["chain_order"] = chain_df["id"].map(order_map)
    chain_df["role_order"] = chain_df["id"].map(lambda x: role_order.get(role_map.get(x, "own_intra"), 99))

    chain_df = chain_df.sort_values(
        ["protocol_display", "role_order", "chain_order", "start_timestep"]
    ).reset_index(drop=True)

    protocols_present = [
        p for p in ["BLE", "LTE", "WiFi"]
        if p in set(chain_df["protocol_display"])
    ]

    if not protocols_present:
        print("No protocols present in selected chain.")
        return

    protocol_colors = {
        "BLE": "#E68613",
        "LTE": "#3B75AF",
        "WiFi": "#BDBDBD"
    }

    role_markers = {
        "selected": "*",
        "own_intra": "o",
        "crosslink_seed": "D",
        "crosslink_intra": "s"
    }

    role_labels = {
        "selected": "selected anchor",
        "own_intra": "own intra-chain",
        "crosslink_seed": "direct crosslink seed",
        "crosslink_intra": "crosslink intra-chain"
    }

    edge_styles = {
        "intra_single_ok": dict(color="#228833", linestyle="-", linewidth=1.8),
        "intra_filtered_only_ok": dict(color="#7A3EB1", linestyle="--", linewidth=1.8),
        "intra_unresolved": dict(color="#CC3311", linestyle=":", linewidth=1.8),
        "crosslink": dict(color="black", linestyle="-", linewidth=2.0),
    }

    # Panel heights based on number of IDs per protocol
    height_ratios = []
    for p in protocols_present:
        n = max(1, len(chain_df[chain_df["protocol_display"] == p]))
        height_ratios.append(max(1.3, 0.42 * n))

    fig, axes = plt.subplots(
        nrows=len(protocols_present),
        ncols=1,
        sharex=True,
        figsize=(15.5, sum(height_ratios) + 1.8),
        gridspec_kw={"height_ratios": height_ratios}
    )

    if len(protocols_present) == 1:
        axes = [axes]

    x_min = int(chain_df["start_timestep"].min())
    x_max = int(chain_df["last_timestep"].max())
    span = max(1, x_max - x_min)
    left_margin = max(int(0.16 * span), 120)
    right_margin = max(int(0.04 * span), 25)
    node_x = x_min - 0.60 * left_margin

    coord_map = {}

    for ax, protocol_name in zip(axes, protocols_present):
        sub = chain_df[chain_df["protocol_display"] == protocol_name].copy().reset_index(drop=True)

        y_positions = np.arange(len(sub))

        # light background for node lane
        ax.axvspan(x_min - left_margin, x_min - 0.12 * left_margin, color="#F7F7F7", zorder=0)

        labels = []
        for y, (_, rec) in zip(y_positions, sub.iterrows()):
            identifier = rec["id"]
            role = role_map.get(identifier, "own_intra")
            start = int(rec["start_timestep"])
            end = int(rec["last_timestep"])
            width = end - start + 1

            # time bar
            ax.barh(
                y=y,
                width=width,
                left=start,
                height=0.68,
                color=protocol_colors.get(protocol_name, "gray"),
                edgecolor="black",
                linewidth=1.6 if role == "selected" else 0.8,
                alpha=0.90,
                zorder=2
            )

            # node marker in separate left lane
            ax.scatter(
                node_x,
                y,
                s=180 if role == "selected" else 90,
                marker=role_markers.get(role, "o"),
                color=protocol_colors.get(protocol_name, "gray"),
                edgecolors="black",
                linewidths=1.0,
                zorder=4
            )

            coord_map[identifier] = {"ax": ax, "x": node_x, "y": y}

            labels.append(_short_id(identifier, max_len=30))

        ax.set_yticks(y_positions)
        ax.set_yticklabels(labels, fontsize=8)
        ax.invert_yaxis()

        ax.set_ylabel(protocol_name, rotation=0, labelpad=28, fontsize=10, fontweight="bold", va="center")
        ax.grid(axis="x", linestyle="--", alpha=0.22)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    # Draw mapping arrows between node markers
    for edge in edges:
        src = edge["src"]
        dst = edge["dst"]
        tag = edge["tag"]

        if src not in coord_map or dst not in coord_map:
            continue

        src_meta = coord_map[src]
        dst_meta = coord_map[dst]
        style = edge_styles[tag]

        connector = ConnectionPatch(
            xyA=(src_meta["x"], src_meta["y"]),
            coordsA=src_meta["ax"].transData,
            xyB=(dst_meta["x"], dst_meta["y"]),
            coordsB=dst_meta["ax"].transData,
            arrowstyle="->",
            mutation_scale=10,
            shrinkA=2,
            shrinkB=2,
            color=style["color"],
            linestyle=style["linestyle"],
            linewidth=style["linewidth"],
            zorder=3
        )
        fig.add_artist(connector)

    # Shared x formatting
    for ax in axes:
        ax.set_xlim(x_min - left_margin, x_max + right_margin)

    axes[-1].set_xlabel("Timestep", fontsize=10)

    # Title
    if "privacy_score" in selected_row.index:
        fig.suptitle(
            f"User: {user_id} | Selected ID: {selected_id} | "
            f"Privacy score: {selected_row['privacy_score']:.4f}",
            y=0.995,
            fontsize=12
        )
    else:
        fig.suptitle(
            f"User: {user_id} | Selected ID: {selected_id}",
            y=0.995,
            fontsize=12
        )

    # Legend
    legend_handles = [
    Patch(facecolor=protocol_colors["BLE"], edgecolor="black", label="BLE"),
    Patch(facecolor=protocol_colors["LTE"], edgecolor="black", label="LTE"),
    Patch(facecolor=protocol_colors["WiFi"], edgecolor="black", label="WiFi"),
    Line2D([0], [0], marker="*", color="w", markerfacecolor="gray", markeredgecolor="black",
           markersize=11, label="selected anchor"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="gray", markeredgecolor="black",
           markersize=8, label="own intra-chain"),
    Line2D([0], [0], marker="D", color="w", markerfacecolor="gray", markeredgecolor="black",
           markersize=8, label="direct crosslink seed"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor="gray", markeredgecolor="black",
           markersize=8, label="crosslink intra-chain"),
    Line2D([0], [0], color="#228833", linestyle="-", linewidth=1.8, label="intra: correct in single"),
    Line2D([0], [0], color="#7A3EB1", linestyle="--", linewidth=1.8, label="intra: only correct in filtered"),
    Line2D([0], [0], color="#CC3311", linestyle=":", linewidth=1.8, label="intra: unresolved"),
    Line2D([0], [0], color="black", linestyle="-", linewidth=2.0, label="direct crosslink"),
]

    fig.legend(
        handles=legend_handles,
        loc="upper center",
        ncol=5,
        frameon=False,
        bbox_to_anchor=(0.5, 0.955),
        fontsize=9
    )

    fig.tight_layout(rect=[0, 0, 1, 0.90])

    out_path = os.path.join(
        folder_path,
        f"timing_faceted_{user_id}_{scenario_name}.png"
    )
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Saved: {out_path}")
    
def load_npy_dict(path):
    obj = np.load(path, allow_pickle=True)
    try:
        return obj.item()
    except Exception:
        return obj


def ensure_list(x):
    if isinstance(x, str):
        return ast.literal_eval(x)
    return x


def normalize_mapping(mapping):
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
        for item in mapping:
            if item is None:
                continue
            if isinstance(item, float) and np.isnan(item):
                continue
            if item == "":
                continue
            out.append(str(item))
        return out

    return [str(mapping)]


def dedupe_preserve_order(seq):
    return list(dict.fromkeys(seq))


def same_user(src_id, dst_id, id_user_data):
    return (
        src_id in id_user_data
        and dst_id in id_user_data
        and id_user_data[src_id] == id_user_data[dst_id]
    )


def singleton_points_to(mapping_dict, src_id, dst_id):
    targets = normalize_mapping(mapping_dict.get(src_id, []))
    return len(targets) == 1 and targets[0] == dst_id


def classify_directed_intra_edge(a, b, intramap_single_raw, intramap_filtered_raw, id_user_data):
    """
    For adjacent IDs a and b inside a chain, return:
        (src, dst, tag)

    tag is one of:
        - intra_single_ok
        - intra_filtered_only_ok
        - intra_unresolved

    This checks both directions because chain adjacency does not always tell you
    which way the original singleton mapping points.
    """

    # Correct already in filtered_intramap_single
    if singleton_points_to(intramap_single_raw, a, b) and same_user(a, b, id_user_data):
        return a, b, "intra_single_ok"
    if singleton_points_to(intramap_single_raw, b, a) and same_user(b, a, id_user_data):
        return b, a, "intra_single_ok"

    # Not correct in single, but correct in filtered_intramap
    if singleton_points_to(intramap_filtered_raw, a, b) and same_user(a, b, id_user_data):
        return a, b, "intra_filtered_only_ok"
    if singleton_points_to(intramap_filtered_raw, b, a) and same_user(b, a, id_user_data):
        return b, a, "intra_filtered_only_ok"

    # Unresolved: preserve a direction if one exists in either file
    if singleton_points_to(intramap_filtered_raw, a, b) or singleton_points_to(intramap_single_raw, a, b):
        return a, b, "intra_unresolved"
    if singleton_points_to(intramap_filtered_raw, b, a) or singleton_points_to(intramap_single_raw, b, a):
        return b, a, "intra_unresolved"

    # Final fallback: use chain order direction
    return a, b, "intra_unresolved"


def set_role(role_map, identifier, new_role):
    priority = {
        "crosslink_intra": 0,
        "own_intra": 1,
        "crosslink_seed": 2,
        "selected": 3,
    }
    old_role = role_map.get(identifier)
    if old_role is None or priority[new_role] > priority[old_role]:
        role_map[identifier] = new_role
    
def build_roles_and_edges_exact(
    selected_row,
    inter_data,
    chained_intra,
    chained_dict,
    intramap_single_raw,
    intramap_filtered_raw,
    id_user_data,
    user_data
):
    """
    Returns:
        rchain
        role_map
        edges

    roles:
        - selected
        - own_intra
        - crosslink_seed
        - crosslink_intra

    edge tags:
        - crosslink
        - intra_single_ok
        - intra_filtered_only_ok
        - intra_unresolved
    """
    rebuilt = rebuild_selected_sources_exact(
        selected_row=selected_row,
        inter_data=inter_data,
        chained_intra=chained_intra,
        chained_dict=chained_dict,
        id_user_data=id_user_data,
        user_data=user_data
    )

    selected_id = rebuilt["selected_id"]
    rchain = rebuilt["rchain"]
    own_chain = rebuilt["own_chain"]
    crosslink_chains = rebuilt["crosslink_chains"]
    raw_crosslink_targets = rebuilt["raw_crosslink_targets"]

    rchain_set = set(rchain)
    role_map = {}
    edges = []
    seen_edges = set()

    def add_edge(src, dst, tag):
        key = (src, dst, tag)
        if src in rchain_set and dst in rchain_set and key not in seen_edges:
            seen_edges.add(key)
            edges.append({"src": src, "dst": dst, "tag": tag})

    # Roles: own chain
    set_role(role_map, selected_id, "selected")
    for identifier in own_chain:
        if identifier == selected_id:
            set_role(role_map, identifier, "selected")
        else:
            set_role(role_map, identifier, "own_intra")

    # Intra arrows for own chain
    for i in range(len(own_chain) - 1):
        a = own_chain[i]
        b = own_chain[i + 1]
        src, dst, tag = classify_directed_intra_edge(
            a, b,
            intramap_single_raw,
            intramap_filtered_raw,
            id_user_data
        )
        add_edge(src, dst, tag)

    # Crosslink chains
    for chain in crosslink_chains:
        if not chain:
            continue

        seeds = [m for m in raw_crosslink_targets if m in chain]

        # fallback if no raw target survives directly in the chain
        if not seeds:
            seeds = [chain[0]]

        # mark seeds
        for seed in seeds:
            if seed != selected_id:
                set_role(role_map, seed, "crosslink_seed")
                add_edge(selected_id, seed, "crosslink")

        # mark the rest of the chain
        for identifier in chain:
            if identifier == selected_id:
                set_role(role_map, identifier, "selected")
            elif identifier not in seeds:
                set_role(role_map, identifier, "crosslink_intra")

        # intra arrows inside this crosslink chain
        for i in range(len(chain) - 1):
            a = chain[i]
            b = chain[i + 1]
            src, dst, tag = classify_directed_intra_edge(
                a, b,
                intramap_single_raw,
                intramap_filtered_raw,
                id_user_data
            )
            add_edge(src, dst, tag)

    return rchain, role_map, edges
def rebuild_selected_sources_exact(
    selected_row,
    inter_data,
    chained_intra,
    chained_dict,
    id_user_data,
    user_data
):
    """
    Replays the reconstruction logic for one selected row:

        chain1 = chained_dict[selected_id]
        chain_ = inter_intra_mapper(mapping, chained_intra)
        chain_.append(chain1)
        keep only chains fully contained in the user's IDs

    Returns:
        selected_id
        rchain
        own_chain
        crosslink_chains
        raw_crosslink_targets
    """
    selected_id = str(selected_row["id"])
    user_id = id_user_data[selected_id]
    valid_ids = set(user_data[user_id])

    mapping_raw = inter_data.get(selected_id, [])
    raw_crosslink_targets = normalize_mapping(mapping_raw)

    own_chain = normalize_mapping(chained_dict.get(selected_id, []))
    crosslink_chains = inter_intra_mapper(mapping_raw, chained_intra) or []
    crosslink_chains = [normalize_mapping(c) for c in crosslink_chains]

    accepted_crosslink_chains = []
    for chain in crosslink_chains:
        if not chain:
            continue
        if set(chain).issubset(valid_ids):
            accepted_crosslink_chains.append(dedupe_preserve_order(chain))

    accepted_own_chain = []
    if own_chain and set(own_chain).issubset(valid_ids):
        accepted_own_chain = dedupe_preserve_order(own_chain)

    # Preserve final selected row's rchain ordering if present
    stored_rchain = []
    if "rchain" in selected_row.index and selected_row["rchain"] is not None:
        stored_rchain = dedupe_preserve_order(ensure_list(selected_row["rchain"]))

    rebuilt_union = dedupe_preserve_order(
        [x for chain in accepted_crosslink_chains for x in chain] + accepted_own_chain
    )

    if stored_rchain:
        rebuilt_set = set(rebuilt_union)
        accepted_crosslink_chains = [
            [x for x in chain if x in rebuilt_set and x in stored_rchain]
            for chain in accepted_crosslink_chains
        ]
        accepted_crosslink_chains = [c for c in accepted_crosslink_chains if c]

        accepted_own_chain = [x for x in accepted_own_chain if x in stored_rchain]

        rchain = [x for x in stored_rchain if x in rebuilt_set]
    else:
        rchain = rebuilt_union

    return {
        "selected_id": selected_id,
        "rchain": rchain,
        "own_chain": accepted_own_chain,
        "crosslink_chains": accepted_crosslink_chains,
        "raw_crosslink_targets": raw_crosslink_targets,
    }


    
TARGET_USER = "P_1-1-pt_150"   # change if needed

selected_row = multi_protocol_df.loc[multi_protocol_df["user_id"] == TARGET_USER].iloc[0]

plot_selected_chain_faceted(
    selected_row=selected_row,
    id_data=id_data,
    inter_data=inter_data,
    chained_intra=chained_intra,
    chained_dict=chained_dict,
    intramap_single_raw=intramap_single,
    intramap_filtered_raw=intramap_filtered,
    id_user_data=id_user_data,
    user_data=user_data,
    folder_path=folder_path,
    scenario_name=SCENARIO_NAME
)

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

def tracking_protocol_stats_from_rchain(rchain, id_data):
    """
    For one reconstructed chain:
      - compute total union tracking time across BLE/WiFi/LTE
      - compute per-protocol covered time
      - compute per-protocol shares

    Note:
      BLE/WiFi/LTE times can overlap, so
      ble_tracked_time + wifi_tracked_time + lte_tracked_time
      may be larger than any_tracking_time.
    """
    rchain = ensure_rchain_list(rchain)

    empty_result = pd.Series({
        "ble_id_count": 0,
        "wifi_id_count": 0,
        "lte_id_count": 0,
        "ble_tracked_time": 0,
        "wifi_tracked_time": 0,
        "lte_tracked_time": 0,
        "any_tracking_time": 0,
        "ble_total_share": np.nan,
        "wifi_total_share": np.nan,
        "lte_total_share": np.nan,
        "ble_share_of_protocol_time": np.nan,
        "wifi_share_of_protocol_time": np.nan,
        "lte_share_of_protocol_time": np.nan,
    })

    if not rchain:
        return empty_result

    chain_df = id_data[id_data["id"].isin(rchain)].copy()
    if chain_df.empty:
        return empty_result

    chain_df["protocol_norm"] = chain_df["protocol"].replace({
        "Bluetooth": "BLE",
        "BLE": "BLE",
        "LTE": "LTE",
        "WiFi": "WiFi",
        "Wi-Fi": "WiFi",
        "wifi": "WiFi",
    })

    def _covered_time(df_sub):
        if df_sub.empty:
            return 0
        intervals = merge_intervals(
            list(zip(df_sub["start_timestep"].astype(int), df_sub["last_timestep"].astype(int)))
        )
        return interval_length(intervals)

    ble_df = chain_df[chain_df["protocol_norm"] == "BLE"].copy()
    wifi_df = chain_df[chain_df["protocol_norm"] == "WiFi"].copy()
    lte_df = chain_df[chain_df["protocol_norm"] == "LTE"].copy()
    tracked_df = chain_df[chain_df["protocol_norm"].isin(["BLE", "WiFi", "LTE"])].copy()

    ble_time = _covered_time(ble_df)
    wifi_time = _covered_time(wifi_df)
    lte_time = _covered_time(lte_df)
    any_time = _covered_time(tracked_df)

    protocol_sum = ble_time + wifi_time + lte_time

    return pd.Series({
        "ble_id_count": ble_df["id"].nunique(),
        "wifi_id_count": wifi_df["id"].nunique(),
        "lte_id_count": lte_df["id"].nunique(),
        "ble_tracked_time": ble_time,
        "wifi_tracked_time": wifi_time,
        "lte_tracked_time": lte_time,
        "any_tracking_time": any_time,

        # share relative to total union tracking time
        "ble_total_share": ble_time / any_time if any_time > 0 else np.nan,
        "wifi_total_share": wifi_time / any_time if any_time > 0 else np.nan,
        "lte_total_share": lte_time / any_time if any_time > 0 else np.nan,

        # share relative to sum of protocol-specific covered times
        "ble_share_of_protocol_time": ble_time / protocol_sum if protocol_sum > 0 else np.nan,
        "wifi_share_of_protocol_time": wifi_time / protocol_sum if protocol_sum > 0 else np.nan,
        "lte_share_of_protocol_time": lte_time / protocol_sum if protocol_sum > 0 else np.nan,
    })


def build_per_user_protocol_duration_df(multi_protocol_df, id_data):
    """
    Build one row per user with reconstructed-chain protocol duration stats.
    """
    core_cols = [
        col for col in [
            "user_id", "id", "protocol", "privacy_score",
            "start_timestep", "last_timestep", "total_time", "rchain"
        ]
        if col in multi_protocol_df.columns
    ]

    base_df = multi_protocol_df[core_cols].copy()

    stats_df = base_df["rchain"].apply(
        lambda rc: tracking_protocol_stats_from_rchain(rc, id_data)
    )

    out_df = pd.concat([base_df.reset_index(drop=True), stats_df.reset_index(drop=True)], axis=1)
    return out_df


def plot_per_user_protocol_duration_distribution(
    per_user_protocol_df,
    folder_path,
    scenario_name,
    sort_by="any_tracking_time"
):
    """
    One row per user:
      - background bar = total union tracking time
      - thin overlay bars = BLE / WiFi / LTE covered times
    """
    plot_df = per_user_protocol_df.copy()

    if sort_by in plot_df.columns:
        plot_df = plot_df.sort_values(sort_by, ascending=False).reset_index(drop=True)
    else:
        plot_df = plot_df.sort_values("user_id").reset_index(drop=True)

    if plot_df.empty:
        print("No users available for plotting.")
        return

    y = np.arange(len(plot_df))
    max_total = float(plot_df["any_tracking_time"].fillna(0).max())

    fig_height = max(6, 0.34 * len(plot_df) + 1.8)
    fig, ax = plt.subplots(figsize=(12.5, fig_height))

    # Background total-duration bar
    ax.barh(
        y,
        plot_df["any_tracking_time"].fillna(0),
        height=0.72,
        color="#EEEEEE",
        edgecolor="black",
        linewidth=0.7,
        zorder=1
    )

    # Slim overlay bars for each protocol
    proto_specs = [
        ("ble_tracked_time", "BLE", "#E68613", -0.22),
        ("wifi_tracked_time", "WiFi", "#BDBDBD", 0.00),
        ("lte_tracked_time", "LTE", "#3B75AF", 0.22),
    ]

    for col, label, color, y_shift in proto_specs:
        ax.barh(
            y + y_shift,
            plot_df[col].fillna(0),
            height=0.16,
            color=color,
            edgecolor="none",
            zorder=3,
            label=label
        )

    # User labels
    ax.set_yticks(y)
    ax.set_yticklabels(plot_df["user_id"].astype(str), fontsize=8)
    ax.invert_yaxis()

    ax.set_xlabel("Tracked duration in reconstructed chain (timesteps)")
    ax.set_ylabel("User")
    ax.set_title(f"Per-user reconstructed tracking duration by protocol\n{scenario_name}")

    ax.grid(axis="x", linestyle="--", alpha=0.35, zorder=0)

    # Annotate total duration at the right of each row
    x_pad = max(3, 0.01 * max_total) if max_total > 0 else 1
    for i, (_, rec) in enumerate(plot_df.iterrows()):
        total_val = int(rec["any_tracking_time"]) if pd.notna(rec["any_tracking_time"]) else 0
        ax.text(
            total_val + x_pad,
            i,
            f"T={total_val}",
            va="center",
            ha="left",
            fontsize=8
        )

    # Manual legend
    legend_handles = [
        Patch(facecolor="#EEEEEE", edgecolor="black", label="Total tracked duration"),
        Patch(facecolor="#E68613", edgecolor="none", label="BLE covered time"),
        Patch(facecolor="#BDBDBD", edgecolor="none", label="WiFi covered time"),
        Patch(facecolor="#3B75AF", edgecolor="none", label="LTE covered time"),
    ]
    ax.legend(handles=legend_handles, frameon=False, loc="lower right")

    # Important note about overlap
    note = (
        "Note: BLE, WiFi, and LTE covered times may overlap in the same timesteps, "
        "so their sum can exceed the total tracked duration."
    )
    ax.text(
        0.01,
        0.01,
        note,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=8
    )

    ax.set_xlim(0, max_total * 1.18 if max_total > 0 else 1)

    fig.tight_layout()

    out_csv = os.path.join(folder_path, f"per_user_protocol_duration_{scenario_name}.csv")
    out_png = os.path.join(folder_path, f"per_user_protocol_duration_{scenario_name}.png")
    out_pdf = os.path.join(folder_path, f"per_user_protocol_duration_{scenario_name}.pdf")

    plot_df.to_csv(out_csv, index=False)
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, bbox_inches="tight")
    plt.show()

    print(f"Saved: {out_csv}")
    print(f"Saved: {out_png}")
    print(f"Saved: {out_pdf}")


# ----------------------------------------------------
# Build per-user protocol stats and plot
# Paste this after multi_protocol_df is ready
# ----------------------------------------------------
per_user_protocol_df = build_per_user_protocol_duration_df(
    multi_protocol_df=multi_protocol_df,
    id_data=id_data
)

plot_per_user_protocol_duration_distribution(
    per_user_protocol_df=per_user_protocol_df,
    folder_path=folder_path,
    scenario_name=SCENARIO_NAME,
    sort_by="any_tracking_time"
)
