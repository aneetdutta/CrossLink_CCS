#!/usr/bin/env python3


from pathlib import Path
from typing import Final

import numpy as np
import pandas as pd



OUTPUT_ROOT: Final[Path] = Path("./output/data/example_scenario/")
DATA_ROOT: Final[Path] = Path("./data")
OUTFILES: Final[Path] = Path("./output/data")


RADIUS_M: Final[float] = 350.0
CHUNK_SIZE: Final[int] = 1_000_000

OUTPUT_SOURCE: Final[dict[str, Path]] = {
    "Baseline": (
        OUTFILES
        / "scenario_result_512_sumo_all1"
        / "multi_protocol_scenario_result_512_sumo_all1.csv"
    ),
    "PATCH": (
        OUTFILES
        / "scenario_result_512_sumo_partial"
        / "multi_protocol_scenario_result_512_sumo_partial.csv"
    ),
    "MOB": (
        OUTFILES
        / "scenario_partial_512_sumo_user1"
        / "multi_protocol_scenario_partial_512_sumo_user1.csv"
    ),
    "RAND": (
        OUTFILES
        / "scenario_partial_512_sumo_timestrategic"
        / "multi_protocol_scenario_partial_512_sumo_timestrategic.csv"
    ),
        



}



SCENARIOS: Final[dict[str, Path]] = {
    "Baseline": (
        DATA_ROOT
        / "scenario_result_512_sumo_all1"
        / "user_data_scenario_result_512_sumo_all1.csv"
    ),
    "PATCH": (
        DATA_ROOT
        / "scenario_result_512_sumo_partial"
        / "user_data_scenario_result_512_sumo_partial.csv"
    ),
    "MOB": (
        DATA_ROOT
        / "scenario_partial_512_sumo_user1"
        / "user_data_scenario_partial_512_sumo_user1.csv"
    ),
    "RAND": (
        DATA_ROOT
        / "scenario_partial_512_sumo_timestrategic"
        / "user_data_scenario_partial_512_sumo_timestrategic.csv"
    ),
}

for scenario, csv_file in OUTPUT_SOURCE.items():
    privacy_files= csv_file




def compute_start_points_chunked(input_csv, chunk_size=CHUNK_SIZE):

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive.")

    columns = ["user_id", "timestep", "loc_x", "loc_y"]
    best = {}

    for chunk in pd.read_csv(
        input_csv,
        usecols=columns,
        dtype={
            "user_id": "string",
            "timestep": "float64",
            "loc_x": "float64",
            "loc_y": "float64",
        },
        chunksize=chunk_size,
    ):
        chunk["user_id"] = chunk["user_id"].str.strip()
        chunk = chunk.dropna(subset=columns)
        chunk = chunk[chunk["user_id"] != ""]
        if chunk.empty:
            continue
        if not np.isfinite(chunk[["timestep", "loc_x", "loc_y"]].to_numpy()).all():
            raise ValueError(f"Infinite timestep or coordinate in {input_csv}")

        idx = chunk.groupby("user_id")["timestep"].idxmin()
        for uid, timestep, x, y in chunk.loc[idx, columns].itertuples(
            index=False, name=None
        ):
            previous = best.get(uid)
            if previous is None or timestep < previous[0]:
                best[uid] = (timestep, x, y)

    return (
        pd.DataFrame(
            [(uid, *point) for uid, point in best.items()],
            columns=["user_id", "timestep", "start_x", "start_y"],
        )
        .sort_values("user_id")
        .reset_index(drop=True)
    )


def radius_neighbors(coords, radius):

    if not np.isfinite(radius) or radius < 0:
        raise ValueError("radius must be finite and non-negative.")

    try:
        from scipy.spatial import cKDTree
    except ImportError:

        neighbors = []
        for center in coords:
            distances = np.hypot(*(coords - center).T)
            neighbors.append(np.flatnonzero(distances <= radius).tolist())
    else:
        tree = cKDTree(coords)
        neighbors = tree.query_ball_point(coords, r=radius)

    counts = np.array([len(indices) for indices in neighbors], dtype=int)
    return neighbors, counts


def find_largest_cluster(start_df, radius):

    if start_df.empty:
        raise ValueError("No valid start points found.")

    coords = start_df[["start_x", "start_y"]].to_numpy(dtype=float)
    neighbors, counts = radius_neighbors(coords, radius)
    max_count = int(counts.max())
    best_idxs = np.flatnonzero(counts == max_count)

    tied_centers = start_df.iloc[best_idxs].copy()
    tied_centers.insert(0, "radius_m", radius)
    tied_centers.insert(1, "member_count_within_radius", max_count)


    center_i = int(best_idxs[0])
    center = start_df.iloc[center_i]
    member_idx = neighbors[center_i]
    members = start_df.iloc[member_idx].copy()
    differences = coords[member_idx] - coords[center_i]
    members["distance_to_center_m"] = np.hypot(*differences.T)
    members.insert(0, "radius_m", radius)
    members.insert(0, "center_y", center["start_y"])
    members.insert(0, "center_x", center["start_x"])
    members.insert(0, "center_user_id", center["user_id"])
    members = members.sort_values(
        ["distance_to_center_m", "user_id"], kind="stable"
    ).reset_index(drop=True)

    return members, tied_centers


def match_privacy_scores(privacy_csv, members):

    scores = pd.read_csv(
        privacy_csv, usecols=["user_id", "privacy_score"],
        dtype={"user_id": "string"},
    )
    scores["user_id"] = scores["user_id"].str.strip()
    scores = scores.dropna(subset=["user_id"])
    scores = scores[scores["user_id"] != ""]
    scores = scores.drop_duplicates(subset=["user_id"], keep="first")


    return (
        scores[["user_id", "privacy_score"]]
        .merge(members[["user_id"]], on="user_id", how="inner", validate="one_to_one")
        .reset_index(drop=True)
    )


def process_scenario(scenario, csv_file, privacy_csv):
    start_df = compute_start_points_chunked(csv_file)
    members, tied_centers = find_largest_cluster(start_df, RADIUS_M)
    matched = match_privacy_scores(privacy_csv, members)

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    suffix = scenario
    outputs = {
        f"largest_A_members_{suffix}.csv": members,
        f"largest_A_ids_{suffix}.csv": members[["user_id"]],
        f"largest_A_tied_centers_{suffix}.csv": tied_centers,
        f"matched_user_ids_{suffix}.csv": matched,
    }
    for filename, table in outputs.items():
        output_csv = OUTPUT_ROOT / filename
        table.to_csv(output_csv, index=False)
        print(f"Saved: {output_csv}")

    center = tied_centers.iloc[0]
    print(f"Total users with valid start points: {len(start_df)}")
    print(f"Radius: {RADIUS_M} m; largest cluster: {len(members)} users")
    print(f"Chosen center: {center['user_id']}; tied centers: {len(tied_centers)}")
    print(f"Matched privacy-score rows: {len(matched)}")
    print(f"Cluster users absent from privacy CSV: {len(members) - len(matched)}")
    print(f"Matched rows with missing privacy_score: {matched['privacy_score'].isna().sum()}")


if __name__ == "__main__":
    
   

    for scenario, csv_file in SCENARIOS.items():
        print(f"\nProcessing {scenario}")
        process_scenario(scenario, csv_file, OUTPUT_SOURCE[scenario])


