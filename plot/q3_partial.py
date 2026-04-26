import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from modules.general import str_to_bool

#SCENARIO_NAME = os.getenv("SCENARIO_NAME")
# ENABLE_SMART_TRACKING = str_to_bool(os.getenv("ENABLE_SMART_TRACKING"))
#ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
#ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))
#ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
#NUM_USERS = int(os.getenv("TOTAL_NUMBER_OF_USERS", 512))

marker_interval = 50
NUM_USERS = 512
BASE_SCENARIO_NAME = f"scenario_result_{NUM_USERS}_sumo"
# ENABLE_SMART_TRACKING = str_to_bool(os.getenv("ENABLE_SMART_TRACKING"))
ENABLE_BLUETOOTH = True
ENABLE_LTE = True
ENABLE_WIFI = False
NUM_USERS = 512

plt.figure(figsize=(3.3,1.3))
#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00", "#CC79A7", "#F0E442
# Load the CSV files

def ensure_min_length_with_zeros(array, min_length=NUM_USERS):
    array_sorted = np.sort(array)
    if len(array_sorted) < min_length:
        zeros_to_add = min_length - len(array_sorted)
        array_sorted = np.append(array_sorted, [0] * zeros_to_add)
    return np.sort(array_sorted)



if ENABLE_WIFI:
    baseline_smart_wifi_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_partial/single_ble_scenario_result_512_sumo_partial.csv')
    baseline_smart_wifi_scores = baseline_smart_wifi_df['privacy_score'].values
    baseline_smart_wifi_scores_sorted = ensure_min_length_with_zeros(np.sort(baseline_smart_wifi_scores))
    baseline_smart_wifi_users = np.arange(1, len(baseline_smart_wifi_scores_sorted) + 1)
    count_users_privacy_1 = baseline_smart_wifi_df[baseline_smart_wifi_df['privacy_score'] == 1.0].shape[0]
    count_users_privacy_2 = baseline_smart_wifi_df[baseline_smart_wifi_df['privacy_score'] >= 0.95].shape[0]
    count_users_privacy_3 = baseline_smart_wifi_df[baseline_smart_wifi_df['privacy_score'] >= 0.9].shape[0]
    count_users_privacy_4 = baseline_smart_wifi_df[baseline_smart_wifi_df['privacy_score'] >= 0.8].shape[0]
    print(f"Total number of users for Single WiFI with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
    print(f"Total number of users for Single WiFI with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
    print(f"Total number of users for Single WiFI with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
    print(f"Total number of users for Single WiFI with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
    plt.plot(baseline_smart_wifi_users, baseline_smart_wifi_scores_sorted, label='Single Protocol (Wifi)', alpha=0.7, linewidth=1, color="#0072B2")
    
if ENABLE_BLUETOOTH:
    baseline_smart_ble_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_partial/single_ble_scenario_result_512_sumo_partial.csv')
    baseline_smart_ble_scores = baseline_smart_ble_df['privacy_score'].values
    baseline_smart_ble_scores_sorted = ensure_min_length_with_zeros(np.sort(baseline_smart_ble_scores))
    baseline_smart_ble_users = np.arange(1, len(baseline_smart_ble_scores_sorted) + 1)
    count_users_privacy_1 = baseline_smart_ble_df[baseline_smart_ble_df['privacy_score'] == 1.0].shape[0]
    count_users_privacy_2 = baseline_smart_ble_df[baseline_smart_ble_df['privacy_score'] >= 0.95].shape[0]
    count_users_privacy_3 = baseline_smart_ble_df[baseline_smart_ble_df['privacy_score'] >= 0.9].shape[0]
    count_users_privacy_4 = baseline_smart_ble_df[baseline_smart_ble_df['privacy_score'] >= 0.8].shape[0]
    print(f"Total number of users for Single BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
    print(f"Total number of users for Single BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
    print(f"Total number of users for Single BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
    print(f"Total number of users for Single BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
    plt.plot(baseline_smart_ble_users, baseline_smart_ble_scores_sorted, label='Single Protocol (Bluetooth)', alpha=0.7, linewidth=1, color="#a6d854", marker='D', markevery=marker_interval,markersize=2)


if ENABLE_LTE:
    baseline_smart_lte_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_partial/single_lte_scenario_result_512_sumo_partial.csv')
    baseline_smart_lte_scores = baseline_smart_lte_df['privacy_score'].values
    baseline_smart_lte_scores_sorted = ensure_min_length_with_zeros(np.sort(baseline_smart_lte_scores))
    baseline_smart_lte_users = np.arange(1, len(baseline_smart_lte_scores_sorted) + 1)
    count_users_privacy_1 = baseline_smart_lte_df[baseline_smart_lte_df['privacy_score'] == 1.0].shape[0]
    count_users_privacy_2 = baseline_smart_lte_df[baseline_smart_lte_df['privacy_score'] >= 0.95].shape[0]
    count_users_privacy_3 = baseline_smart_lte_df[baseline_smart_lte_df['privacy_score'] >= 0.9].shape[0]
    count_users_privacy_4 = baseline_smart_lte_df[baseline_smart_lte_df['privacy_score'] >= 0.8].shape[0]
    print(f"Total number of users for Single LTE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
    print(f"Total number of users for Single LTE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
    print(f"Total number of users for Single LTE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
    print(f"Total number of users for Single LTE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
    plt.plot(baseline_smart_lte_users, baseline_smart_lte_scores_sorted, label='Single Protocol (LTE)', alpha=0.7, linewidth=1, color="#e7298a", marker='^', markevery=marker_interval,markersize=2)




multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_partial/multi_protocol_scenario_result_512_sumo_partial.csv')  
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = ensure_min_length_with_zeros(np.sort(multi_protocol_scores))
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for Multi-protocol with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for Multi-protocol with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for Multi-protocol with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for Multi-protocol with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
scores_less_than_one = multi_protocol_scores_sorted[multi_protocol_scores_sorted < 1.0]

# Print the scores and their count
# print(f"Scores less than 1.0: {scores_less_than_one}")
print(f"Count of scores less than 1.0: {len(scores_less_than_one)}")

multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)

if ENABLE_WIFI and ENABLE_BLUETOOTH and not ENABLE_LTE:
    multi_label = 'Multi-Protocol (LTE, Bluetooth)'
elif ENABLE_BLUETOOTH and ENABLE_LTE and not ENABLE_WIFI:
    multi_label = 'Multi-Protocol (LTE, Bluetooth)'
elif ENABLE_LTE and ENABLE_WIFI and not ENABLE_BLUETOOTH:
    multi_label = 'Multi-Protocol (LTE, WiFi)'
elif ENABLE_LTE and ENABLE_WIFI and ENABLE_BLUETOOTH:
    multi_label = 'Multi-Protocol (LTE, WiFi, Bluetooth)'
else:
    multi_label = None
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label=multi_label, alpha=0.7, linewidth=1, color="#000000", marker='*', markevery=marker_interval,markersize=2)



#SCENARIO_NAME1 = f"scenario_exponential_512_sumo_LB"
multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all5/multi_protocol_scenario_result_512_sumo_all5.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-WIFI-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='Full Coverage (Baseline)', alpha=0.7, linewidth=1, color="#000000", marker='o', markevery=marker_interval,markersize=2)

num_ticks = math.floor(len(multi_protocol_users) / (NUM_USERS / 10))

# Generate exponents spaced linearly between start_exp and end_exp
#exps = np.linspace(start_exp, end_exp, num_ticks)
xticks=[]
for i in range(0,NUM_USERS+1,64):
    if i==0:
        xticks.append(1)
    else:
        xticks.append(i)








plt.xticks(xticks, fontsize=8)
plt.yticks(fontsize=8)
#plt.xscale('log', base=2)
plt.xlabel('Number of Users', fontsize=8)
plt.ylabel('Privacy Leakage', fontsize=8)
plt.legend(loc='lower right', fontsize=5)
plt.grid(True,linewidth=0.2)
plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels

#plt.subplots_adjust(left=0.1, right=0.95, bottom=0.12, top=0.95)
plt.savefig(f'output/images/q3_privacy_leakage_{BASE_SCENARIO_NAME}_partial_ndss.pdf', dpi=600, bbox_inches='tight')
# plt.show()
