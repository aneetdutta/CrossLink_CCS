import os
import sys
import itertools
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any

import numpy as np
import pandas as pd
import polars as pl

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.sniffer import Sniffer
from modules.general import extract_orjson, str_to_bool


# =========================
# Environment / Config
# =========================
BLUETOOTH_RANGE = int(os.getenv("BLUETOOTH_RANGE"))
WIFI_RANGE = int(os.getenv("WIFI_RANGE"))
LTE_RANGE = int(os.getenv("LTE_RANGE"))
SNIFFER_PROCESSING_BATCH_SIZE = int(os.getenv("SNIFFER_PROCESSING_BATCH_SIZE"))
SCENARIO_NAME = os.getenv("SCENARIO_NAME")

ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))

ENABLE_PARTIAL_COVERAGE = str_to_bool(os.getenv("ENABLE_PARTIAL_COVERAGE", "false"))
LIMIT_USER_AFTER_USER_DATA = str_to_bool(os.getenv("LIMIT_USER_AFTER_USER_DATA", "false"))

BS_XY_CSV = os.getenv(
    "BS_XY_CSV",
    "data/opencellid_cells_demo_LTE_212_10_uniqueLoc_XY.csv"
)

# If your detected dataframe uses a different column name for protocol,
# add it here.
PROTOCOL_COL_CANDIDATES = [
    "protocol",
    "radio",
    "radio_type",
    "tech",
    "technology",
]


# =========================
# Helpers
# =========================
def normalize_cellid_series(s: pd.Series) -> pd.Series:
    """
    Convert cell ids to clean strings:
    2855    -> "2855"
    2855.0  -> "2855"
    """
    return (
        s.astype("string")
         .str.strip()
         .str.replace(r"\.0$", "", regex=True)
    )


def load_bs_lookup(bs_csv_path: str) -> pd.DataFrame:
    """
    Load base-station CSV and return:
    serving_cell_id, bs_x, bs_y, bs_range
    """
    bs_df = pd.read_csv(bs_csv_path)

    required_cols = {"cellid", "x", "y"}
    missing = required_cols - set(bs_df.columns)
    if missing:
        raise KeyError(
            f"Base-station CSV is missing required columns: {sorted(missing)}. "
            f"Found: {list(bs_df.columns)}"
        )

    if "range" not in bs_df.columns:
        bs_df["range"] = np.nan

    bs_df["cellid"] = normalize_cellid_series(bs_df["cellid"])
    bs_df["x"] = pd.to_numeric(bs_df["x"], errors="coerce")
    bs_df["y"] = pd.to_numeric(bs_df["y"], errors="coerce")
    bs_df["range"] = pd.to_numeric(bs_df["range"], errors="coerce").fillna(0.0)

    bs_df = bs_df.rename(columns={
        "cellid": "serving_cell_id",
        "x": "bs_x",
        "y": "bs_y",
        "range": "bs_range",
    })

    bs_df = bs_df.drop_duplicates(subset=["serving_cell_id"])

    return bs_df[["serving_cell_id", "bs_x", "bs_y", "bs_range"]]


def build_user_cell_lookup(raw_user_data_df: pl.DataFrame) -> pd.DataFrame:
    """
    Build a lookup from (timestep, user_id) -> serving_cell_id
    from the original user data.
    """
    required_cols = {"timestep", "user_id", "serving_cell_id"}
    missing = required_cols - set(raw_user_data_df.columns)
    if missing:
        raise KeyError(
            f"raw_user_data_df is missing required columns: {sorted(missing)}. "
            f"Found: {raw_user_data_df.columns}"
        )

    user_cell_df = (
        raw_user_data_df
        .select([
            pl.col("timestep"),
            pl.col("user_id"),
            pl.col("serving_cell_id").cast(pl.Utf8),
        ])
        .unique(subset=["timestep", "user_id"])
        .to_pandas()
    )

    user_cell_df["timestep"] = pd.to_numeric(
        user_cell_df["timestep"], errors="coerce"
    ).astype("Int64")
    user_cell_df["user_id"] = user_cell_df["user_id"].astype("string")
    user_cell_df["serving_cell_id"] = normalize_cellid_series(
        user_cell_df["serving_cell_id"]
    )

    return user_cell_df


def get_protocol_column(df: pd.DataFrame) -> str:
    for col in PROTOCOL_COL_CANDIDATES:
        if col in df.columns:
            return col

    raise KeyError(
        "Could not find protocol column in detected dataframe. "
        f"Tried: {PROTOCOL_COL_CANDIDATES}. "
        f"Available columns: {list(df.columns)}"
    )


def process_batch(
    batch: List[Dict[str, Any]],
    sniffers: List["Sniffer"],
    enable_bluetooth: bool = ENABLE_BLUETOOTH,
    enable_wifi: bool = ENABLE_WIFI,
    enable_lte: bool = ENABLE_LTE,
) -> List[Dict[str, Any]]:
    detected_rows = []

    for user_data in batch:
        user_location = [user_data["loc_x"], user_data["loc_y"]]

        for sniffer in sniffers:
            rows = sniffer.detect_raw_users(
                timestep=user_data["timestep"],
                user_id=user_data["user_id"],
                user_location=user_location,
                user_lte_id=user_data["lte_id"],
                user_wifi_id=user_data["wifi_id"],
                user_bluetooth_id=user_data["bluetooth_id"],
                transmit_ble=user_data["transmit_ble"],
                transmit_wifi=user_data["transmit_wifi"],
                transmit_lte=user_data["transmit_lte"],
            )

            if rows:
                detected_rows.extend(rows)

    return detected_rows


