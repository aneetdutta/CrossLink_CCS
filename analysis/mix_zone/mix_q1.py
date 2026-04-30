import csv
import pandas as pd
from collections import defaultdict
import numpy as np
import math



def upper_bound(lambda_r,lambda_t,T):
    a=0.5
    A = lambda_r - lambda_t
    B = lambda_r + lambda_t
    A_mod=lambda_t-lambda_r
    C1 = (1 / B) + (lambda_t / B**2)   
    C2=lambda_r/A_mod
    C3=(A_mod**2)*B
    C4=((2*lambda_r**2)*lambda_t)
    print("--")
    print(C4)
    p_mix=(lambda_r*C1)
    print("--")
    
    #C = 1.0 / B + lambda_t / B**2
    
    #p_mix=lambda_r * C
    u=np.exp(-2*lambda_r*T*p_mix)
    #u=(1-p_mix)**k
    #upper_bound=np.exp(-lambda_r * T) * (1 - p_mix)+p_mix
     
    #p_ub=lambda_r*C1  
    u=np.exp(-2*lambda_r*T*p_mix)
    upper_bound=1-u
    
    #upper_bound=1-p_ub
    #upper_bound=
    #upper_bound=k*p_mix
    #print(upper_bound)
    return upper_bound
    
    
    

def upper_bound_wifi(lambda_r,T):

    p_mix=0.25
    u=np.exp(-2*lambda_r*T*p_mix)
    upper_bound=1-u
    
    #upper_bound=1-p_ub
    #upper_bound=
    #upper_bound=k*p_mix
    print(upper_bound)
    return upper_bound

neighbor_file1 = ""
neighbor_file2 = ""
neighbor_file3 = ""
output_csv = ''
scores_file = ""

''' Parameters for BLE'''
lambdar_r_ble=0.00303030303 #(600 seconds)
lambda_t_ble=0.2 #(1 minute)

''' Parameters for LTE'''
lambdar_r_lte=0.00208333333 #(900 seconds)
lambda_t_lte=0.33 #(1 minute)


''' Parameters for WiFi'''
lambdar_r_wf=0.1 #(600 seconds)
lambda_t_wf=0.1 #(1 minute)

df_scores=pd.read_csv(scores_file)
df = pd.read_csv(neighbor_file1)

df_lte=pd.read_csv(neighbor_file2)

df_wifi=pd.read_csv(neighbor_file3)

unique_users_array = df_scores['user_id'].unique()

# List of unique users
unique_user_list = unique_users_array.tolist()

mixing_users=0
mixing_users_lte=0
mixing_users_ble=0
mixing_users_wifi=0

users_mix=[]

for user in unique_user_list:
    
    user_rows = df[df['user_id'] == user]
    
    user_rows_lte=df_lte[df_lte['user_id']==user]
    
    user_rows_wifi=df_wifi[df_wifi['user_id']==user]
    
    
    # if no mixing happened for an user in BLE
    if user_rows.empty:
        #print(user)
        T=0   
        upper_ble=0
    if user_rows_lte.empty:
        #print(user)
        T_lte=0   
        upper_ble=0
    else:
        durations = user_rows['duration_seconds'].tolist()
        # Calculate the total mixing time in BLE for the user
        upper_ble=0
        #for item in durations:
         #   upper_ble=upper_ble+upper_bound(lambdar_r_ble,lambda_t_ble,item)
        T=sum(durations)
    # if no mixing happened for an user in BLE    
    if user_rows_lte.empty:
        upper_lte=0
    else:
        durations1 = user_rows_lte['duration_seconds'].tolist()
        upper_lte=0
        #for item in durations1:
         #   upper_lte=upper_lte+upper_bound(lambdar_r_lte,lambda_t_lte,item)
        
        # Calculate the total mixing time in LTE for the user
        T_lte=sum(durations1)
    if user_rows_wifi.empty:
        upper_wifi=0
    else:
        durations2 = user_rows_wifi['duration_seconds'].tolist()
        T_wifi=sum(durations2)
    
    
        
    # probability of mixing atleast once during the mix-zone duration T
    upper_ble=upper_bound(lambdar_r_ble,lambda_t_ble,T)
    
    
    upper_lte=upper_bound(lambdar_r_lte,lambda_t_lte,T_lte)
    
    upper_wifi=upper_bound_wifi(lambdar_r_wf,T_wifi)
    
    upper_lte1=upper_bound(lambdar_r_lte,lambda_t_lte,T)
    upper=upper_ble*upper_lte
    users_mix.append([user,upper])
    mixing_users=mixing_users+upper
    mixing_users_lte=mixing_users_lte+upper_lte
    mixing_users_ble=mixing_users_ble+upper_ble#_no_mix
    mixing_users_wifi=mixing_users_wifi+upper_wifi
    
    

    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['user_id', 'mixing_probability'])  # Header row
        writer.writerows(users_mix)


print(f"Saved mixing probabilities to {output_csv}")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

# Read CSV file into DataFrame (replace 'your_file.csv' with your CSV file path)
df = pd.read_csv('/path-leakage/analysis/mix_zone/users_mixing_probabilities.csv')

user_ranges = df.groupby('user_id')['mixing_probability'].agg(['min', 'max'])
user_ranges['range'] = user_ranges['max'] - user_ranges['min']

# Define bins with granularity of 0.01
bins = np.arange(0, user_ranges['range'].max() + 0.01, 0.01)

# Plot histogram of mixing_probability ranges
plt.figure(figsize=(10,6))
plt.hist(user_ranges['range'], bins=bins, color='skyblue', edgecolor='black', alpha=0.7)

# Customize plot
plt.title('Histogram of Mixing Probability Ranges per User')
plt.xlabel('Range of Mixing Probability')
plt.ylabel('Number of Users')
plt.grid(axis='y', alpha=0.75)
plt.xlim(left=0)

# Display the plot
plt.show()
     
print(users_mix)    
print(f"Estimated number of users that mix:{mixing_users}")
print(f"Estimated number of users that will mix in LTE:{mixing_users_lte}")
print(f"Estimated number of users that will mix in BLE:{mixing_users_ble}")
print(f"Estimated number of users that will mix in WiFi:{mixing_users_wifi}")
#print(f"Estimated number of users that does not mix:{mixing_users}")
#print(f"Estimated number of users that does not mix in LTE:{mixing_users_lte}")
#print(f"Estimated number of users that does not mix in BLE:{mixing_users_ble}")
  
    
