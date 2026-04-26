#!/usr/bin/env python3
import csv
import math
import json
import os
from collections import defaultdict
from itertools import combinations

# =========================
# HARD-CODED SETTINGS
# =========================
CSV_FILE = "/path-leakage/data/synchronized_low_ti/user_data_synchronized_low_ti.csv"
# or your uploaded file:
# CSV_FILE = "/mnt/data/user_data_scenario_result_512_sumo_all1.csv"

PROTOCOLS = ("lte", "ble", "wifi")

# DIFFERENT base thresholds per protocol (edit these)
BASE_THRESHOLD_BY_PROTO = {
    "lte": 20.0,
    "ble": 2.0,
    "wifi": 20.0,
}

VMAX = 3.0  # same Vmax term as your earlier code
INTERPOLATION_GRANULARITY = 0.1  # same as your interpolate_and_check()

# Minimum candidate-session length in timesteps (on effective_threshold)
MIN_SESSION_TIMESTEPS = 1

# Output directory
OUT_DIR = os.path.dirname(CSV_FILE) or "."
OUT_NEIGHBOR_DURATIONS_CSV = os.path.join(OUT_DIR, "neighbor_durations_by_protocol.csv")
OUT_PROTOCOL_SESSIONS_CSV = os.path.join(OUT_DIR, "mixzone_sessions_protocol_eval.csv")
OUT_SUMMARY_JSON = os.path.join(OUT_DIR, "mixzone_protocol_summary.json")

# If True, store the list of absolute timesteps when the pair was close (effective threshold).
# WARNING: this can make the sessions CSV big.
STORE_CLOSE_TIMESTEPS = True

# Column names in your CSV
FIELD_USER = "user_id"
FIELD_T = "timestep"
FIELD_X = "loc_x"
FIELD_Y = "loc_y"
RAND_TMPL = "randomized_{proto}"
TX_TMPL = "transmit_{proto}"

# =========================
# Helpers
# =========================
def to_bool(v):
    if v is None:
        return False
    if isinstance(v, bool):
        return v
    s = str(v).strip().lower()
    return s in ("1", "true", "t", "yes", "y")


def powerset_nonempty(items):
    items = list(items)
    for r in range(1, len(items) + 1):
        for comb in combinations(items, r):
            yield comb


