import os, sys
sys.path.append(os.getcwd())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# Define marker interval
marker_interval = 50

plt.figure(figsize=(3.3,1.1))

NUM_USERS = 512
#SCENARIO_NAME1 = f"scenario_exponential_512_sumo_LB"
##SCENARIO_NAME2 = f"q3_localization_error_high"
#SCENARIO_NAME3 = f"q3_localization_error_low"
#SCENARIO_NAME4 = f"scenario_q2_ri_same_ti_high"
#SCENARIO_NAME5 = f"scenario_q2_ri_low_ti_low"
SCENARIO_NAME = f"scenario_result_{NUM_USERS}_sumo"

multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME}_high/multi_protocol_scenario_result_512_sumo_high.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='LTE: 78m, WiFi: 10m ,BLE: 5m', alpha=0.7, linewidth=1, color="#e7298a", marker='^', markevery=marker_interval,markersize=2)


multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME}_all1/multi_protocol_scenario_result_512_sumo_all1.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='LTE: 10m, WiFi: 5m ,BLE: 1.5m (Baseline)', alpha=0.7, linewidth=1, color="#000000", marker='*', markevery=marker_interval,markersize=2)



multi_protocol_df = pd.read_csv(f'output/data/{SCENARIO_NAME}_low/multi_protocol_scenario_result_512_sumo_low.csv')
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
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='LTE: 1m, WiFi: 1m ,BLE: 1 m', alpha=0.7, linewidth=1, color="#a6d854", marker='D', markevery=marker_interval,markersize=2)


num_ticks = math.floor(len(multi_protocol_users) / (NUM_USERS / 10))

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

#xticks = np.linspace(min(multi_protocol_users), max(multi_protocol_users), math.floor(len(multi_protocol_users)/50))
yticks=[0,0.2,0.4,0.6,0.8,1.0]
#xticks = np.round(xticks).astype(int)
plt.xticks(xticks, fontsize=8)
plt.yticks(fontsize=8)
plt.xlabel('Number of Users', fontsize=8)
plt.ylabel('Privacy Leakage', fontsize=8)
plt.legend(loc='lower right', fontsize=5)
plt.grid(True,linewidth=0.2)



#7 Inches it the entire page, 3.33 is a column and 2.1 works if you want 3 next to each other with decent spacing
plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels



#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.savefig(f'output/images/privacy_leakage_q3_localization_ccs.pdf', dpi=600, bbox_inches='tight')
plt.show()
