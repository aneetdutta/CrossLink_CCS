import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Define marker interval
marker_interval = 50

plt.figure(figsize=(1.6,1.5))

NUM_USERS = 512
BASE_SCENARIO_NAME = f"scenario_result_{NUM_USERS}_sumo"
def ensure_min_length_with_zeros(array, min_length=NUM_USERS):
    array_sorted = np.sort(array)
    if len(array_sorted) < min_length:
        zeros_to_add = min_length - len(array_sorted)
        array_sorted = np.append(array_sorted, [0] * zeros_to_add)
    return np.sort(array_sorted)





#scenario_result_512_sumo_partial
# Load the CSV files
#single_ble_scenario_result_512_sumo_all5
#privacy_leakage_scenario_result_512_sumo_partial
baseline_ble_df = pd.read_csv(f'output/data/scenario_result_512_sumo_partial/multi_protocol_scenario_result_512_sumo_partial.csv')
baseline_ble_scores = baseline_ble_df['privacy_score'].values
baseline_ble_scores_sorted = np.sort(baseline_ble_scores)
baseline_ble_users = np.arange(1, len(baseline_ble_scores_sorted) + 1)
count_users_privacy_1 = baseline_ble_df[baseline_ble_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = baseline_ble_df[baseline_ble_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = baseline_ble_df[baseline_ble_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = baseline_ble_df[baseline_ble_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(baseline_ble_users, baseline_ble_scores_sorted, label=r'$\mathit{PATCH}$', alpha=0.7, linewidth=1, color="#8da0cb", marker='s', markevery=marker_interval,markersize=2)

baseline_lte_df = pd.read_csv(f'output/data/scenario_partial_512_sumo_user1/multi_protocol_scenario_partial_512_sumo_user1.csv')
baseline_lte_scores = baseline_lte_df['privacy_score'].values
baseline_lte_scores_sorted = np.sort(baseline_lte_scores)
baseline_lte_users = np.arange(1, len(baseline_lte_scores_sorted) + 1)
count_users_privacy_1 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.8].shape[0]
count_users_privacy_2 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.7].shape[0]
count_users_privacy_3 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.6].shape[0]
count_users_privacy_4 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.5].shape[0]
print(f"Total number of users for MOB with privacy_score >= 0.8: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for MOB with privacy_score >= 0.7: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for MOB with privacy_score >= 0.6: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for MOB with privacy_score >= 0.5: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(baseline_lte_users, baseline_lte_scores_sorted, label=r'$\mathit{MOB}$', alpha=0.7, linewidth=1, color="#fdc086", marker='v', markevery=marker_interval,markersize=2)


multi_protocol_df = pd.read_csv(f'output/data/scenario_partial_512_sumo_hostrategic/multi_protocol_scenario_partial_512_sumo_hostrategic.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
#plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label=r'$\mathit{SPOT}$', alpha=0.7, linewidth=1, color="#d62728", marker='*', markevery=marker_interval,markersize=2)

multi_protocol_df = pd.read_csv(f'output/data/scenario_partial_512_sumo_timestrategic/multi_protocol_scenario_partial_512_sumo_timestrategic.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label=r'$\mathit{RAND}$', alpha=0.7, linewidth=1, color="#9467bd", marker='*', markevery=marker_interval,markersize=2)


multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all1/multi_protocol_scenario_result_512_sumo_all1.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
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
#exps=[0,7,8,9]
# Convert exponents back to numbers: ~ powers of 2
#xticks = [2**exp for exp in exps]

   # xticks = xticks[::step]


plt.xticks(xticks, fontsize=4)
plt.yticks(fontsize=4)
#plt.xscale('log', base=2)
plt.xlabel('Number of Users', fontsize=8)
plt.ylabel('Privacy Leakage', fontsize=8)
plt.legend(loc='lower right', fontsize=5)
plt.grid(True,linewidth=0.2)
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)




plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.savefig(f'output/images/privacy_leakage_q3_{NUM_USERS}_partial_usenix1.pdf', dpi=600, bbox_inches='tight')
plt.show()
