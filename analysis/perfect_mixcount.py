import csv
import math
import numpy as np
from collections import defaultdict

def time_difference(time1, time2):
    
    return abs(time1 - time2)

def calculate_with_vmax(csv_filename, base_threshold=20, Vmax=3):
    data_by_timestep = defaultdict(list)
    user_timesteps = defaultdict(set)
    
    users = set()
    user_position_time = defaultdict(dict)

    with open(csv_filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = row['user_id']
            x = float(row['loc_x'])
            y = float(row['loc_y'])
            t = int(float(row['timestep']))
            data_by_timestep[t].append((user_id, x, y))
            user_timesteps[user_id].add(t)
            
            users.add(user_id)
            user_position_time[user_id][t] = (x,y)

    together_periods = defaultdict(lambda: defaultdict(list))
    current_session = defaultdict(lambda: defaultdict(lambda: {
        "ongoing": False,
        "start_time": None,
        "end_time":None,
        "accumulated_duration": 0
    }))
    
    for u1 in users:
        print(u1)
        print(u2)
        for u2 in users:
    	
    	    if u1 == u2:
    	        continue
    	    
    	    current_start = None
    	    current_end = None
    	    t_prev = None
    	    
    	    for t in user_timesteps[u1]:
    	    
    	        (x1, y1) = user_position_time[u1][t]
    	        (x2, y2) = user_position_time[u2][t]
    	    	
    	        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                effective_threshold=base_threshol+(1*Vmax)
                #effective_threshold = base_threshold+Vmax
               
                
                if t - 1 != t_prev:
                    # We had a gap (or just started)
                    if current_start:
                        # store (current_start, t_prev)
                        current_start = None
                
                if distance <= effective_threshold:
                    if not current_start:
                        current_start = t
                else:
                    if current_start:
                        # store this thin (current_start, t)
                        current_start = None
    	    	
    	    	t_prev = t
    	    	
    
    
   
    return result, user_timesteps

   

   

def interpolate_and_check(stats, user_data, base_threshold):
    interpolation_granularity = 0.1  # 1/10th of a second
    neighbor_duration = defaultdict(float)

    # For each user in stats
    for user_id, info in stats.items():
        neighbors = info.get("neighbors", {})
        for neighbor_id, periods in neighbors.items():
            
            for period in periods:
                start_time = period["start_time"]
                end_time = period["end_time"]

                
                for t in range(start_time, end_time):
                    key_u_t  = (user_id, t)
                    key_u_t1 = (user_id, t+1)
                    key_n_t  = (neighbor_id, t)
                    key_n_t1 = (neighbor_id, t+1)

                   
                    if key_u_t in user_data and key_u_t1 in user_data and \
                       key_n_t in user_data and key_n_t1 in user_data:

                        x1_u = float(user_data[key_u_t]['loc_x'])
                        y1_u = float(user_data[key_u_t]['loc_y'])
                        x2_u = float(user_data[key_u_t1]['loc_x'])
                        y2_u = float(user_data[key_u_t1]['loc_y'])

                        x1_n = float(user_data[key_n_t]['loc_x'])
                        y1_n = float(user_data[key_n_t]['loc_y'])
                        x2_n = float(user_data[key_n_t1]['loc_x'])
                        y2_n = float(user_data[key_n_t1]['loc_y'])

                        num_steps = int(1 / interpolation_granularity)
                        for step in range(num_steps):
                            fraction = step * interpolation_granularity

                            interp_x_u = x1_u + fraction * (x2_u - x1_u)
                            interp_y_u = y1_u + fraction * (y2_u - y1_u)
                            interp_x_n = x1_n + fraction * (x2_n - x1_n)
                            interp_y_n = y1_n + fraction * (y2_n - y1_n)

                            dist = math.sqrt((interp_x_n - interp_x_u)**2 + (interp_y_n - interp_y_u)**2)

                            if dist <= base_threshold:
                                neighbor_duration[(user_id, neighbor_id)] += interpolation_granularity

    return neighbor_duration

# Main execution
if __name__ == "__main__":
    csv_file = "/home/aneet_wisec/usenix_2025/path-leakage/data/scenario_exponential_512_sumo_all/user_data_scenario_exponential_512_sumo_all.csv"
    base_threshold = 3
    Vmax = 3

    stats, user_timesteps = calculate_with_vmax(csv_file, base_threshold, Vmax)

    user_data = {}
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['timestep'] = int(float(row['timestep']))
            key = (row['user_id'], row['timestep'])
            user_data[key] = row

    neighbor_duration = interpolate_and_check(stats, user_data, base_threshold)

    for (user, neighbor), duration in neighbor_duration.items():
        print(f"Neighbor pair ({user}, {neighbor}) condition holds for {duration:.2f} seconds.")

