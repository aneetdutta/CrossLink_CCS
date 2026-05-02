import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage import gaussian_filter1d

plt.figure(figsize=(3.3, 2.1))
marker_interval = 50
# Example file paths (update these with your actual paths)

file_paths = [
    '/path-leakage/output/data/scenario_result_512_sumo_LW/multi_protocol_scenario_result_512_sumo_LW.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_LW1/multi_protocol_scenario_result_512_sumo_LW1.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_LW3/multi_protocol_scenario_result_512_sumo_LW3.csv',
]

# Load and concatenate data
all_data = []
for file in file_paths:
    df = pd.read_csv(file)
    sorted_scores = np.sort(df['privacy_score'])
    interp_scores = np.interp(np.arange(1, 512), np.linspace(1, 512, len(sorted_scores)), sorted_scores)
    all_data.append(interp_scores)

all_data = np.array(all_data)

# Calculate percentiles
p10 = np.percentile(all_data, 10, axis=0)
p25 = np.percentile(all_data, 25, axis=0)
p50 = np.percentile(all_data, 50, axis=0)
p75 = np.percentile(all_data, 75, axis=0)
p90 = np.percentile(all_data, 90, axis=0)

mean_scores = np.mean(all_data, axis=0)

x_common = np.arange(1, 512)


# Plot mean line
sns.lineplot(x=x_common, y=mean_scores, color="#a6d854", linewidth=1.5,marker='D',markevery=marker_interval,markersize=2,label='Multi Protocol (LTE,WiFi)')

# Plot smoothed standard deviation bands
plt.fill_between(x_common, p25, p90, color="#c0e384", alpha=0.4)

file_paths = [
    '/path-leakage/output/data/scenario_result_512_sumo_LB/multi_protocol_scenario_result_512_sumo_LB.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_LB1/multi_protocol_scenario_result_512_sumo_LB1.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_LB3/multi_protocol_scenario_result_512_sumo_LB3.csv',
]

# Load and concatenate data
all_data = []
for file in file_paths:
    df = pd.read_csv(file)
    sorted_scores = np.sort(df['privacy_score'])
    interp_scores = np.interp(np.arange(1, 512), np.linspace(1, 512, len(sorted_scores)), sorted_scores)
    all_data.append(interp_scores)

all_data = np.array(all_data)

# Calculate percentiles
p10 = np.percentile(all_data, 10, axis=0)
p25 = np.percentile(all_data, 25, axis=0)
p50 = np.percentile(all_data, 50, axis=0)
p75 = np.percentile(all_data, 75, axis=0)
p90 = np.percentile(all_data, 90, axis=0)

mean_scores = np.mean(all_data, axis=0)

x_common = np.arange(1, 512)

# Plot mean line
sns.lineplot(x=x_common, y=mean_scores, color='#1f77b4', linewidth=1.5,marker='^',markevery=marker_interval,markersize=2,label='Multi Protocol (LTE,BLE)')

# Plot smoothed standard deviation bands
plt.fill_between(x_common, p25, p90, color="#aec7e8", alpha=0.4)

file_paths = [
    '/path-leakage/output/data/scenario_result_512_sumo_BW/multi_protocol_scenario_result_512_sumo_BW.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_BW1/multi_protocol_scenario_result_512_sumo_BW1.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_BW3/multi_protocol_scenario_result_512_sumo_BW3.csv',
]

# Load and concatenate data
all_data = []
for file in file_paths:
    df = pd.read_csv(file)
    sorted_scores = np.sort(df['privacy_score'])
    interp_scores = np.interp(np.arange(1, 512), np.linspace(1, 512, len(sorted_scores)), sorted_scores)
    all_data.append(interp_scores)

all_data = np.array(all_data)

# Calculate percentiles
p10 = np.percentile(all_data, 10, axis=0)
p25 = np.percentile(all_data, 25, axis=0)
p50 = np.percentile(all_data, 50, axis=0)
p75 = np.percentile(all_data, 75, axis=0)
p90 = np.percentile(all_data, 90, axis=0)

