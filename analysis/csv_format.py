import csv

# File paths (adjust these paths as needed)
neighbor_file = "/home/aneet_wisec/usenix_2025/path-leakage/analysis/mix_zone/neighbor_durations_ble_sumo_512.csv"
scores_file = "/home/aneet_wisec/usenix_2025/path-leakage/output/data/scenario_exponential_512_sumo_LB/multi_protocol_scenario_exponential_512_sumo_LB.csv"
output_file = "mixedzone_duration_lte.csv"

# Step 1: Read scores_file into a dictionary keyed by user_id
scores_dict = {}
with open(scores_file, mode='r', newline='', encoding='utf-8') as f_scores:
    reader = csv.DictReader(f_scores)
    for row in reader:
        # Assuming user_id is unique in scores file
        user_id = row["user_id"]
        scores_dict[user_id] = {
            "ideal_duration": row["ideal_duration"],
            "privacy_score": row["privacy_score"]
        }

# Step 2: Read neighbor_file, match user_id and append new columns
with open(neighbor_file, mode='r', newline='', encoding='utf-8') as f_neighbor, \
     open(output_file, mode='w', newline='', encoding='utf-8') as f_out:

    reader = csv.DictReader(f_neighbor)
    # Extend fieldnames for new columns
    fieldnames = reader.fieldnames + ["ideal_duration", "privacy_score"]
    writer = csv.DictWriter(f_out, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        user_id = row["user_id"]
        # Look up scores for this user_id if available
        if user_id in scores_dict:
            row["ideal_duration"] = scores_dict[user_id]["ideal_duration"]
            row["privacy_score"] = scores_dict[user_id]["privacy_score"]
        else:
            # Handle missing scores if necessary
            row["ideal_duration"] = ""
            row["privacy_score"] = ""
        writer.writerow(row)

print(f"Updated neighbor data saved to {output_file}")

