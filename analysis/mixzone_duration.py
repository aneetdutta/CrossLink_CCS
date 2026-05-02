import os
import polars as pl
import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from multiprocessing import Pool, cpu_count

# Function to process a single combination R
def process_combination(R, file_path):
    print(f"Processing for R = {R}")

    # Load the CSV file into a Polars DataFrame
    df = pl.read_csv(file_path)

    # Initialize result dictionary
    result = {}

    # Sort the DataFrame by timestep
    df_sorted = df.sort("timestep")

    # Group by timestep
    for timestep, chunk in df_sorted.groupby("timestep"):
        print(f"{R} combo - Processing timestep : {timestep}")

        # Convert to numpy for fast computation
        users = chunk["user_id"].to_numpy()
        loc_x = chunk["loc_x"].to_numpy()
        loc_y = chunk["loc_y"].to_numpy()

        # Combine x, y coordinates into a 2D array
        coordinates = np.column_stack((loc_x, loc_y))

        # Build a KDTree for efficient neighbor lookup
        tree = KDTree(coordinates)

        # Query pairs within the R-meter range
        pairs = tree.query_pairs(r=R)

        # Process pairs and update results
        for i, j in pairs:
            user_id = users[i]
            other_user_id = users[j]

            # Update results for user_id
            if user_id not in result:
                result[user_id] = {}
            if other_user_id not in result[user_id]:
                result[user_id][other_user_id] = []
            result[user_id][other_user_id].append(timestep)

            # Update results for other_user_id (ensure symmetry)
            if other_user_id not in result:
                result[other_user_id] = {}
            if user_id not in result[other_user_id]:
                result[other_user_id][user_id] = []
            result[other_user_id][user_id].append(timestep)

    # Transform JSON into a DataFrame
    proximity_df = pd.DataFrame.from_dict(result, orient="index")

    # Function to process list of timesteps into durations
    def process_list(values):
        if isinstance(values, list) and values:
            values.sort()
            durations = []
            start = values[0]

            for i in range(1, len(values)):
                if values[i] != values[i - 1] + 1:
                    durations.append(values[i - 1] - start + 1)
                    start = values[i]

            durations.append(values[-1] - start + 1)
            return max(durations) if len(durations) > 1 else durations[0]
        return values

    # Apply post-processing to the DataFrame
    proximity_df = proximity_df.applymap(process_list)

    # Save to CSV
    output_file = f"mixzone_{R}.csv"
    proximity_df.to_csv(output_file, index=True)

    print(f"Saved results for R = {R} to {output_file}")
    return f"R = {R} completed"

# Main function for parallel processing
def main():
    # Input file path
    file_path = "/path-leakage/data/scenario_exponential_512_sumo_all/user_data_scenario_exponential_512_sumo_all.csv"
    print("Loaded DataFrame")

    # Range combinations
    Combinations = [10+10, 1+1, 5+5]
    # Combinations = [5+5, 5+1]

    # Determine number of processes
    num_processes = min(len(Combinations), cpu_count())

    # Use multiprocessing Pool to parallelize over Combinations
    with Pool(processes=num_processes) as pool:
        results = pool.starmap(process_combination, [(R, file_path) for R in Combinations])

    for res in results:
        print(res)

if __name__ == "__main__":
    main()