mean_scores = np.mean(all_data, axis=0)

x_common = np.arange(1, 512)


# Plot mean line
sns.lineplot(x=x_common, y=mean_scores, color="#bf5b17", linewidth=1.5,marker='x',markevery=marker_interval,markersize=2,label='Multi Protocol (BLE,WiFi)')

# Plot smoothed standard deviation bands
plt.fill_between(x_common, p25, p90, color="#d9884f", alpha=0.4)


file_paths = [
    '/path-leakage/output/data/scenario_result_512_sumo_all/multi_protocol_scenario_result_512_sumo_all.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all1/multi_protocol_scenario_result_512_sumo_all1.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all3/multi_protocol_scenario_result_512_sumo_all3.csv',
]

# Load and concatenate data
all_data = []
for file in file_paths:
    df = pd.read_csv(file)
    sorted_scores = np.sort(df['privacy_score'])
    interp_scores = np.interp(np.arange(1, 512), np.linspace(1, 512, len(sorted_scores)), sorted_scores)
    all_data.append(interp_scores)

all_data = np.array(all_data)

# Calculate percentiles
p10 = np.percentile(all_data, 10, axis=0)
p25 = np.percentile(all_data, 25, axis=0)
p50 = np.percentile(all_data, 50, axis=0)
p75 = np.percentile(all_data, 75, axis=0)
p90 = np.percentile(all_data, 90, axis=0)

mean_scores = np.mean(all_data, axis=0)

x_common = np.arange(1, 512)

#color="#000000", marker='*'
# Plot mean line
sns.lineplot(x=x_common, y=mean_scores, color="#FFD700", linewidth=1.5,marker='*',markevery=marker_interval,markersize=2,label='Multi Protocol (LTE,BLE,WiFi)')

# Plot smoothed standard deviation bands
plt.fill_between(x_common, p25, p90, color="#FFF8B5", alpha=0.4)

file_paths = [
    '/path-leakage/output/data/scenario_result_512_sumo_all/single_ble_scenario_result_512_sumo_all.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all1/single_ble_scenario_result_512_sumo_all1.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all3/single_ble_scenario_result_512_sumo_all3.csv',
]

# Load and concatenate data
all_data = []
for file in file_paths:
    df = pd.read_csv(file)
    sorted_scores = np.sort(df['privacy_score'])
    interp_scores = np.interp(np.arange(1, 512), np.linspace(1, 512, len(sorted_scores)), sorted_scores)
    all_data.append(interp_scores)

all_data = np.array(all_data)

# Calculate percentiles
p10 = np.percentile(all_data, 10, axis=0)
p25 = np.percentile(all_data, 25, axis=0)
p50 = np.percentile(all_data, 50, axis=0)
p75 = np.percentile(all_data, 75, axis=0)
p90 = np.percentile(all_data, 90, axis=0)

mean_scores = np.mean(all_data, axis=0)

x_common = np.arange(1, 512)

#color="#000000", marker='*'
# Plot mean line


sns.lineplot(x=x_common, y=mean_scores, color="#8da0cb", linewidth=1.5,marker='s',markevery=marker_interval,markersize=2,label='Single Protocol (BLE)')

# Plot smoothed standard deviation bands
plt.fill_between(x_common, p25, p90, color="#bbc7e2", alpha=0.4)

file_paths = [
    '/path-leakage/output/data/scenario_result_512_sumo_all/single_wifi_scenario_result_512_sumo_all.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all1/single_wifi_scenario_result_512_sumo_all1.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all3/single_wifi_scenario_result_512_sumo_all3.csv',
]

# Load and concatenate data
all_data = []
for file in file_paths:
    df = pd.read_csv(file)
    sorted_scores = np.sort(df['privacy_score'])
    interp_scores = np.interp(np.arange(1, 512), np.linspace(1, 512, len(sorted_scores)), sorted_scores)
    all_data.append(interp_scores)

all_data = np.array(all_data)

