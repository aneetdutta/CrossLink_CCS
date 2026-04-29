import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Define marker interval
marker_interval = 50

plt.figure(figsize=(3.3,1.8))

NUM_USERS = 512
#SCENARIO_NAME1 = f"scenario_exponential_512_sumo_LB"
#SCENARIO_NAME2 = f"scenario_q2_ri_low_ti_high"
#SCENARIO_NAME3 = f"scenario_q2_ri_low_ti_same"
#SCENARIO_NAME4 = f"scenario_q2_ri_same_ti_high"
#SCENARIO_NAME5 = f"scenario_q2_ri_low_ti_low"
#SCENARIO_NAME6 = f"q4_mobility_512_sumo_1-5_LB"
BASE_SCENARIO_NAME = f"scenario_result_{NUM_USERS}_sumo"

STYLE = {
    "sync_300":   dict(color="#1f77b4", marker="^"),  # triangle up
    "baseline":   dict(color="#000000", marker="o"),  # circle
    "sync_600":   dict(color="#ff7f0e", marker="D"),  # diamond
    "sync_180":   dict(color="#2ca02c", marker="s"),  # square
    "mixing":     dict(color="#d62728", marker="v"),  # triangle down
    "naive_ble":  dict(color="#9467bd", marker="P"),  # plus-filled
    "naive_wifi": dict(color="#8c564b", marker="X"),  # x-filled
    "naive_lte":  dict(color="#e377c2", marker="*"),  # star
}

multi_protocol_df = pd.read_csv(f'/output/data/{BASE_SCENARIO_NAME}_synchronized_low_ti/multi_protocol_{BASE_SCENARIO_NAME}_synchronized_low_ti.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='Local Synchronization (300 s)', alpha=0.7, linewidth=1,markevery=marker_interval, markersize=2, **STYLE["sync_300"])


multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all1/multi_protocol_{BASE_SCENARIO_NAME}_all1.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted,label='No-synchronization (Baseline)', alpha=0.7, linewidth=1,markevery=marker_interval, markersize=2, **STYLE["baseline"])

multi_protocol_df = pd.read_csv(f'/output/data/scenario_synced_randomization_512_all/multi_protocol_scenario_synced_randomization_512_all.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted,label='Local Synchronization (600 s)', alpha=0.7, linewidth=1,markevery=marker_interval, markersize=2, **STYLE["sync_600"])


multi_protocol_df = pd.read_csv(f'/output/data/synchronized_high_ti/multi_protocol_synchronized_high_ti.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted,label='Local Synchronization (180 s)', alpha=0.7, linewidth=1,markevery=marker_interval, markersize=2, **STYLE["sync_180"])

multi_protocol_df = pd.read_csv(f'/output/data/scenario_proximity_512_sumo_new/multi_protocol_scenario_proximity_512_sumo_new.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted,label='Perfect Mixing', alpha=0.7, linewidth=1,markevery=marker_interval, markersize=2, **STYLE["mixing"])


single_protocol_df = pd.read_csv(f'/output/data/scenario_proximity_512_sumo_new/single_ble_scenario_proximity_512_sumo_new.csv')
single_protocol_scores = single_protocol_df['privacy_score'].values
single_protocol_scores_sorted = np.sort(single_protocol_scores)
single_protocol_users = np.arange(1, len(single_protocol_scores_sorted) + 1)
count_users_privacy_1 = single_protocol_df[single_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-WIFI-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(single_protocol_users, single_protocol_scores_sorted, label='Single Protocol (BLE)', alpha=0.7, linewidth=1, color="#a6d854", marker='D', markevery=marker_interval,markersize=2)

single_protocol_df = pd.read_csv(f'/output/data/scenario_proximity_512_sumo_new/single_wifi_scenario_proximity_512_sumo_new.csv')
single_protocol_scores = single_protocol_df['privacy_score'].values
single_protocol_scores_sorted = np.sort(single_protocol_scores)
single_protocol_users = np.arange(1, len(single_protocol_scores_sorted) + 1)
count_users_privacy_1 = single_protocol_df[single_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-WIFI-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(single_protocol_users, single_protocol_scores_sorted,label='Single Protocol (WiFi)', alpha=0.7, linewidth=1,markevery=marker_interval, markersize=2, **STYLE["naive_wifi"])

single_protocol_df = pd.read_csv(f'/output/data/scenario_proximity_512_sumo_new/single_lte_scenario_proximity_512_sumo_new.csv')
single_protocol_scores = single_protocol_df['privacy_score'].values
single_protocol_scores_sorted = np.sort(single_protocol_scores)
single_protocol_users = np.arange(1, len(single_protocol_scores_sorted) + 1)
count_users_privacy_1 = single_protocol_df[single_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = single_protocol_df[single_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-WIFI-BLE with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-WIFI-BLE with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(single_protocol_users, single_protocol_scores_sorted,label='Single Protocol (LTE)', alpha=0.7, linewidth=1,markevery=marker_interval, markersize=2, **STYLE["naive_lte"])








xticks=[]
for i in range(0,NUM_USERS+1,64):
    if i==0:
        xticks.append(1)
    else:
        xticks.append(i)

# plt.margins(0)
# plt.autoscale(enable=True, axis='both', tight=True)

#xticks = np.linspace(min(multi_protocol_users), max(multi_protocol_users), math.floor(len(multi_protocol_users)/50))
#xticks = np.round(xticks).astype(int)
plt.xticks(xticks, fontsize=8)
plt.yticks(fontsize=8)
plt.xlabel('Number of Users', fontsize=8)
plt.ylabel('Privacy Leakage', fontsize=8)
plt.legend(loc='lower right', fontsize=5)
#plt.grid(True)

#plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=15)
#plt.legend(loc='lower center', bbox_to_anchor=(0.65, 0), ncol=1, fontsize=5)
plt.grid(True,linewidth=0.2)
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)




plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels

#plt.subplots_adjust(left=0, right=1, bottom=0.35, top=1)  
#plt.tight_layout()

#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.savefig(f'output/images/privacy_leakage_countermeasure_usenix.pdf', dpi=600, bbox_inches='tight')
plt.show()
