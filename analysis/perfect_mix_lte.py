import csv
import pandas as pd
from collections import defaultdict



def upper_bound(lambda_r,lambda_t,T):

    A = lambda_r - lambda_t
    B = lambda_r + lambda_t

    C1 = (1 / B) + (lambda_t / B**2)   

    p_mix=lambda_r*C1
    
    k=2*lambda_r*T
    
    u=(1-p_mix)**k
    
    
    upper_bound=1-u
    
    return upper_bound

neighbor_file1 = "/path-leakage/analysis/neighbor_durations_ble_lte.csv"
neighbor_file2 = "/path-leakage/analysis/neighbor_durations_ble_lte.csv"
scores_file = "/path-leakage/output/data/scenario_exponential_512_sumo_LB/multi_protocol_scenario_exponential_512_sumo_LB.csv"

''' Parameters for BLE'''
lambdar_r_ble=0.00166666666 #(600 seconds)
lambda_t_ble=0.01666666666 #(1 minute)

''' Parameters for LTE'''
lambdar_r_lte=0.00111111111 #(900 seconds)
lambda_t_lte=0.01666666666 #(1 minute)

df_scores=pd.read_csv(scores_file)
df = pd.read_csv(neighbor_file1)

df_lte=pd.read_csv(neighbor_file2)

unique_users_array = df_scores['user_id'].unique()

# List of unique users
unique_user_list = unique_users_array.tolist()

mixing_users=0

for user in unique_user_list:
    user_rows = df[df['user_id'] == user]
    
    user_rows_lte=df_lte[df_lte['user_id']==user]
    # if no mixing happened for an user in BLE
    if user_rows.empty:
        T=0   
    else:
       durations = user_rows['duration_seconds'].tolist()
        # Calculate the total mixing time in BLE for the user
       T=sum(durations)
    # if no mixing happened for an user in BLE    
    if user_rows_lte.empty:
        T_lte=0
    else:
        durations = user_rows_lte['duration_seconds'].tolist()
        # Calculate the total mixing time in LTE for the user
        T_lte=sum(durations)
    
    
        
    # probability of mixing atleast once during the mix-zone duration T
    upper_ble=upper_bound(lambdar_r_ble,lambda_t_ble,T)
    upper_lte=upper_bound(lambdar_r_lte,lambda_t_lte,T_lte)
    #print(upper_lte)
    upper=upper_ble*upper_lte
    mixing_users=mixing_users+upper_lte
    
print(f"Estimated number of users that mixed atleast once:{mixing_users}")
#print("Estimated number of users that mixed atleast once:{mixing_users}")
   
   
    
