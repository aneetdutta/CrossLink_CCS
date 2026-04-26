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
BASE_SCENARIO_NAME = f"scenario_result_{NUM_USERS}_sumo"
# Load the CSV files
#single_ble_scenario_result_512_sumo_all5








multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all1/multi_protocol_scenario_result_512_sumo_all1.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE-Wifi with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='CrossLink with uncertainity modeling', alpha=0.7, linewidth=1, color="#000000", marker='*', markevery=marker_interval,markersize=2)

multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all_nom/multi_protocol_scenario_result_512_sumo_all_nom.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE-Wifi with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='No mobility modeling', alpha=0.7, linewidth=1, color="#bf5b17", marker='s', markevery=marker_interval,markersize=2)

multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all_noloc/multi_protocol_scenario_result_512_sumo_all_noloc.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE-Wifi with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='No localization unceratinity modeling', alpha=0.7, linewidth=1, color="#e7298a", marker='^', markevery=marker_interval,markersize=2)

multi_protocol_df = pd.read_csv(f'output/data/{BASE_SCENARIO_NAME}_all_nomloc/multi_protocol_scenario_result_512_sumo_all_nomloc.csv')
multi_protocol_scores = multi_protocol_df['privacy_score'].values
multi_protocol_scores_sorted = np.sort(multi_protocol_scores)
multi_protocol_users = np.arange(1, len(multi_protocol_scores_sorted) + 1)
count_users_privacy_1 = multi_protocol_df[multi_protocol_df['privacy_score'] == 1.0].shape[0]
count_users_privacy_2 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.95].shape[0]
count_users_privacy_3 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.9].shape[0]
count_users_privacy_4 = multi_protocol_df[multi_protocol_df['privacy_score'] >= 0.8].shape[0]
print(f"Total number of users for LTE-BLE-Wifi with privacy_score == 1.0: {count_users_privacy_1} - Percentage: {count_users_privacy_1/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.95: {count_users_privacy_2} - Percentage: {count_users_privacy_2/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.9: {count_users_privacy_3} - Percentage: {count_users_privacy_3/NUM_USERS}")
print(f"Total number of users for LTE-BLE-Wifi with privacy_score >= 0.8: {count_users_privacy_4} - Percentage: {count_users_privacy_4/NUM_USERS}")
plt.plot(multi_protocol_users, multi_protocol_scores_sorted, label='No uncertainty modeling', alpha=0.7, linewidth=1, color="#a6d854", marker='D', markevery=marker_interval,markersize=2)








#BLE_b=int(12)
#plt.axvline(x=BLE_b, color='#1f77b4', linestyle='--', linewidth=1, label=f'Non-trackable users in BLE')

#LTE_b=int(93)
#plt.axvline(x=LTE_b, color='#ff7f0e', linestyle='--', linewidth=1, label=f'Non-trackable users in LTE')



#wifi_b=int(510)
#plt.axvline(x=wifi_b, color='#2ca02c', linestyle='--', linewidth=1, label=f'Non-trackable users in WiFi')

#lte_ble_b=int(5)
#plt.axvline(x=lte_ble_b, color='#9467bd', linestyle='--', linewidth=1, label=f'Non-trackable users in LTE+BLE')

#lte_wifi_b=int(93)
#plt.axvline(x=lte_wifi_b, color='#8c564b', linestyle='--', linewidth=1, label=f'Non-trackable users in LTE+WiFi')



#ble_wifi_b=int(12)
#plt.axvline(x=ble_wifi_b, color='#d62728', linestyle='--', linewidth=1, label=f'Non-trackable users in BLE+WiFi')

#lte_ble_wifi_b=int(5)
#plt.axvline(x=lte_ble_wifi_b, color='#000000', linestyle='--', linewidth=1, label=f'Non-trackable users in LTE+BLE+WiFi')



# plt.margins(0)
# plt.autoscale(enable=True, axis='both', tight=True)


#xticks = np.linspace(min(multi_protocol_users), max(multi_protocol_users), math.floor(len(multi_protocol_users)/(NUM_USERS/10)))
#xticks = np.round(xticks).astype(int)
#min_val = 1
#max_val = NUM_USERS

#start_exp = math.log2(min_val)  # start (float)
#end_exp   = math.log2(max_val)  # end   (float)

# Number of ticks (you can adjust as needed)

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
#xticks = np.round(xticks).astype(int)

plt.xticks(xticks, fontsize=8)
plt.yticks(fontsize=8)
#plt.xscale('log', base=2)
plt.xlabel('Number of Users', fontsize=8)
plt.ylabel('Privacy Leakage', fontsize=8)
#plt.legend(loc='lower right', fontsize=5)
plt.grid(True,linewidth=0.2)
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
leg = plt.legend(
    loc='upper center',
    bbox_to_anchor=(0.5, -0.25),  # below the axes
    ncol=2,                       # or 3, depending on how many items
    fontsize=5,
    frameon=False
)

plt.subplots_adjust(bottom=0.28)
plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels

#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.savefig(f'output/images/privacy_leakage_abalation_ccs.pdf', dpi=600, bbox_inches='tight')
plt.show()
