import os, sys
sys.path.append(os.getcwd())
import os
import polars as pl
from collections import defaultdict
from modules.general import str_to_bool, calculate_distance_l, extend_paths
from collections import deque

from modules.logger import MyLogger
# remove_subsets_from_dict

# pl.Config.set_tbl_rows(2000)


SCENARIO_NAME = os.getenv("SCENARIO_NAME")
MAX_MOBILITY_FACTOR = float(os.getenv('MAX_MOBILITY_FACTOR'))
TOTAL_NUMBER_OF_USERS = int(os.getenv("TOTAL_NUMBER_OF_USERS", 0))
MAX_RANDOMIZATION_INTERVAL = 1800
MAX_TIMESTEP = 25200

ml = MyLogger(f"filter_users_RI_count_{SCENARIO_NAME}")
# Path to the input CSV file
input_csv_path = f"data/raw_user_data_filter_polygon_{SCENARIO_NAME}.csv"
# output_csv_path = f"data/raw_user_data_filtered_{SCENARIO_NAME}.csv"

df = pl.read_csv(input_csv_path)

ml.logger.info("loaded df")

unique_user_ids = df.select("user_id").unique()

# ml.logger.info the total number of unique user_ids
ml.logger.info(f"Total unique user_ids before mobility filter: {unique_user_ids.height}")

df = df.sort(["user_id", "timestep"])

###################
# Mobility Filter #
###################
def calculate_mobility(group: pl.DataFrame) -> pl.DataFrame:
    # Calculate differences in loc_x, loc_y, and timestep for each row in the group
    group = group.with_columns(
        (group["loc_x"] - group["loc_x"].shift(fill_value=None)).alias("delta_x"),
        (group["loc_y"] - group["loc_y"].shift(fill_value=None)).alias("delta_y"),
        (group["timestep"] - group["timestep"].shift(fill_value=None)).alias("delta_time")
    )
    
    # Calculate mobility as sqrt(delta_x^2 + delta_y^2) / delta_time
    group = group.with_columns(
        ((group["delta_x"]**2 + group["delta_y"]**2).sqrt() / group["delta_time"]).alias("mobility")
    )
    
    # Filter out rows where delta_time is null (first row of each group)
    group = group.filter(~group["delta_time"].is_null())
    
    # Filter based on mobility and delta_time
    group = group.filter(
        (group["delta_time"] > 1) | (group["mobility"] > MAX_MOBILITY_FACTOR)
    )
    
    return group

# Apply the function to each user_id group
df_with_mobility = df.group_by("user_id", maintain_order=True).map_groups(calculate_mobility)

# ml.logger.info(unique_user_ids.height)
unique_user_ids = df_with_mobility.select("user_id").unique().to_series()

# 2. Filter the original df by excluding these unique user_ids
df = df.filter(~pl.col("user_id").is_in(unique_user_ids))
unique_user_id = df.select("user_id").unique()
# df = df.sort("timestep")
ml.logger.info(f"Total unique user_ids after mobility filter, but before extending them and RI filter: {unique_user_id.height}")

unique_users_at_25200 = df.filter(pl.col("timestep") == 25200).select("user_id").unique()

ml.logger.info(f"{unique_users_at_25200.height} Users at timestep == 25200 after mobility and before extension" )

# ml.logger.info(df)

###############################
# Extend User Timesteps 25200 #
###############################

df = extend_paths(df, MAX_TIMESTEP)

# #################################
# # Checking again
# #################################

unique_user_ids = df.select("user_id").unique()
ml.logger.info(f"Total unique user_ids before mobility filter: {unique_user_ids.height}")

df = df.sort(["user_id", "timestep"])

# Apply the function to each user_id group
df_with_mobility = df.group_by("user_id", maintain_order=True).map_groups(calculate_mobility)

unique_user_ids = df_with_mobility.select("user_id").unique().to_series()
# 2. Filter the original df by excluding these unique user_ids
df = df.filter(~pl.col("user_id").is_in(unique_user_ids))
unique_user_id = df.select("user_id").unique()
# df = df.sort("timestep")
ml.logger.info(f"Checking again: Total unique user_ids after mobility filter, but after extending them and before RI filter: {unique_user_id.height}")


unique_users_at_25200 = df.filter(pl.col("timestep") == 25200).select("user_id").unique()

ml.logger.info(f"{unique_users_at_25200.height} Users at timestep == 25200 after mobility and extension" )

# ml.logger.info(df)

# ###########################
# # Filter by Max Timesteps #
# ###########################

timesteps_per_user = (
    df.group_by("user_id")  # Group by user_id
    .agg(pl.col("timestep").count().alias("total_timesteps"))  # Count timesteps per user
    .sort("total_timesteps", descending=True)  # Sort by total_timesteps in descending order
)

output_file_path = f"data/raw_user_data_timesteps_per_user_{SCENARIO_NAME}.csv"
timesteps_per_user.write_csv(output_file_path)

ml.logger.info(f"Timesteps per user written to: {output_file_path}")

filtered_timesteps_per_user = timesteps_per_user.filter(pl.col("total_timesteps") <= MAX_RANDOMIZATION_INTERVAL)

user_ids_to_filter = filtered_timesteps_per_user.select("user_id").to_series()

# Filter the original dataframe to exclude these user_ids
df = df.filter(~pl.col("user_id").is_in(user_ids_to_filter))

unique_user_id = df.select("user_id").unique()
ml.logger.info(f"Total unique user_ids after mobility filter and RI filter and extension: {unique_user_id.height}")

if not TOTAL_NUMBER_OF_USERS:
    user_limits = [32, 128, 256, 512, 1024, 1536, 2048]
else:
    user_limits = [TOTAL_NUMBER_OF_USERS]

# Get the height of unique_user_id (total unique users)
num_unique_users = unique_user_id.height

# Create the NUM_OF_USERS list based on the condition
NUM_OF_USERS = [num for num in user_limits if num <= num_unique_users] + [num_unique_users]

for num_users in NUM_OF_USERS:
    top_users = timesteps_per_user.head(num_users)
    top_users = top_users.select("user_id").to_series()
    df_filtered = df.filter(pl.col("user_id").is_in(top_users))
    output_file_path_selected_users = f"data/raw_user_data_{SCENARIO_NAME}_{num_users}.csv"
    df_filtered = df_filtered.sort(["timestep"])
    df_filtered.write_csv(output_file_path_selected_users)
    ml.logger.info(f"Selected users written to: {output_file_path_selected_users}")
