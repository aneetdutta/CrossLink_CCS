import csv
import pandas as pd
from collections import defaultdict
import numpy as np
import math

def per_event_upper_bound(lambda_r: float, lambda_t: float, T: float) -> float:
    """
    Time–dependent per‑event upper bound (formula 5a in the derivation).

    Parameters
    ----------
    lambda_r : float
        Randomisation rate of each device (must be >0 and <1 for the modelling assumptions).
    lambda_t : float
        Transmission / contact rate (>0 and typically > lambda_r).
    T : float
        Observation window length (seconds, minutes … whatever time unit the rates use).

    Returns
    -------
    float
        Upper bound on the probability that **one** randomisation opportunity within the
        window mixes the two devices.
    """
    if lambda_r <= 0 or lambda_t <= 0:
        raise ValueError("λ_r and λ_t must be positive.")
    if T < 0:
        raise ValueError("T must be non‑negative.")

    B = lambda_r + lambda_t
    A = lambda_r - lambda_t          # will be negative
    absA = abs(A)
    C = 1.0 / B + lambda_t / B**2

    # Term f2(T)
    f2 = (
        2.0
        * lambda_r**2
        * math.exp(-B * T)
        * C
        * (math.exp(absA * T) - 1.0)
        / absA
    )

    # Supremum of f3(T)
    f3_sup = (2.0 * lambda_r**2 * lambda_t) / (math.e * B**2 * absA)

    # Supremum of f4(T)
    gamma = absA / B  # in (0,1) if λ_t > λ_r
    term1 = (1.0 - gamma) ** ((1.0 - gamma) / gamma)
    term2 = (1.0 - gamma) ** (1.0 / gamma)
    f4_sup = 2.0 * lambda_r**2 / absA**2 * (term1 - term2)

    # Constant λ_r C from f1(T) ≤ λ_r C
    f1_const = lambda_r * C

    p_event = f1_const + f2 + f3_sup + f4_sup
    p=min(max(p_event, 0.0), 1.0)  # Clamp into [0,1]
    u=p**(2*lambda_r*T)
    return 1-u

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

neighbor_file1 = "/path-leakage/analysis/mix_zone/neighbor_durations_ble_sumo_512.csv"
neighbor_file2 = "/path-leakage/analysis/mix_zone/neighbor_durations_lte_sumo_512.csv"
neighbor_file3 = "/path-leakage/analysis/mix_zone/neighbor_durations_WiFi_sumo_512.csv"

scores_file = "/path-leakage/output/data/scenario_result_512_sumo_all5/multi_protocol_scenario_result_512_sumo_all5.csv"

''' Parameters for BLE'''
lambdar_r_ble=0.00476190476 #(600 seconds)
lambda_t_ble=0.2 #(1 minute)

''' Parameters for LTE'''
lambdar_r_lte=0.00476190476 #(900 seconds)
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
    
    mixing_users=mixing_users+upper
    mixing_users_lte=mixing_users_lte+upper_lte
    mixing_users_ble=mixing_users_ble+upper_ble#_no_mix
    mixing_users_wifi=mixing_users_wifi+upper_wifi
    
print(f"Estimated number of users that mix:{mixing_users}")
print(f"Estimated number of users that will mix in LTE:{mixing_users_lte}")
print(f"Estimated number of users that will mix in BLE:{mixing_users_ble}")
print(f"Estimated number of users that will mix in WiFi:{mixing_users_wifi}")
#print(f"Estimated number of users that does not mix:{mixing_users}")
#print(f"Estimated number of users that does not mix in LTE:{mixing_users_lte}")
#print(f"Estimated number of users that does not mix in BLE:{mixing_users_ble}")
  
    