def batch_data(data: List[Dict[str, Any]], batch_size: int):
    print("batch", len(data), batch_size)
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]


def main():
    # =========================
    # Sniffer locations
    # =========================
    if not ENABLE_PARTIAL_COVERAGE:
        # coverage of 30
        sniffer_location = extract_orjson(
            "sniffer_location/full_coverage_wifi_sniffer_location.json"
        )
        print(len(sniffer_location["sniffer_location"]))
    else:
        print("Partial Coverage enabled")
        sniffer_location = extract_orjson("sniffer_location/partial_coverage.json")
        print(len(sniffer_location["sniffer_location"]))

    # =========================
    # Load raw user data
    # =========================
    if LIMIT_USER_AFTER_USER_DATA:
        raw_user_data_df = pl.read_csv(
            f"data/{SCENARIO_NAME}/user_data_limit_{SCENARIO_NAME}.csv"
        )
    else:
        raw_user_data_df = pl.read_csv(
            f"data/{SCENARIO_NAME}/user_data_{SCENARIO_NAME}.csv"
        )

    print(raw_user_data_df)

    raw_user_data = raw_user_data_df.to_dicts()

    # =========================
    # Build lookup tables
    # =========================
    user_cell_df = build_user_cell_lookup(raw_user_data_df)
    bs_lookup_df = load_bs_lookup(BS_XY_CSV)

    # =========================
    # Create sniffers
    # =========================
    sniffer_locs = sniffer_location["sniffer_location"]
    sniffers = [
        Sniffer(i, sniffer_loc, BLUETOOTH_RANGE, WIFI_RANGE, LTE_RANGE)
        for i, sniffer_loc in enumerate(sniffer_locs)
    ]

    # =========================
    # Process in parallel
    # =========================
    batches = batch_data(raw_user_data, SNIFFER_PROCESSING_BATCH_SIZE)

    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        results_iter = executor.map(
            process_batch,
            batches,
            itertools.repeat(sniffers),
        )
        detected_users = list(itertools.chain.from_iterable(results_iter))

    # =========================
    # Build final dataframe
    # =========================
    sniffed_file = f"data/{SCENARIO_NAME}/raw_sniffed_data_{SCENARIO_NAME}.csv"

    df = pd.DataFrame(detected_users)

    if df.empty:
        print("No detected users found. Saving empty dataframe.")
        df.to_csv(sniffed_file, index=False)
        print(f"Saved file to {sniffed_file}")
        return

    if "timestep" not in df.columns:
        raise KeyError(f"'timestep' not found in detected dataframe columns: {list(df.columns)}")
    if "user_id" not in df.columns:
        raise KeyError(f"'user_id' not found in detected dataframe columns: {list(df.columns)}")

    df["timestep"] = pd.to_numeric(df["timestep"], errors="coerce").astype("Int64")
    df["user_id"] = df["user_id"].astype("string")

    df = df.sort_values(by="timestep")

    # Existing distance: sniffer -> user
    required_dist_cols = {"sl_x", "sl_y", "ul_x", "ul_y"}
    missing_dist_cols = required_dist_cols - set(df.columns)
    if missing_dist_cols:
        raise KeyError(
            f"Detected dataframe is missing columns needed for distance calculation: "
            f"{sorted(missing_dist_cols)}. Found: {list(df.columns)}"
        )

    df["dist_S_U"] = np.hypot(
        df["sl_x"] - df["ul_x"],
        df["sl_y"] - df["ul_y"]
    ).astype(float)

    # Add serving_cell_id from original raw user data
    df = df.merge(
        user_cell_df,
        on=["timestep", "user_id"],
        how="left"
    )

    # Add base-station x/y/range using serving_cell_id <-> cellid
    df = df.merge(
        bs_lookup_df,
        on="serving_cell_id",
        how="left"
    )

    # LTE-only mask
    protocol_col = get_protocol_column(df)
    lte_mask = df[protocol_col].astype("string").str.upper().eq("LTE")

    # New columns
    df["dist_S_BS"] = np.nan   # sniffer -> base station
    df["dist_U_BS"] = np.nan   # user -> base station

    valid_lte = lte_mask & df["bs_x"].notna() & df["bs_y"].notna()

    df.loc[valid_lte, "dist_S_BS"] = np.hypot(
        df.loc[valid_lte, "sl_x"] - df.loc[valid_lte, "bs_x"],
        df.loc[valid_lte, "sl_y"] - df.loc[valid_lte, "bs_y"]
    )

    df.loc[valid_lte, "dist_U_BS"] = np.hypot(
        df.loc[valid_lte, "ul_x"] - df.loc[valid_lte, "bs_x"],
        df.loc[valid_lte, "ul_y"] - df.loc[valid_lte, "bs_y"]
    )

    print(df.head())
    print(f"Total rows: {len(df)}")
    print(f"Protocol column used: {protocol_col}")

    df.to_csv(sniffed_file, index=False)
    print(f"Saved file to the directory: {sniffed_file}")


if __name__ == "__main__":
    main()
