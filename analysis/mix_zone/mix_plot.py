import csv
import pandas as pd
from collections import defaultdict
import numpy as np



neighbor_file1 = ""
scores_file = ""
output_csv = ""


df_scores=pd.read_csv(scores_file)
df = pd.read_csv(neighbor_file1)



unique_users_array = df_scores['user_id'].unique()

# List of unique users
unique_user_list = unique_users_array.tolist()

user_T_pair=[]

for user in unique_user_list:
    user_rows = df[df['user_id'] == user]
    
    #print(user_rows)
    # if no mixing happened for an user in BLE
    if user_rows.empty:
        T=0   
    else:
        durations = user_rows['duration_seconds'].tolist()
        T=sum(durations)
    user_T_pair.append((user,T))
    
    
    
with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    writer.writerow(["user_id", "mix_duration"])
    
    for user,T in user_T_pair:
   
        writer.writerow([user,T])
     
    

#print(f"Estimated number of users that does not mix:{mixing_users}")
#print(f"Estimated number of users that does not mix in LTE:{mixing_users_lte}")
#print(f"Estimated number of users that does not mix in BLE:{mixing_users_ble}")
  
    
