import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.figure(figsize=(3.3,2.1))
# Read data from CSV files
file1 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB/multi_protocol_scenario_result_512_sumo_LB.csv'
file2 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB1/multi_protocol_scenario_result_512_sumo_LB1.csv'
file3 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB2/multi_protocol_scenario_result_512_sumo_LB2.csv'
file4 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB3/multi_protocol_scenario_result_512_sumo_LB3.csv'
file5 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB4/multi_protocol_scenario_result_512_sumo_LB4.csv'

df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df3 = pd.read_csv(file3)
df4 = pd.read_csv(file4)
df5 = pd.read_csv(file5)

# Sort the privacy scores for cumulative plotting
privacy_scores1_sorted = np.sort(df1['privacy_score'])
privacy_scores2_sorted = np.sort(df2['privacy_score'])
privacy_scores3_sorted = np.sort(df3['privacy_score'])
privacy_scores4_sorted = np.sort(df4['privacy_score'])
privacy_scores5_sorted = np.sort(df5['privacy_score'])

# Common x-axis: sample index (1-512)
x_common = np.arange(1, 512)

# Interpolate privacy scores to align them on the common x-axis
privacy1_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores1_sorted)), privacy_scores1_sorted)
privacy2_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores2_sorted)), privacy_scores2_sorted)
privacy3_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores3_sorted)), privacy_scores3_sorted)
privacy4_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores4_sorted)), privacy_scores4_sorted)
privacy5_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores5_sorted)), privacy_scores5_sorted)

# Calculate band (min and max values between the two distributions)
privacy_min_multi = np.minimum.reduce([privacy1_interp, privacy2_interp,privacy3_interp,privacy4_interp,privacy5_interp])
privacy_max_multi = np.maximum.reduce([privacy1_interp, privacy2_interp,privacy3_interp,privacy4_interp,privacy5_interp])

# Plot the individual lines and the shaded band
#plt.figure(figsize=(12, 6))
#plt.plot(x_common, privacy1_interp,alpha=0.6)
#plt.plot(x_common, privacy2_interp,alpha=0.6)
#plt.plot(x_common, privacy3_interp,alpha=0.6)
#plt.plot(x_common, privacy4_interp,alpha=0.6)
#plt.plot(x_common, privacy5_interp,alpha=0.6)

# Shaded band representing variability
plt.fill_between(x_common, privacy_min_multi, privacy_max_multi, color="#000000", alpha=0.6, label='Multiprotocol (LTE,Bluetooth)')


file1 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB/single_lte_scenario_result_512_sumo_LB.csv'
file2 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB1/single_lte_scenario_result_512_sumo_LB1.csv'
file3 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB2/single_lte_scenario_result_512_sumo_LB2.csv'
file4 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB3/single_lte_scenario_result_512_sumo_LB3.csv'
file5 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB4/single_lte_scenario_result_512_sumo_LB4.csv'


df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df3 = pd.read_csv(file3)
df4 = pd.read_csv(file4)
df5 = pd.read_csv(file5)

# Sort the privacy scores for cumulative plotting
privacy_scores1_sorted = np.sort(df1['privacy_score'])
privacy_scores2_sorted = np.sort(df2['privacy_score'])
privacy_scores3_sorted = np.sort(df3['privacy_score'])
privacy_scores4_sorted = np.sort(df4['privacy_score'])
privacy_scores5_sorted = np.sort(df5['privacy_score'])

# Common x-axis: sample index (1-512)
x_common = np.arange(1, 512)

# Interpolate privacy scores to align them on the common x-axis
privacy1_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores1_sorted)), privacy_scores1_sorted)
privacy2_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores2_sorted)), privacy_scores2_sorted)
privacy3_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores3_sorted)), privacy_scores3_sorted)
privacy4_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores4_sorted)), privacy_scores4_sorted)
privacy5_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores5_sorted)), privacy_scores5_sorted)