# Calculate percentiles
p10 = np.percentile(all_data, 10, axis=0)
p25 = np.percentile(all_data, 25, axis=0)
p50 = np.percentile(all_data, 50, axis=0)
p75 = np.percentile(all_data, 75, axis=0)
p90 = np.percentile(all_data, 90, axis=0)

mean_scores = np.mean(all_data, axis=0)

x_common = np.arange(1, 512)

#color="#000000", marker='*'
# Plot mean line


sns.lineplot(x=x_common, y=mean_scores, color="#66c2a5", linewidth=1.5,marker='o',markevery=marker_interval,markersize=2,label='Single Protocol (WiFi)')

# Plot smoothed standard deviation bands
plt.fill_between(x_common, p25, p90, color="#9dd9c9", alpha=0.4)

file_paths = [
    '/path-leakage/output/data/scenario_result_512_sumo_all/single_lte_scenario_result_512_sumo_all.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all1/single_lte_scenario_result_512_sumo_all1.csv',
    '/path-leakage/output/data/scenario_result_512_sumo_all3/single_lte_scenario_result_512_sumo_all3.csv',
]

# Load and concatenate data
all_data = []
for file in file_paths:
    df = pd.read_csv(file)
    sorted_scores = np.sort(df['privacy_score'])
    interp_scores = np.interp(np.arange(1, 512), np.linspace(1, 512, len(sorted_scores)), sorted_scores)
    all_data.append(interp_scores)

all_data = np.array(all_data)

# Calculate percentiles
p10 = np.percentile(all_data, 10, axis=0)
p25 = np.percentile(all_data, 25, axis=0)
p50 = np.percentile(all_data, 50, axis=0)
p75 = np.percentile(all_data, 75, axis=0)
p90 = np.percentile(all_data, 90, axis=0)

mean_scores = np.mean(all_data, axis=0)

x_common = np.arange(1, 512)

#color="#000000", marker='*'
# Plot mean line

#color="#fdc086", marker='v'
sns.lineplot(x=x_common, y=mean_scores, color="#8C78A1", linewidth=1.5,marker='v',markevery=marker_interval,markersize=2,label='Single Protocol (LTE)')

# Plot smoothed standard deviation bands
plt.fill_between(x_common, p25, p90, color="#B5A2C8", alpha=0.4)






xticks=[]
for i in range(0,512+1,64):
    if i==0:
        xticks.append(1)
    else:
        xticks.append(i)
#exps=[0,7,8,9]
# Convert exponents back to numbers: ~ powers of 2
#xticks = [2**exp for exp in exps]

   # xticks = xticks[::step]
LTE_bound=193.00967935792022
#star_x_position = 256  # Example position, adjust as needed
#plt.scatter(LTE_bound, 1.0, marker='+', color='green', s=10, zorder=5,label='Expected lower bound of LTE')
#plt.axvline(x=LTE_bound, color='red', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in LTE')

#LTE_ubound=321.0179
#plt.axvline(x=LTE_ubound, color='red', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in LTE')

BLE_bound=39.31876996624587
#plt.scatter(BLE_bound, 1.0, marker='+', color='blue', s=10, zorder=5,label='Expected lower bound of BLE')
#plt.axvline(x=BLE_bound, color='blue', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in BLE')

#BLE_ubound=88.5470
#plt.axvline(x=BLE_ubound, color='blue', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in BLE')


plt.xticks(xticks, fontsize=8)
plt.yticks(fontsize=8)
#plt.xscale('log', base=2)
plt.xlabel('Number of Users', fontsize=8)
plt.ylabel('Privacy Leakage', fontsize=8)
plt.legend(loc='lower right', fontsize=5)
plt.grid(True,linewidth=0.2)
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)




plt.rc('savefig', bbox='tight')
plt.rc('savefig', pad_inches=0.02) # 0 and 0.01 crop the frame/axis labels
#plt.subplots_adjust(left=0, right=1, bottom=0, top=1)
plt.savefig(f'privacy_leakage_q1_512_band.pdf', dpi=600, bbox_inches='tight')
plt.show()
