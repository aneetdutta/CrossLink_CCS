import csv
import pandas as pd
from collections import defaultdict
import numpy as np
import math

def per_event_upper_bound(lambda_r: float, lambda_t: float, T: float) -> float:
    if lambda_r <= 0 or lambda_t <= 0:
        raise ValueError("λ_r and λ_t must be positive.")
    if T < 0:
        raise ValueError("T must be non‑negative.")

    B = lambda_r + lambda_t
    A = lambda_r - lambda_t
    absA = abs(A)
    C = 1.0 / B + lambda_t / B**2

    f2 = (
        2.0
        * lambda_r**2
        * math.exp(-B * T)
        * C
        * (math.exp(absA * T) - 1.0)
        / absA
    )

    f3_sup = (2.0 * lambda_r**2 * lambda_t) / (math.e * B**2 * absA)

    gamma = absA / B
    term1 = (1.0 - gamma) ** ((1.0 - gamma) / gamma)
    term2 = (1.0 - gamma) ** (1.0 / gamma)
    f4_sup = 2.0 * lambda_r**2 / absA**2 * (term1 - term2)

    f1_const = lambda_r * C

    p_event = f1_const + f2 + f3_sup + f4_sup
    p = min(max(p_event, 0.0), 1.0)
    u = p ** (2 * lambda_r * T)
    return 1 - u


def upper_bound(lambda_r, lambda_t, T):
    """
    Your original function but WITHOUT debug prints (so it doesn't spam output per user).
    """
    A = lambda_r - lambda_t
    B = lambda_r + lambda_t
    A_mod = lambda_t - lambda_r

    C1 = (1 / B) + (lambda_t / B**2)
    p_mix = (lambda_r * C1)

    u = np.exp(-2 * lambda_r * T * p_mix)
    upper = 1 - u
    return upper


def upper_bound_wifi(lambda_r, T):
    p_mix = 0.25
    u = np.exp(-2 * lambda_r * T * p_mix)
    upper = 1 - u
    return upper


# =========================
# INPUT FILES
# =========================

# ✅ NEW: single combined neighbor duration file (my format)
neighbor_file_all = "/home/aneet_wisec/usenix_2025/path-leakage/data/scenario_result_1024_sumo_all4/neighbor_durations_by_protocol.csv"

scores_file = "/home/aneet_wisec/usenix_2025/path-leakage/data/scenario_result_1024_sumo_all4/user_data_scenario_result_1024_sumo_all4.csv"

# =========================
# PARAMETERS
# =========================

''' Parameters for BLE '''
lambdar_r_ble = 0.008  # (600 seconds)
lambda_t_ble  = 0.333            # (1 minute)

''' Parameters for LTE '''
lambdar_r_lte = 0.00238095238  # (900 seconds)
lambda_t_lte  = 0.2           # (1 minute)

''' Parameters for WiFi '''
lambdar_r_wf = 0.03333333333             # (600 seconds)
lambda_t_wf  = 0.03333333333             # (1 minute)  (not used in your wifi function)


# =========================
# LOAD DATA
# =========================

df_scores = pd.read_csv(scores_file)

# Read combined neighbor durations
df_nd = pd.read_csv(neighbor_file_all)

# Normalize types + protocol naming
df_scores["user_id"] = df_scores["user_id"].astype(str)
df_nd["user_id"] = df_nd["user_id"].astype(str)
df_nd["neighbor_id"] = df_nd["neighbor_id"].astype(str)

df_nd["protocol"] = df_nd["protocol"].astype(str).str.strip().str.lower()

# Ensure numeric duration
df_nd["duration_seconds"] = pd.to_numeric(df_nd["duration_seconds"], errors="coerce").fillna(0.0)

unique_user_list = df_scores["user_id"].unique().tolist()

# Precompute total duration per (user_id, protocol)
# totals.loc[user_id, "ble"/"lte"/"wifi"] = total duration_seconds
totals = (
    df_nd.groupby(["user_id", "protocol"])["duration_seconds"]
    .sum()
    .unstack(fill_value=0.0)
)

# Ensure all protocol columns exist even if missing
for p in ["ble", "lte", "wifi"]:
    if p not in totals.columns:
        totals[p] = 0.0


# =========================
# COMPUTE MIXING ESTIMATES
# =========================

mixing_users = 0.0
mixing_users_lte = 0.0
mixing_users_ble = 0.0
mixing_users_wifi = 0.0
mixing_users_wifi_lte = 0.0
mixing_users_wifi_ble = 0.0
mixing_users_wifi_ble_lte = 0.0

for user in unique_user_list:
    # get durations; if user not present -> 0
    if user in totals.index:
        T_ble = float(totals.loc[user, "ble"])
        T_lte = float(totals.loc[user, "lte"])
        T_wifi = float(totals.loc[user, "wifi"])
    else:
        T_ble, T_lte, T_wifi = 0.0, 0.0, 0.0

    # Probability of mixing at least once during total mix-zone duration T for each protocol
    upper_ble = upper_bound(lambdar_r_ble, lambda_t_ble, T_ble)
    upper_lte = upper_bound(lambdar_r_lte, lambda_t_lte, T_lte)
    upper_wifi = upper_bound(lambdar_r_wf,lambda_t_wf,T_wifi)

    # Your original combination logic (BLE * LTE)
    upper_ble_lte = upper_ble * upper_lte
    upper_wifi_lte= upper_wifi * upper_lte
    upper_wifi_ble= upper_wifi * upper_ble
    upper_wifi_ble_lte=upper_wifi * upper_ble * upper_lte

    mixing_users += upper_ble_lte
    mixing_users_lte += upper_lte
    mixing_users_ble += upper_ble
    mixing_users_wifi += upper_wifi
    mixing_users_wifi_lte += upper_wifi_lte
    mixing_users_wifi_ble += upper_wifi_ble
    mixing_users_wifi_ble_lte += upper_wifi_ble_lte

print(f"Estimated number of users that mix (BLE*LTE): {mixing_users}")
print(f"Estimated number of users that will mix in LTE: {mixing_users_lte}")
print(f"Estimated number of users that will mix in BLE: {mixing_users_ble}")
print(f"Estimated number of users that will mix in WiFi: {mixing_users_wifi}")
print(f"Estimated number of users that mix (BLE*WiFi): {mixing_users_wifi_ble}")
print(f"Estimated number of users that mix (LTE*WiFi): {mixing_users_wifi_lte}")
print(f"Estimated number of users that mix (LTE*WiFi*BLE): {mixing_users_wifi_ble_lte}")



