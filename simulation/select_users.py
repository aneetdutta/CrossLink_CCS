#!/usr/bin/env python3


import argparse
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StartPoint:
    timestep: float
    x: float
    y: float


def compute_start_points_chunked(
    input_csv: str,
    chunk_size: int = 1_000_000,
) -> pd.DataFrame:
   
    usecols = ["timestep", "user_id", "loc_x", "loc_y"]
    best: Dict[str, StartPoint] = {}

    for chunk in pd.read_csv(input_csv, usecols=usecols, chunksize=chunk_size):
        chunk = chunk.dropna(subset=usecols)
        if chunk.empty:
            continue

       
        idx = chunk.groupby("user_id")["timestep"].idxmin()
        reduced = chunk.loc[idx, usecols]

       
        for row in reduced.itertuples(index=False):
            uid = str(row.user_id)
            ts = float(row.timestep)
            x = float(row.loc_x)
            y = float(row.loc_y)

            prev = best.get(uid)
            if prev is None or ts < prev.timestep:
                best[uid] = StartPoint(ts, x, y)

    start_df = pd.DataFrame(
        [(uid, sp.timestep, sp.x, sp.y) for uid, sp in best.items()],
        columns=["user_id", "timestep", "start_x", "start_y"],
    ).sort_values("user_id").reset_index(drop=True)

    return start_df


def radius_neighbors(coords: np.ndarray, radius: float) -> Tuple[List[List[int]], np.ndarray]:
   
    try:
        from scipy.spatial import cKDTree  

        tree = cKDTree(coords)
        neighbors = tree.query_ball_point(coords, r=radius)
        counts = np.array([len(n) for n in neighbors], dtype=int)
        return neighbors, counts

    except Exception:
        
        diff = coords[:, None, :] - coords[None, :, :]
        dist2 = np.einsum("ijk,ijk->ij", diff, diff)
        within = dist2 <= (radius * radius)
        neighbors = [np.where(within[i])[0].tolist() for i in range(within.shape[0])]
        counts = within.sum(axis=1).astype(int)
        return neighbors, counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Largest start-point cluster based on definition A (single-center radius).")
    parser.add_argument("--input", required=True, help="Input CSV (must contain timestep,user_id,loc_x,loc_y)")
    parser.add_argument("--radius", type=float, default=100.0, help="Radius in meters (default 100)")
    parser.add_argument("--chunk_size", type=int, default=1_000_000, help="Chunk size for reading CSV (default 1,000,000)")

    parser.add_argument(
        "--out_members",
        default="largest_startpoint_cluster_based_on_A_members.csv",
        help="Output CSV with members + distances (default largest_startpoint_cluster_based_on_A_members.csv)",
    )
    parser.add_argument(
        "--out_ids",
        default="largest_startpoint_cluster_based_on_A_ids.csv",
        help="Output CSV with only member user_ids (default largest_startpoint_cluster_based_on_A_ids.csv)",
    )
    parser.add_argument(
        "--out_tied_centers",
        default="largest_startpoint_cluster_based_on_A_tied_centers.csv",
        help="Output CSV listing all tied best centers (default largest_startpoint_cluster_based_on_A_tied_centers.csv)",
    )

    args = parser.parse_args()

    
    start_df = compute_start_points_chunked(args.input, chunk_size=args.chunk_size)
    if start_df.empty:
        raise SystemExit("No start points found. Check the input columns / file.")

    coords = start_df[["start_x", "start_y"]].to_numpy(dtype=float)

   
    neighbors, counts = radius_neighbors(coords, radius=args.radius)
    max_count = int(counts.max())
    best_idxs = np.where(counts == max_count)[0]

    tied_centers = start_df.loc[best_idxs, ["user_id", "timestep", "start_x", "start_y"]].copy()
    tied_centers.insert(0, "radius_m", float(args.radius))
    tied_centers.insert(1, "member_count_within_radius", max_count)
    tied_centers.to_csv(args.out_tied_centers, index=False)

    
    center_i = int(best_idxs[0])
    center_user = str(start_df.loc[center_i, "user_id"])
    center_x = float(start_df.loc[center_i, "start_x"])
    center_y = float(start_df.loc[center_i, "start_y"])

    member_idx = neighbors[center_i]
    members = start_df.iloc[member_idx].copy()

   
    diffs = coords[member_idx] - coords[center_i]
    dists = np.sqrt((diffs * diffs).sum(axis=1))

    members["distance_to_center_m"] = dists
    members.insert(0, "radius_m", float(args.radius))
    members.insert(0, "center_y", center_y)
    members.insert(0, "center_x", center_x)
    members.insert(0, "center_user_id", center_user)

    members = members.sort_values("distance_to_center_m").reset_index(drop=True)

   
    members.to_csv(args.out_members, index=False)
    members[["user_id"]].to_csv(args.out_ids, index=False)

    
    print(f"Total users (start points): {len(start_df)}")
    print(f"Radius: {args.radius} m")
    print(f"Max members within radius (definition A): {max_count}")
    print("Tied best centers:")
    for _, row in tied_centers.iterrows():
        print(f"  - {row['user_id']} at ({row['start_x']:.6f}, {row['start_y']:.6f})")

    print(f"\nChosen center: {center_user} at ({center_x:.6f}, {center_y:.6f})")
    print(f"Saved members CSV: {args.out_members}")
    print(f"Saved ids CSV: {args.out_ids}")
    print(f"Saved tied centers CSV: {args.out_tied_centers}")


if __name__ == "__main__":
    main()