# Calculate band (min and max values between the two distributions)
privacy_min_lte = np.minimum.reduce([privacy1_interp, privacy2_interp,privacy3_interp,privacy4_interp,privacy5_interp])
privacy_max_lte = np.maximum.reduce([privacy1_interp, privacy2_interp,privacy3_interp,privacy4_interp,privacy5_interp])

# Plot the individual lines and the shaded band
#plt.figure(figsize=(12, 6))
#plt.plot(x_common, privacy1_interp,alpha=0.6)
#plt.plot(x_common, privacy2_interp,alpha=0.6)
#plt.plot(x_common, privacy3_interp,alpha=0.6)
#plt.plot(x_common, privacy4_interp,alpha=0.6)
#plt.plot(x_common, privacy5_interp,alpha=0.6)

# Shaded band representing variability
plt.fill_between(x_common, privacy_min_lte, privacy_max_lte, color="#fdc086", alpha=0.6, label='Single Protocol (LTE)')


file1 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB/single_ble_scenario_result_512_sumo_LB.csv'
file2 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB1/single_ble_scenario_result_512_sumo_LB1.csv'
file3 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB2/single_ble_scenario_result_512_sumo_LB2.csv'
file4 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB3/single_ble_scenario_result_512_sumo_LB3.csv'
file5 = '/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_result_512_sumo_LB4/single_ble_scenario_result_512_sumo_LB4.csv'


df1 = pd.read_csv(file1)
df2 = pd.read_csv(file2)
df3 = pd.read_csv(file3)
df4 = pd.read_csv(file4)
df5 = pd.read_csv(file5)

# Sort the privacy scores for cumulative plotting
privacy_scores1_sorted = np.sort(df1['privacy_score'])
privacy_scores2_sorted = np.sort(df2['privacy_score'])
privacy_scores3_sorted = np.sort(df3['privacy_score'])
privacy_scores4_sorted = np.sort(df4['privacy_score'])
privacy_scores5_sorted = np.sort(df5['privacy_score'])

# Common x-axis: sample index (1-512)
x_common = np.arange(1, 512)

# Interpolate privacy scores to align them on the common x-axis
privacy1_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores1_sorted)), privacy_scores1_sorted)
privacy2_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores2_sorted)), privacy_scores2_sorted)
privacy3_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores3_sorted)), privacy_scores3_sorted)
privacy4_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores4_sorted)), privacy_scores4_sorted)
privacy5_interp = np.interp(x_common, np.linspace(1, 512, len(privacy_scores5_sorted)), privacy_scores5_sorted)

# Calculate band (min and max values between the two distributions)
privacy_min_ble = np.minimum.reduce([privacy1_interp, privacy2_interp,privacy3_interp,privacy4_interp,privacy5_interp])
privacy_max_ble = np.maximum.reduce([privacy1_interp, privacy2_interp,privacy3_interp,privacy4_interp,privacy5_interp])

# Plot the individual lines and the shaded band
#plt.figure(figsize=(12, 6))
#plt.plot(x_common, privacy1_interp,alpha=0.6)
#plt.plot(x_common, privacy2_interp,alpha=0.6)
#plt.plot(x_common, privacy3_interp,alpha=0.6)
#plt.plot(x_common, privacy4_interp,alpha=0.6)
#plt.plot(x_common, privacy5_interp,alpha=0.6)

# Shaded band representing variability
plt.fill_between(x_common, privacy_min_ble, privacy_max_ble, color="#a6d854", alpha=0.6, label='Single Protocol (BLE)')




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
plt.axvline(x=LTE_bound, color='red', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in LTE')

LTE_ubound=321.0179
plt.axvline(x=LTE_ubound, color='red', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in LTE')

BLE_bound=39.31876996624587
plt.axvline(x=BLE_bound, color='blue', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in BLE')

BLE_ubound=88.5470
plt.axvline(x=BLE_ubound, color='blue', linestyle='--', linewidth=1, label=f'Number of devices mixes atleast once in BLE')


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
