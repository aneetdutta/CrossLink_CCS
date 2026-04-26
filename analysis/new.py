import csv
import math
import numpy as np
from collections import defaultdict
import csv
output_csv = ""

def calculate_with_generic_dynamic_threshold(csv_filename, base_threshold, Vmax):
    data_by_timestep = defaultdict(list)
    user_timesteps = defaultdict(set)

    with open(csv_filename, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = row['user_id']
            x = float(row['loc_x'])
            y = float(row['loc_y'])
            t = int(float(row['timestep']))
            data_by_timestep[t].append((user_id, x, y))
            user_timesteps[user_id].add(t)

    together_periods = defaultdict(lambda: defaultdict(list))
    current_session = defaultdict(lambda: defaultdict(lambda: {
        "ongoing": False,
        "start_time": None,
        "accumulated_duration": 0
    }))

    for t in sorted(data_by_timestep.keys()):
        users_at_t = data_by_timestep[t]
        n = len(users_at_t)

        for i in range(n):
            u1, x1, y1 = users_at_t[i]
            for j in range(i+1,n):
                u2, x2, y2 = users_at_t[j]
                if u1==u2:
                    continue
                distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
                
                effective_threshold = base_threshold + 1 * Vmax

                session = current_session[u1][u2]

                if distance <= effective_threshold:
                    if not session["ongoing"]:
                        session["ongoing"] = True
                        session["start_time"] = t
                        
                        session["accumulated_duration"] = 0
                    session["accumulated_duration"] += 1
                else:
                    if session["ongoing"]:
                        period_info = {
                            "start_time": session["start_time"],
                            "end_time": t - 1,
                            "duration": session["accumulated_duration"]
                        }
                        together_periods[u1][u2].append(period_info)
                        together_periods[u2][u1].append(period_info)
                        session["ongoing"] = False
                        session["start_time"] = None
                        session["accumulated_duration"] = 0

    for u1, neighbors in current_session.items():
        for u2, session in neighbors.items():
            if session["ongoing"]:
                last_timestep = max(user_timesteps[u1].union(user_timesteps[u2]))
                period_info = {
                    "start_time": session["start_time"],
                    "end_time": last_timestep,
                    "duration": session["accumulated_duration"]
                }
                together_periods[u1][u2].append(period_info)
                together_periods[u2][u1].append(period_info)
                session["ongoing"] = False

    result = {}
    for user_id in user_timesteps:
        total_ts = len(user_timesteps[user_id])
        neighbors_data = {}
        for neighbor_id, periods in together_periods[user_id].items():
            if periods:
                neighbors_data[neighbor_id] = periods
        result[user_id] = {
            "neighbors": neighbors_data,
            "total_timesteps": total_ts
        }
    print(result)
    return result, user_timesteps  # Also return user_timesteps for later use

def interpolate_and_check(stats, user_timesteps, user_data, base_threshold):
    
    interpolation_granularity = 0.1 
  
    neighbor_duration = defaultdict(float)


    for user_id, info in stats.items():
        #print(user_id)
        #print(info)
        neighbors = info.get("neighbors", {})
        for neighbor_id, periods in neighbors.items():
           
            for period in periods:
                start_time = period["start_time"]
                end_time = period["end_time"]

              
                for t in range(start_time, end_time):
                  
                    key_u_t = (user_id, t)
                    key_u_t1 = (user_id, t+1)
                    key_n_t = (neighbor_id, t)
                    key_n_t1 = (neighbor_id, t+1)

                   
                    if key_u_t in user_data and key_u_t1 in user_data and \
                       key_n_t in user_data and key_n_t1 in user_data:

                       
                        x1_u, y1_u = float(user_data[key_u_t]['loc_x']), float(user_data[key_u_t]['loc_y'])
                        x2_u, y2_u = float(user_data[key_u_t1]['loc_x']), float(user_data[key_u_t1]['loc_y'])
                        x1_n, y1_n = float(user_data[key_n_t]['loc_x']), float(user_data[key_n_t]['loc_y'])
                        x2_n, y2_n = float(user_data[key_n_t1]['loc_x']), float(user_data[key_n_t1]['loc_y'])

                   
                        num_steps = int(1 / interpolation_granularity)
                        for step in range(num_steps):
                            fraction = step * interpolation_granularity
                            # Interpolated time between t and t+1
                            interp_time = t + fraction

                            # Linear interpolation for user's position
                            interp_x_u = x1_u + fraction * (x2_u - x1_u)
                            interp_y_u = y1_u + fraction * (y2_u - y1_u)

                            # Linear interpolation for neighbor's position
                            interp_x_n = x1_n + fraction * (x2_n - x1_n)
                            interp_y_n = y1_n + fraction * (y2_n - y1_n)

                            # Compute distance at interpolated time
                            dist = math.sqrt((interp_x_n - interp_x_u)**2 + (interp_y_n - interp_y_u)**2)

                            # Check if distance is within base_threshold
                            if dist <= base_threshold:
                                neighbor_duration[(user_id, neighbor_id)] += interpolation_granularity

    return neighbor_duration

# Main execution
if __name__ == "__main__":
    csv_file = "/home/aneet_wisec/usenix_2025/path-leakage/data/scenario_result_512_sumo_all/user_data_scenario_result_512_sumo_all.csv"
    base_threshold = 20
    Vmax = 3

    
    stats, user_timesteps = calculate_with_generic_dynamic_threshold(csv_file, base_threshold, Vmax)
    # Load user.csv data again into a lookup for positions for interpolation
    user_data = {}
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['timestep'] = int(float(row['timestep']))
            key = (row['user_id'], row['timestep'])
            user_data[key] = row
 
    neighbor_duration = interpolate_and_check(stats, user_timesteps, user_data, base_threshold)

    # Print results
    for (user, neighbor), duration in neighbor_duration.items():
        print(f"Neighbor pair ({user}, {neighbor}) matched condition for {duration:.2f} seconds.")
        
        
   



    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
     #Write headers
        writer.writerow(["user_id", "neighbor_id", "duration_seconds"])
    
    # Write rows for each neighbor pair
        for (user_id, neighbor_id), duration in neighbor_duration.items():
            writer.writerow([user_id, neighbor_id, duration])
     
    

        
    
        
print(f"Data saved to {output_csv}")


