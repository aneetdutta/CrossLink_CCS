import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Define marker interval
marker_interval = 50

plt.figure(figsize=(3.3,2.0))



NUM_USERS = 512
BASE_SCENARIO_NAME = f"scenario_proximity_{NUM_USERS}_sumo"


baseline_wifi_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all/baseline_wifi_{BASE_SCENARIO_NAME}_all.csv')
baseline_wifi_scores = baseline_wifi_df['privacy_score'].values
baseline_wifi_scores_sorted = np.sort(baseline_wifi_scores)
baseline_wifi_users = np.arange(1, len(baseline_wifi_scores_sorted) + 1)
count_users_privacy_1 = baseline_wifi_df[baseline_wifi_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = baseline_wifi_df[baseline_wifi_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = baseline_wifi_df[baseline_wifi_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = baseline_wifi_df[baseline_wifi_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for WiFi with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for WiFi with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for WiFi with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for WiFi with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(baseline_wifi_users, baseline_wifi_scores_sorted, label='Naive Baseline (WiFi)', linestyle=':', alpha=0.7, linewidth=1, color="#8A5C20", marker='o', markevery=marker_interval,markersize=2)

baseline_ble_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all/baseline_ble_{BASE_SCENARIO_NAME}_all.csv')
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
plt.plot(baseline_ble_users, baseline_ble_scores_sorted, label='Naive Baseline (Bluetooth)', linestyle=':', alpha=0.7, linewidth=1, color="#ccd5ae", marker='s', markevery=marker_interval,markersize=2)

baseline_lte_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all/baseline_lte_{BASE_SCENARIO_NAME}_all.csv')
baseline_lte_scores = baseline_lte_df['privacy_score'].values
baseline_lte_scores_sorted = np.sort(baseline_lte_scores)
baseline_lte_users = np.arange(1, len(baseline_lte_scores_sorted) + 1)
count_users_privacy_1 = baseline_lte_df[baseline_lte_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(baseline_lte_users, baseline_lte_scores_sorted, label='Naive Baseline (LTE)', linestyle=':', alpha=0.7, linewidth=1, color="#cdb4db", marker='v', markevery=marker_interval,markersize=2)


# Load the CSV files
baseline_wifi_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all/single_wifi_{BASE_SCENARIO_NAME}_all.csv')
baseline_wifi_scores = baseline_wifi_df['privacy_score'].values
baseline_wifi_scores_sorted = np.sort(baseline_wifi_scores)
baseline_wifi_users = np.arange(1, len(baseline_wifi_scores_sorted) + 1)
count_users_privacy_1 = baseline_wifi_df[baseline_wifi_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = baseline_wifi_df[baseline_wifi_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = baseline_wifi_df[baseline_wifi_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = baseline_wifi_df[baseline_wifi_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for WiFi with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for WiFi with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for WiFi with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for WiFi with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(baseline_wifi_users, baseline_wifi_scores_sorted, label='Single Protocol (WiFi)', linestyle=':', alpha=0.7, linewidth=1, color="#66c2a5", marker='o', markevery=marker_interval,markersize=2)

baseline_ble_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all/single_ble_{BASE_SCENARIO_NAME}_all.csv')
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
plt.plot(baseline_ble_users, baseline_ble_scores_sorted, label='Single Protocol (Bluetooth)', linestyle=':', alpha=0.7, linewidth=1, color="#8da0cb", marker='s', markevery=marker_interval,markersize=2)

baseline_lte_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all/single_lte_{BASE_SCENARIO_NAME}_all.csv')
baseline_lte_scores = baseline_lte_df['privacy_score'].values
baseline_lte_scores_sorted = np.sort(baseline_lte_scores)
baseline_lte_users = np.arange(1, len(baseline_lte_scores_sorted) + 1)
count_users_privacy_1 = baseline_lte_df[baseline_lte_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = baseline_lte_df[baseline_lte_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(baseline_lte_users, baseline_lte_scores_sorted, label='Single Protocol (LTE)', linestyle=':', alpha=0.7, linewidth=1, color="#fdc086", marker='v', markevery=marker_interval,markersize=2)

ble_wifi_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_BW/multi_protocol_{BASE_SCENARIO_NAME}_BW.csv')
ble_wifi_scores = ble_wifi_df['privacy_score'].values
ble_wifi_scores_sorted = np.sort(ble_wifi_scores)
ble_wifi_users = np.arange(1, len(ble_wifi_scores_sorted) + 1)
count_users_privacy_1 = ble_wifi_df[ble_wifi_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = ble_wifi_df[ble_wifi_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = ble_wifi_df[ble_wifi_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = ble_wifi_df[ble_wifi_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for BLE-WIFI with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for BLE-WIFI with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for BLE-WIFI with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for BLE-WIFI with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(ble_wifi_users, ble_wifi_scores_sorted, label='Multi-Protocol (WiFi, Bluetooth)', alpha=0.7, linewidth=1, color="#bf5b17", marker='x', markevery=marker_interval,markersize=2)

wifi_lte_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_LW/multi_protocol_{BASE_SCENARIO_NAME}_LW.csv')
wifi_lte_scores = wifi_lte_df['privacy_score'].values
wifi_lte_scores_sorted = np.sort(wifi_lte_scores)
wifi_lte_users = np.arange(1, len(wifi_lte_scores_sorted) + 1)
count_users_privacy_1 = wifi_lte_df[wifi_lte_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = wifi_lte_df[wifi_lte_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = wifi_lte_df[wifi_lte_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = wifi_lte_df[wifi_lte_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-WIFI with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-WIFI with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-WIFI with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-WIFI with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(wifi_lte_users, wifi_lte_scores_sorted, label='Multi-Protocol (LTE, WiFi)', alpha=0.7, linewidth=1, color="#a6d854", marker='D', markevery=marker_interval,markersize=2)

lte_ble_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_LB/multi_protocol_{BASE_SCENARIO_NAME}_LB.csv')
lte_ble_scores = lte_ble_df['privacy_score'].values
lte_ble_scores_sorted = np.sort(lte_ble_scores)
lte_ble_users = np.arange(1, len(lte_ble_scores_sorted) + 1)
count_users_privacy_1 = lte_ble_df[lte_ble_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = lte_ble_df[lte_ble_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = lte_ble_df[lte_ble_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = lte_ble_df[lte_ble_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(lte_ble_users, lte_ble_scores_sorted, label='Multi-Protocol (LTE, Bluetooth)', alpha=0.7, linewidth=1, color="#e7298a", marker='^', markevery=marker_interval,markersize=2)


multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all/multi_protocol_{BASE_SCENARIO_NAME}_all.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='Multi-Protocol (LTE, WiFi, Bluetooth)', alpha=0.7, linewidth=1, color="#000000", marker='*', markevery=marker_interval,markersize=2)

num_ticks = math.floor(len(lte_ble_users) / (NUM_USERS / 10))

# Generate exponents spaced linearly between start_exp and end_exp
#exps = np.linspace(start_exp, end_exp, num_ticks)
xticks=[]
for i in range(0,NUM_USERS+1,64):
    if i==0:
        xticks.append(1)
    else:
        xticks.append(i)

# plt.margins(0)
# plt.autoscale(enable=True, axis='both', tight=True)

#xticks = np.linspace(min(multi_protocol_users), max(multi_protocol_users), math.floor(len(multi_protocol_users)/(NUM_USERS/10)))




#xticks = np.round(xticks).astype(int)
plt.xticks(xticks, fontsize=8)
plt.yticks(fontsize=8)
plt.xlabel('Number of Users', fontsize=8)
plt.ylabel('Privacy Leakage', fontsize=8)
plt.legend(loc='upper left', fontsize=5)
plt.grid(True,linewidth=0.2)
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)




plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels






plt.savefig(f'output/images/privacy_leakage_proximity_{NUM_USERS}.pdf', dpi=600, bbox_inches='tight')
plt.show()
