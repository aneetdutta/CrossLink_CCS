import os, sys
sys.path.append(os.getcwd())

import json, csv

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
TOTAL_NUMBER_OF_USERS = int(os.getenv("TOTAL_NUMBER_OF_USERS"))
DATA_SOURCE = os.getenv("DATA_SOURCE")
with open(f"data/graph_user_positions_{SCENARIO_NAME}_{TOTAL_NUMBER_OF_USERS}.json", "r") as f:
    pedestrian_data = json.load(f)

rows = []
for user_id, locations in pedestrian_data.items():
    for timestep, (loc_x, loc_y) in enumerate(locations):
        rows.append({
            "timestep": timestep+1,
            "user_id": user_id,
            "loc_x": loc_x,
            "loc_y": loc_y
        })

# Sort rows by timestep
rows = sorted(rows, key=lambda x: x["timestep"])

# Write to CSV
with open(f"data/raw_user_data_{SCENARIO_NAME}_{TOTAL_NUMBER_OF_USERS}.csv", "w", newline="") as csvfile:
    fieldnames = ["timestep", "user_id", "loc_x", "loc_y"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    writer.writeheader()
    writer.writerows(rows)
    