def load_user_csv(csv_filename):
    """
    Loads:
      data_by_timestep[t] = [(user_id, x, y), ...]
      user_timesteps[user] = set([t,...])
      user_data[(user,t)] = row dict
    """
    data_by_timestep = defaultdict(list)
    user_timesteps = defaultdict(set)
    user_data = {}

    with open(csv_filename, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = str(row[FIELD_USER])
            t = int(float(row[FIELD_T]))
            x = float(row[FIELD_X])
            y = float(row[FIELD_Y])

            data_by_timestep[t].append((user_id, x, y))
            user_timesteps[user_id].add(t)
            row[FIELD_T] = t  # normalize
            user_data[(user_id, t)] = row

    return data_by_timestep, user_timesteps, user_data


# =========================
# 1) Candidate sessions using effective_threshold = base + Vmax
#    (matches your earlier calculate_with_generic_dynamic_threshold)
# =========================
def calculate_together_periods_multi(data_by_timestep, user_timesteps):
    """
    Returns:
      together_periods[proto][(u1,u2)] = list of dicts:
         {start_time, end_time, duration_timesteps, close_timesteps(optional)}
    """
    # precompute effective thresholds
    eff_thr = {p: float(BASE_THRESHOLD_BY_PROTO[p]) + float(VMAX) for p in PROTOCOLS}

    together_periods = {p: defaultdict(list) for p in PROTOCOLS}
    current_session = {p: {} for p in PROTOCOLS}  # p -> dict(pair -> state)

    def new_state():
        st = {
            "ongoing": False,
            "start_time": None,
            "accumulated_duration": 0,
        }
        if STORE_CLOSE_TIMESTEPS:
            st["close_timesteps"] = []
        return st

    # iterate timesteps in order (same as your code)
    for t in sorted(data_by_timestep.keys()):
        users_at_t = data_by_timestep[t]
        n = len(users_at_t)

        for i in range(n):
            u1, x1, y1 = users_at_t[i]
            for j in range(i + 1, n):
                u2, x2, y2 = users_at_t[j]
                if u1 == u2:
                    continue

                pair = tuple(sorted((u1, u2)))

                dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                for p in PROTOCOLS:
                    thr = eff_thr[p]
                    sess = current_session[p].setdefault(pair, new_state())

                    if dist <= thr:
                        if not sess["ongoing"]:
                            sess["ongoing"] = True
                            sess["start_time"] = t
                            sess["accumulated_duration"] = 0
                            if STORE_CLOSE_TIMESTEPS:
                                sess["close_timesteps"] = []
                        sess["accumulated_duration"] += 1
                        if STORE_CLOSE_TIMESTEPS:
                            sess["close_timesteps"].append(t)
                    else:
                        if sess["ongoing"]:
                            period_info = {
                                "start_time": sess["start_time"],
                                "end_time": t - 1,
                                "duration_timesteps": sess["accumulated_duration"],
                            }
                            if STORE_CLOSE_TIMESTEPS:
                                period_info["close_timesteps"] = list(sess["close_timesteps"])
                            together_periods[p][pair].append(period_info)

                            sess["ongoing"] = False
                            sess["start_time"] = None
                            sess["accumulated_duration"] = 0
                            if STORE_CLOSE_TIMESTEPS:
                                sess["close_timesteps"] = []

    # finalize ongoing sessions at end (same idea as your code)
    for p in PROTOCOLS:
        for pair, sess in current_session[p].items():
            if sess.get("ongoing"):
                u1, u2 = pair
                last_timestep = max(user_timesteps[u1].union(user_timesteps[u2]))
                period_info = {
                    "start_time": sess["start_time"],
                    "end_time": last_timestep,
                    "duration_timesteps": sess["accumulated_duration"],
                }
                if STORE_CLOSE_TIMESTEPS:
                    period_info["close_timesteps"] = list(sess["close_timesteps"])
                together_periods[p][pair].append(period_info)
                sess["ongoing"] = False

    return together_periods


# =========================
# 2) Interpolated strict durations (dist <= base_threshold)
#    (matches your interpolate_and_check)
# =========================
def interpolated_strict_duration_seconds(u1, u2, start_time, end_time, user_data, base_threshold):
    """
    Returns duration in "seconds" (timesteps assumed 1 sec) accumulated at 0.1 granularity
    where interpolated distance <= base_threshold.
    """
    gran = INTERPOLATION_GRANULARITY
    num_steps = int(1 / gran)
    duration = 0.0

    for t in range(start_time, end_time):
        k_u_t = (u1, t)
        k_u_t1 = (u1, t + 1)
        k_n_t = (u2, t)
        k_n_t1 = (u2, t + 1)

        if k_u_t not in user_data or k_u_t1 not in user_data or k_n_t not in user_data or k_n_t1 not in user_data:
            continue

        x1_u = float(user_data[k_u_t][FIELD_X]);  y1_u = float(user_data[k_u_t][FIELD_Y])
        x2_u = float(user_data[k_u_t1][FIELD_X]); y2_u = float(user_data[k_u_t1][FIELD_Y])

        x1_n = float(user_data[k_n_t][FIELD_X]);  y1_n = float(user_data[k_n_t][FIELD_Y])
        x2_n = float(user_data[k_n_t1][FIELD_X]); y2_n = float(user_data[k_n_t1][FIELD_Y])

        for step in range(num_steps):
            fraction = step * gran
            ix_u = x1_u + fraction * (x2_u - x1_u)
            iy_u = y1_u + fraction * (y2_u - y1_u)

            ix_n = x1_n + fraction * (x2_n - x1_n)
            iy_n = y1_n + fraction * (y2_n - y1_n)

            dist = math.sqrt((ix_n - ix_u) ** 2 + (iy_n - iy_u) ** 2)
            if dist <= base_threshold:
                duration += gran

    return duration


# =========================
# 3) Protocol mixing conditions per candidate session
# =========================
def first_true_time(user_id, start_t, end_t, user_data, field):
    """Earliest timestep in [start_t, end_t] where field is True, else None."""
    for t in range(start_t, end_t + 1):
        row = user_data.get((user_id, t))
        if row and to_bool(row.get(field)):
            return t
    return None


def any_true_in_interval(user_id, start_t, end_t, user_data, field):
    """Any timestep in [start_t, end_t] where field is True?"""
    if end_t < start_t:
        return False
    for t in range(start_t, end_t + 1):
        row = user_data.get((user_id, t))
        if row and to_bool(row.get(field)):
            return True
    return False


def check_protocol_conditions(u1, u2, start_t, end_t, user_data, proto):
    """
    Implements your conditions using:
      randomized_<proto>
      transmit_<proto>

    Condition (1): both randomize within [start_t, end_t]
    Condition (2): order rules based on transmit timing
    """
    rand_field = RAND_TMPL.format(proto=proto)
    tx_field = TX_TMPL.format(proto=proto)

    r1 = first_true_time(u1, start_t, end_t, user_data, rand_field)
    r2 = first_true_time(u2, start_t, end_t, user_data, rand_field)
    if r1 is None or r2 is None:
        return False, {
            "reason": "cond1_failed_missing_randomization",
            "r_u1": r1, "r_u2": r2
        }

    # decide first/second randomizer
    if r1 < r2 or (r1 == r2 and u1 <= u2):
        first, second = u1, u2
        r_first, r_second = r1, r2
    else:
        first, second = u2, u1
        r_first, r_second = r2, r1

    # first device transmits randomized identifier after its randomization
    tx_first_rand = first_true_time(first, r_first, end_t, user_data, tx_field)
    if tx_first_rand is None:
        return False, {
            "reason": "cond2_failed_no_tx_by_first_after_randomization",
            "first": first, "second": second,
            "r_first": r_first, "r_second": r_second,
            "tx_first_rand": None
        }

    # Condition (2a)
    if tx_first_rand >= r_second:
        return True, {
            "reason": "ok_case_a",
            "first": first, "second": second,
            "r_first": r_first, "r_second": r_second,
            "tx_first_rand": tx_first_rand
        }

    # Condition (2b): first transmits before second randomizes
    # second must NOT transmit original in [tx_first_rand, r_second)
    # (since second hasn't randomized yet, any transmit is "original")
    bad = any_true_in_interval(second, tx_first_rand, r_second - 1, user_data, tx_field)
    if bad:
        return False, {
            "reason": "cond2_failed_case_b_second_transmitted_original",
            "first": first, "second": second,
            "r_first": r_first, "r_second": r_second,
            "tx_first_rand": tx_first_rand
        }

    return True, {
        "reason": "ok_case_b",
        "first": first, "second": second,
        "r_first": r_first, "r_second": r_second,
        "tx_first_rand": tx_first_rand
    }


# =========================
# MAIN
# =========================
def main():
    # sanity
    for p in PROTOCOLS:
        if p not in BASE_THRESHOLD_BY_PROTO:
            raise RuntimeError(f"Missing BASE_THRESHOLD_BY_PROTO['{p}']")

    print("Reading CSV:", CSV_FILE)
    data_by_timestep, user_timesteps, user_data = load_user_csv(CSV_FILE)
    print("Unique timesteps:", len(data_by_timestep))
    print("Unique users:", len(user_timesteps))

    # Candidate sessions per protocol (effective threshold)
    together_periods = calculate_together_periods_multi(data_by_timestep, user_timesteps)

    # Prepare outputs and stats
    ok_users = {p: set() for p in PROTOCOLS}
    ok_pairs = {p: set() for p in PROTOCOLS}
    ok_sessions = {p: 0 for p in PROTOCOLS}

    # For combinations across protocols (pair-level and user-level)
    pair_success = defaultdict(set)  # pair -> set(protocols) where it had at least one OK session
    user_success = defaultdict(set)  # user -> set(protocols) where it participated in at least one OK session

    # Neighbor durations (strict, interpolated, per protocol) pair-level
    strict_duration_pair = {p: defaultdict(float) for p in PROTOCOLS}

    # Write session-level evaluation CSV
    with open(OUT_PROTOCOL_SESSIONS_CSV, "w", newline="", encoding="utf-8") as f_sess:
        w_sess = csv.writer(f_sess)
        header = [
            "protocol", "u1", "u2",
            "start_time", "end_time",
            "duration_timesteps_effective_threshold",
            "strict_duration_seconds_interpolated",
            "ok",
            "reason",
            "first", "second",
            "r_first", "r_second",
            "tx_first_rand",
        ]
        if STORE_CLOSE_TIMESTEPS:
            header.append("close_timesteps_json")
        w_sess.writerow(header)

        # Evaluate each protocol’s sessions
        for p in PROTOCOLS:
            base_thr = float(BASE_THRESHOLD_BY_PROTO[p])
            for pair, periods in together_periods[p].items():
                u1, u2 = pair
                for period in periods:
                    s = int(period["start_time"])
                    e = int(period["end_time"])
                    dur_eff = int(period["duration_timesteps"])

                    if dur_eff < MIN_SESSION_TIMESTEPS:
                        continue

                    # strict interpolated duration (like your earlier interpolate_and_check)
                    strict_sec = interpolated_strict_duration_seconds(u1, u2, s, e, user_data, base_thr)
                    strict_duration_pair[p][pair] += strict_sec

                    # mixing condition check (using same candidate period bounds)
                    ok, details = check_protocol_conditions(u1, u2, s, e, user_data, p)

                    if ok:
                        ok_sessions[p] += 1
                        ok_pairs[p].add(pair)
                        ok_users[p].update(pair)
                        pair_success[pair].add(p)
                        user_success[u1].add(p)
                        user_success[u2].add(p)

                    row = [
                        p, u1, u2,
                        s, e,
                        dur_eff,
                        f"{strict_sec:.3f}",
                        bool(ok),
                        details.get("reason"),
                        details.get("first"),
                        details.get("second"),
                        details.get("r_first"),
                        details.get("r_second"),
                        details.get("tx_first_rand"),
                    ]
                    if STORE_CLOSE_TIMESTEPS:
                        row.append(json.dumps(period.get("close_timesteps", [])))
                    w_sess.writerow(row)

    # Write neighbor durations by protocol (ordered pairs like your earlier output style)
    with open(OUT_NEIGHBOR_DURATIONS_CSV, "w", newline="", encoding="utf-8") as f_nd:
        w_nd = csv.writer(f_nd)
        w_nd.writerow(["protocol", "user_id", "neighbor_id", "duration_seconds"])
        for p in PROTOCOLS:
            for (u1, u2), dur in strict_duration_pair[p].items():
                # write both directions to mirror your earlier dict output style
                w_nd.writerow([p, u1, u2, f"{dur:.6f}"])
                w_nd.writerow([p, u2, u1, f"{dur:.6f}"])

    # Build combination summaries
    subsets = list(powerset_nonempty(PROTOCOLS))

    pair_combo_atleast = {}
    for subset in subsets:
        subset_set = set(subset)
        pair_combo_atleast["+".join(subset)] = sum(
            1 for _, sset in pair_success.items() if subset_set.issubset(sset)
        )

    user_combo_atleast = {}
    for subset in subsets:
        subset_set = set(subset)
        user_combo_atleast["+".join(subset)] = sum(
            1 for _, sset in user_success.items() if subset_set.issubset(sset)
        )

    summary = {
        "input_csv": CSV_FILE,
        "protocols": list(PROTOCOLS),
        "base_threshold_by_proto": BASE_THRESHOLD_BY_PROTO,
        "Vmax": VMAX,
        "effective_threshold_by_proto": {p: BASE_THRESHOLD_BY_PROTO[p] + VMAX for p in PROTOCOLS},
        "interpolation_granularity": INTERPOLATION_GRANULARITY,
        "min_session_timesteps": MIN_SESSION_TIMESTEPS,
        "per_protocol": {
            p: {
                "ok_sessions": ok_sessions[p],
                "ok_unique_pairs": len(ok_pairs[p]),
                "ok_unique_users": len(ok_users[p]),
            } for p in PROTOCOLS
        },
        "pair_combo_atleast": pair_combo_atleast,
        "user_combo_atleast": user_combo_atleast,
        "outputs": {
            "neighbor_durations_csv": OUT_NEIGHBOR_DURATIONS_CSV,
            "sessions_eval_csv": OUT_PROTOCOL_SESSIONS_CSV,
            "summary_json": OUT_SUMMARY_JSON,
        }
    }

    with open(OUT_SUMMARY_JSON, "w", encoding="utf-8") as f_js:
        json.dump(summary, f_js, indent=2)

    # Print summary
    print("\n=== Per-protocol results (should align with your earlier proximity semantics) ===")
    for p in PROTOCOLS:
        print(
            f"{p.upper():4s} base_thr={BASE_THRESHOLD_BY_PROTO[p]:6.2f} eff_thr={BASE_THRESHOLD_BY_PROTO[p]+VMAX:6.2f} | "
            f"ok_users={len(ok_users[p])} ok_pairs={len(ok_pairs[p])} ok_sessions={ok_sessions[p]}"
        )

    print("\n=== User combinations (AT LEAST these protocols satisfied, across any neighbors/sessions) ===")
    for subset in subsets:
        label = "+".join(subset)
        print(f"{label:12s}: {summary['user_combo_atleast'][label]}")

    print("\n=== Pair combinations (AT LEAST these protocols satisfied, across any sessions) ===")
    for subset in subsets:
        label = "+".join(subset)
        print(f"{label:12s}: {summary['pair_combo_atleast'][label]}")

    print("\nWrote:")
    print(" -", OUT_NEIGHBOR_DURATIONS_CSV)
    print(" -", OUT_PROTOCOL_SESSIONS_CSV)
    print(" -", OUT_SUMMARY_JSON)


if __name__ == "__main__":
    main()

