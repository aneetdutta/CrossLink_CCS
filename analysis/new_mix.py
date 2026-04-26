import csv, math
from collections import defaultdict
from itertools import combinations
import numpy as np
from sklearn.neighbors import BallTree

# Constants
distance_error = 3.0   # in meters
velocity_max = 3.0     # in meters/second



# Step 1: Read CSV and collect all records
all_records = defaultdict(list)  # List of tuples: (timestamp, user_id, lat, lon)
with open('', mode='r') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        timestamp = float(row['timestep'])  # assuming timestamp is convertible to float
        user_id = row['user_id']

        x = float(row['loc_x'])
        y = float(row['loc_y'])
        all_records[timestamp].append((timestamp, user_id,x,y))


        
        
neighbors_by_time = defaultdict(lambda: defaultdict(set))

for timestamp, records in all_records.items():
    if len(records) < 2:
        continue
    
    # Prepare data for BallTree: array of [x, y] coordinates
    user_ids = [rec[1] for rec in records]
    coordinates = np.array([[rec[2], rec[3]] for rec in records])
    
    # Build BallTree using Euclidean metric
    tree = BallTree(coordinates, metric='euclidean')
    
    # Radius for neighbor search is simply the distance_error
    radius = distance_error+velocity_max
    
    # Query neighbors within radius for each point
    indices = tree.query_radius(coordinates, r=radius)
    
    # Populate neighbors_by_time for this timestamp
    for i, neighbors in enumerate(indices):
        user_id = user_ids[i]
        for j in neighbors:
            # Avoid self-comparison
            if i == j:
                continue
            neighbor_id = user_ids[j]
            neighbors_by_time[timestamp][user_id].add(neighbor_id)
            neighbors_by_time[timestamp][neighbor_id].add(user_id)


from collections import defaultdict

# Suppose neighbors_by_time structure:
# neighbors_by_time = {
#     timestamp1: { user_id1: {neighbor_id1, neighbor_id2, ...}, ... },
#     timestamp2: { user_id1: {neighbor_id3, ...}, ... },
#     ...
# }

# Step 1: Collect all timestamps when each user pair are neighbors
pair_timestamps = defaultdict(list)

for timestamp, neighbors_at_time in neighbors_by_time.items():
    for user, neighbor_set in neighbors_at_time.items():
        for neighbor in neighbor_set:
            # Sort the pair to avoid duplicate entries (A,B and B,A)
            pair = tuple(sorted((user, neighbor)))
            pair_timestamps[pair].append(timestamp)

# Step 2: For each pair, sort timestamps and merge consecutive ones into intervals
pair_intervals = {}

for pair, times in pair_timestamps.items():
    # Sort timestamps for each pair
    sorted_times = sorted(times)
    intervals = []
    
    # Initialize first interval with the first timestamp
    start_time = sorted_times[0]
    end_time = sorted_times[0]
    
    for t in sorted_times[1:]:
        # If current timestamp is consecutive or close enough to previous one,
        # extend the current interval. Adjust threshold if needed.
        # Here we assume timestamps are close enough if they differ by a constant Δ.
        # You can refine this condition based on your data's sampling rate.
        if t - end_time <= 1:  # assuming a gap of 1 unit implies continuity
            end_time = t
        else:
            # No longer consecutive, close previous interval and start new one
            intervals.append((start_time, end_time))
            start_time = t
            end_time = t
            
    # Append the last interval
    intervals.append((start_time, end_time))
    pair_intervals[pair] = intervals

# pair_intervals now holds continuous intervals for each user pair
for pair, intervals in pair_intervals.items():
    print(f"Users {pair} were together during intervals: {intervals}")
    
    
from collections import defaultdict

# Step 1: Calculate total time for each user pair based on intervals
pair_total_time = {}
for pair, intervals in pair_intervals.items():
    total_time = sum(end - start for start, end in intervals)
    pair_total_time[pair] = total_time

# Step 2: Aggregate information for each user
user_neighbor_time = defaultdict(list)
# Structure: { user_id: [(neighbor_id, total_time), ...], ... }

for (user1, user2), total_time in pair_total_time.items():
    user_neighbor_time[user1].append((user2, total_time))
    user_neighbor_time[user2].append((user1, total_time))

# Step 3: Display results for each user
for user, neighbor_times in user_neighbor_time.items():
    print(f"User {user}:")
    for neighbor, total_time in neighbor_times:
        print(f"  - Neighbor {neighbor}: Total time together = {total_time}")

with open('user_neighbor_durations.csv', mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    # Write header
    writer.writerow(['user_id', 'neighbor', 'duration'])
    
    # Write rows for each user and their neighbors
    for user, neighbor_times in user_neighbor_time.items():
        for neighbor, total_time in neighbor_times:
            writer.writerow([user, neighbor, total_time])


