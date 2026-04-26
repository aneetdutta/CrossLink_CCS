#!/usr/bin/env python3
"""
Estimate the expected number of users that mix at least once
during the trace, using per-interval probabilities.

Author: (your name) – 2025-06-09
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ──────────────────────────────────────────────────────────
# 1.  File locations  (EDIT THESE)
# ──────────────────────────────────────────────────────────
NEIGHBOR_BLE = "/home/aneet_wisec/usenix_2025/path-leakage/analysis/neighbor_durations_ble_sumo_512.csv"

NEIGHBOR_LTE = "/home/aneet_wisec/usenix_2025/path-leakage/analysis/neighbor_durations_lte_sumo_512.csv"

SCORES_FILE  = "/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_exponential_512_sumo_LW/multi_protocol_scenario_exponential_512_sumo_LW.csv"  # only for user list

# ──────────────────────────────────────────────────────────
# 2.  Model parameters
# ──────────────────────────────────────────────────────────
#     λ_r  = refresh (reappearance) rate
#     λ_t  = transmission rate
LAMBDAR_R_BLE = 0.00166666666   # 1 / 600 s
LAMBDA_T_BLE  = 0.01666666666   # 1 /  60 s

LAMBDAR_R_LTE = 0.00111111111   # 1 / 900 s
LAMBDA_T_LTE  = 0.01666666666   # 1 /  60 s

# ──────────────────────────────────────────────────────────
# 3.  Helper functions
# ──────────────────────────────────────────────────────────
def upper_bound(lambda_r: float, lambda_t: float, T: float) -> float:
    """
    Probability that *at least one* mix occurs during an interval of length T,
    given the two-phase model (see paper §X.Y).
    """
    A = lambda_r - lambda_t
    B = lambda_r + lambda_t
    C1 = (1.0 / B) + (lambda_t / B**2)
    p_mix = lambda_r * C1                      # 0 < p_mix < 1
    rate  = 2.0 * lambda_r * p_mix             # events per second
    return 1.0 - np.exp(-rate * T)             # 0 ≤ value ≤ 1


def product_one_minus(probs):
    """Return Π (1 − p_i).  If list empty ⇒ 1.0."""
    if not probs:
        return 1.0
    # Use log-sum-exp for numerical stability on long products
    logs = np.log1p(-np.clip(probs, 0.0, 1.0))
    return float(np.exp(logs.sum()))

# ──────────────────────────────────────────────────────────
# 4.  Load CSVs
# ──────────────────────────────────────────────────────────
df_ble = pd.read_csv(NEIGHBOR_BLE)
df_lte = pd.read_csv(NEIGHBOR_LTE)
df_scores = pd.read_csv(SCORES_FILE)

all_users = df_scores["user_id"].unique().tolist()

# Sanity: ensure required columns exist
required_cols = {"user_id", "duration_seconds"}
for name, df in [("BLE", df_ble), ("LTE", df_lte)]:
    if not required_cols.issubset(df.columns):
        raise ValueError(f"{name} file missing columns {required_cols}")

# Optional: speed-up – index by user for O(1) lookup
ble_by_user = {u: g["duration_seconds"].values
               for u, g in df_ble.groupby("user_id")}
lte_by_user = {u: g["duration_seconds"].values
               for u, g in df_lte.groupby("user_id")}

# ──────────────────────────────────────────────────────────
# 5.  Main loop – per user
# ──────────────────────────────────────────────────────────
expected_mix_any   = 0.0  # P(user mixes ≥ once on BLE or LTE)
expected_mix_ble   = 0.0  # P(user mixes ≥ once on BLE)
expected_mix_lte   = 0.0  # P(user mixes ≥ once on LTE)
union_upper_total  = 0.0  # loose union-bound upper limit

for user in all_users:
    # ----- BLE probabilities for this user -----
    p_ble_list = [
        upper_bound(LAMBDAR_R_BLE, LAMBDA_T_BLE, t)
        for t in ble_by_user.get(user, [])
    ]
    q_ble = product_one_minus(p_ble_list)          # prob of *no* mix on BLE
    p_ble = 1.0 - q_ble                           # prob of ≥1 mix on BLE

    # ----- LTE probabilities for this user -----
    p_lte_list = [
        upper_bound(LAMBDAR_R_LTE, LAMBDA_T_LTE, t)
        for t in lte_by_user.get(user, [])
    ]
    q_lte = product_one_minus(p_lte_list)          # prob of *no* mix on LTE
    p_lte = 1.0 - q_lte                           # prob of ≥1 mix on LTE

    # ----- Combined radios -----
    p_any  =  (p_ble * p_lte)                # mixes on BLE or LTE
    p_union = min(sum(p_ble_list) + sum(p_lte_list), 1.0)  # Boole upper bound

    # accumulate expectations
    expected_mix_any  += p_any
    expected_mix_ble  += p_ble
    expected_mix_lte  += p_lte
    union_upper_total += p_union

# ──────────────────────────────────────────────────────────
# 6.  Report
# ──────────────────────────────────────────────────────────
num_users = len(all_users)
print(f"Users in trace                        : {num_users}")
print("────────────────────────────────────────────────────")
print(f"Expected users mixing ≥ once (BLE ∪ LTE) : {expected_mix_any:,.2f}")
print(f"  – via BLE                              : {expected_mix_ble:,.2f}")
print(f"  – via LTE                              : {expected_mix_lte:,.2f}")
print("────────────────────────────────────────────────────")
print(f"Loose union-bound upper limit            : {union_upper_total:,.2f}")

