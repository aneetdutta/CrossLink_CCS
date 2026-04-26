import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Define marker interval
marker_interval = 50

plt.figure(figsize=(2,1.5))

NUM_USERS = 512
SCENARIO_NAME1 = f"scenario_exponential_512_sumo_LB"
SCENARIO_NAME2 = f"scenario_mobility_512_sumo_3_LB"
SCENARIO_NAME3 = f"scenario_mobility_512_sumo_5_LB"
SCENARIO_NAME4 = f"scenario_mobility_512_sumo_10_LB"
SCENARIO_NAME5 = f"q4_scenario_exponential_512_sumo_LB"
SCENARIO_NAME6 = f"q4_mobility_512_sumo_3_LB"
SCENARIO_NAME7 = f"q4_mobility_512_sumo_5_LB"
SCENARIO_NAME8 = f"q4_mobility_512_sumo_10_LB"
BASE_SCENARIO_NAME = f"scenario_result_{NUM_USERS}_sumo"
#SCENARIO_NAME5 = f"scenario_q2_ri_low_ti_low"

multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all1/multi_protocol_scenario_result_512_sumo_all1.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='MP Vmax = 1.6 m/s (Baseline)', alpha=0.7, linewidth=1, color="#000000", marker='*', markevery=marker_interval,markersize=2)

multi_protocol_df = pd.read_csv(f'output/data/scenario_result_512_sumo_moving10/multi_protocol_scenario_result_512_sumo_moving10.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='MP Vmax = 10 m/s', alpha=0.7, linewidth=1, color="#fdc086", marker='D', markevery=marker_interval,markersize=2)


multi_protocol_df = pd.read_csv(f'output/data/scenario_result_512_sumo_moving5/multi_protocol_scenario_result_512_sumo_moving5.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='MP Vmax = 5 m/s', alpha=0.7, linewidth=1, color="#e7298a", marker='^', markevery=marker_interval,markersize=2)


multi_protocol_df = pd.read_csv(f'output/data/scenario_result_512_sumo_moving3/multi_protocol_scenario_result_512_sumo_moving3.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='MP Vmax = 3 m/s', alpha=0.7, linewidth=1, color="#a6d854", marker='D', markevery=marker_interval,markersize=2)

multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME4}/multi_protocol_{SCENARIO_NAME4}.csv')
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
#plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='MP Vmax = 10 m/s', alpha=0.7, linewidth=1, color="#bf5b17", marker='o', markevery=marker_interval,markersize=2)

#multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME5}/multi_protocol_{SCENARIO_NAME5}.csv')
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
#plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='Multi-Protocol Vmax:1.6 m/s, TI: 30 s', alpha=0.7, linewidth=3, color="#fdc086", marker='o', markevery=marker_interval)

multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME6}/multi_protocol_{SCENARIO_NAME6}.csv')
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
#plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='Multi-Protocol Vmax:3 m/s, TI: 30 s', alpha=0.7, linewidth=3, color="#fdc086", marker='o', markevery=marker_interval)


multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME7}/multi_protocol_{SCENARIO_NAME7}.csv')
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
#plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='Multi-Protocol Vmax:5 m/s, TI: 30 s', alpha=0.7, linewidth=3, color="#fdc086", marker='o', markevery=marker_interval)

multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME8}/multi_protocol_{SCENARIO_NAME8}.csv')
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
#plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='Multi-Protocol Vmax:10 m/s, TI: 30 s', alpha=0.7, linewidth=3, color="#fdc086", marker='o', markevery=marker_interval)

num_ticks = math.floor(len(multi_protocol_users) / (NUM_USERS / 10))

# Generate exponents spaced linearly between start_exp and end_exp
#exps = np.linspace(start_exp, end_exp, num_ticks)
xticks=[]
for i in range(0,NUM_USERS+1,128):
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
plt.grid(True,linewidth=0.2)
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)




plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels


#plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, fontsize=15)

#plt.grid(True)
#plt.subplots_adjust(left=0, right=1, bottom=0.35, top=1)  


#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.savefig(f'output/images/privacy_leakage_q4_mobility_ccs.pdf', dpi=600, bbox_inches='tight')
plt.show()
