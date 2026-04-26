import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import seaborn as sns
from shapely.geometry import Point, Polygon
from matplotlib.patches import Polygon as MplPolygon
from sklearn.cluster import DBSCAN
from shapely.geometry import Polygon
from shapely.ops import unary_union
import os, sys
from scipy.spatial import ConvexHull

def create_polygon_from_cluster(cluster_points):
    if len(cluster_points) >= 3:  # Minimum 3 points for a valid polygon
        try:
            # Apply Convex Hull to get the outer boundary
            hull = ConvexHull(cluster_points)
            convex_hull_points = cluster_points[hull.vertices]
            
            # Create the polygon from the convex hull points
            polygon = Polygon(convex_hull_points)
            
            # Ensure the polygon is valid (it might need to be closed)
            if not polygon.is_valid:
                polygon = polygon.buffer(0)
                
            return polygon
        except Exception as e:
            print(f"Error creating polygon from cluster: {e}")
            return None
    else:
        print(f"Cluster has less than 3 points, cannot create a valid polygon.")
        return None
    
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

df = pd.read_csv("data/raw_user_data_scenario_sumo_512.csv")

df_sorted = df.sort_values(by=["user_id", "timestep"])

# Filter only the start and last timestep for each user
start_end_df = (
    df_sorted.groupby("user_id")
    .agg(
        start_timestep=("timestep", "first"),
        last_timestep=("timestep", "last"),
    )
    .reset_index()
)

filtered_df = df_sorted.merge(start_end_df, on="user_id")
# Keep only rows where timestep equals start_timestep or last_timestep
start_df = filtered_df[(filtered_df["timestep"] == filtered_df["start_timestep"])]
end_df = filtered_df[(filtered_df["timestep"] == filtered_df["last_timestep"])]

total_df = filtered_df[(filtered_df["timestep"] == filtered_df["start_timestep"]) | (filtered_df["timestep"] == filtered_df["last_timestep"])]

start_df = (
    start_df.drop(columns=["start_timestep", "last_timestep"])
    .sort_values("timestep")
    .reset_index()
)

end_df = (
    end_df.drop(columns=["start_timestep", "last_timestep"])
    .sort_values("timestep")
    .reset_index()
)

total_df = (
    total_df.drop(columns=["start_timestep", "last_timestep"])
    .sort_values("timestep")
    .reset_index()
)

x_range = df["loc_x"].max() - df["loc_x"].min()
y_range = df["loc_y"].max() - df["loc_y"].min()


n_bins_x = int(np.ceil(x_range / 20))  # Number of bins for x-axis
n_bins_y = int(np.ceil(y_range / 20))  # Number of bins for y-axis


# Define polygon coordinates
polygon_coords = [
    (3499.77, 1500.07),
    (5798.43, 3799.93),
    (6452.11, 3150.56),
    (5401.44, 2099.71),
    (5751.91, 1749.63),
    (4500.10, 498.92),
]
polygon = Polygon(polygon_coords)

# -----------------------------------------------------------
# Define the bin edges
xedges = np.linspace(df["loc_x"].min(), df["loc_x"].max(), n_bins_x + 1)
yedges = np.linspace(df["loc_y"].min(), df["loc_y"].max(), n_bins_y + 1)

bin_x = np.digitize(df["loc_x"].values, xedges) - 1  # Get bin indices for x
bin_y = np.digitize(df["loc_y"].values, yedges) - 1  # Get bin indices for y
# Ensure that bin_x and bin_y are within the correct range
bin_x = np.clip(bin_x, 0, n_bins_x - 1)  # Clamp the values between 0 and n_bins_x - 1
bin_y = np.clip(bin_y, 0, n_bins_y - 1)  # Clamp the values between 0 and n_bins_y - 1

user_bins = {}

# Track unique users in bins using a set
for i, user_id in enumerate(df["user_id"]):
    bin_key = (bin_x[i], bin_y[i])
    if bin_key not in user_bins:
        user_bins[bin_key] = set()
    user_bins[bin_key].add(user_id)

# Convert user_bins to a 2D array of user counts
user_count_matrix = np.zeros((n_bins_x, n_bins_y), dtype=int)
for bin_key, users in user_bins.items():
    user_count_matrix[bin_key[0], bin_key[1]] = len(users)

max_user_count = max(len(users) for users in user_bins.values())

# Identify all bins with the highest user count
max_bins = [bin_key for bin_key, users in user_bins.items() if len(users) >= max_user_count]

highlight_matrix = np.zeros_like(user_count_matrix)

# Set all bins with the highest user count in the highlight matrix
for bin_key in max_bins:
    highlight_matrix[bin_key[0], bin_key[1]] = max_user_count

plt.figure(figsize=(10, 8))
# # Layer 1: Highlight all bins with the highest user count
# plt.imshow(
#     highlight_matrix.T,
#     cmap="Reds",
#     origin="lower",
#     extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
#     alpha=0.7,  # Slight transparency for the first layer
#     label="High-Density Bins",
# )


# Print the result
print(f"Maximum User Count: {max_user_count}")
print(f"Bins with the highest user count: {max_bins}")
# Plot the heatmap of user counts in bins

plt.imshow(
    user_count_matrix.T,
    cmap="Blues",
    origin="lower",
    extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
)

plt.colorbar(label="User Count")
plt.title("User Density Heatmap (Distinct Users in Each Bin)")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")

plt.savefig("analysis/heatmap_new.pdf", dpi=600)








#-------------------------------------------------------


# print(n_bins_x, n_bins_y)
# # Define the bin edges
# xedges = np.linspace(start_df["loc_x"].min(), start_df["loc_x"].max(), n_bins_x + 1)
# yedges = np.linspace(start_df["loc_y"].min(), start_df["loc_y"].max(), n_bins_y + 1)

# bin_x = np.digitize(start_df["loc_x"].values, xedges) - 1  # Get bin indices for x
# bin_y = np.digitize(start_df["loc_y"].values, yedges) - 1  # Get bin indices for y
# # Ensure that bin_x and bin_y are within the correct range
# bin_x = np.clip(bin_x, 0, n_bins_x - 1)  # Clamp the values between 0 and n_bins_x - 1
# bin_y = np.clip(bin_y, 0, n_bins_y - 1)  # Clamp the values between 0 and n_bins_y - 1

# user_bins = {}

# # Track unique users in bins using a set
# for i, user_id in enumerate(start_df["user_id"]):
#     bin_key = (bin_x[i], bin_y[i])
#     if bin_key not in user_bins:
#         user_bins[bin_key] = set()
#     user_bins[bin_key].add(user_id)

# # Convert user_bins to a 2D array of user counts
# user_count_matrix = np.zeros((n_bins_x, n_bins_y), dtype=int)
# for bin_key, users in user_bins.items():
#     user_count_matrix[bin_key[0], bin_key[1]] = len(users)

# max_user_count = max(len(users) for users in user_bins.values())

# # Identify all bins with the highest user count
# max_bins = [bin_key for bin_key, users in user_bins.items() if len(users) >= max_user_count]

# highlight_matrix = np.zeros_like(user_count_matrix)

# # Set all bins with the highest user count in the highlight matrix
# for bin_key in max_bins:
#     highlight_matrix[bin_key[0], bin_key[1]] = max_user_count

# plt.figure(figsize=(10, 8))
# # Layer 1: Highlight all bins with the highest user count
# plt.imshow(
#     highlight_matrix.T,
#     cmap="Reds",
#     origin="lower",
#     extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
#     alpha=0.7,  # Slight transparency for the first layer
#     label="High-Density Bins",
# )


# # Print the result
# print(f"Maximum User Count: {max_user_count}")
# print(f"Bins with the highest user count: {max_bins}")
# # Plot the heatmap of user counts in bins

# # plt.imshow(
# #     user_count_matrix.T,
# #     cmap="Blues",
# #     origin="lower",
# #     extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
# # )
# plt.colorbar(label="User Count")
# plt.title("User Density Heatmap (Distinct Users in Each Bin)")
# plt.xlabel("X Coordinate")
# plt.ylabel("Y Coordinate")

# plt.savefig("analysis/heatmap_start.pdf", dpi=600)



# ----------------------------------

# Define the bin edges
xedges = np.linspace(end_df["loc_x"].min(), end_df["loc_x"].max(), n_bins_x + 1)
yedges = np.linspace(end_df["loc_y"].min(), end_df["loc_y"].max(), n_bins_y + 1)

bin_x = np.digitize(end_df["loc_x"].values, xedges) - 1  # Get bin indices for x
bin_y = np.digitize(end_df["loc_y"].values, yedges) - 1  # Get bin indices for y
# Ensure that bin_x and bin_y are within the correct range
bin_x = np.clip(bin_x, 0, n_bins_x - 1)  # Clamp the values between 0 and n_bins_x - 1
bin_y = np.clip(bin_y, 0, n_bins_y - 1)  # Clamp the values between 0 and n_bins_y - 1


user_bins = {}

# Track unique users in bins using a set
for i, user_id in enumerate(end_df["user_id"]):
    bin_key = (bin_x[i], bin_y[i])
    if bin_key not in user_bins:
        user_bins[bin_key] = set()
    user_bins[bin_key].add(user_id)

# Convert user_bins to a 2D array of user counts
user_count_matrix = np.zeros((n_bins_x, n_bins_y), dtype=int)
for bin_key, users in user_bins.items():
    user_count_matrix[bin_key[0], bin_key[1]] = len(users)

max_user_count = max(len(users) for users in user_bins.values())

# Identify all bins with the highest user count
max_bins = [bin_key for bin_key, users in user_bins.items() if len(users) >= max_user_count-2]

# Print the result
print(f"Maximum User Count: {max_user_count}")
print(f"Bins with the highest user count: {max_bins}")

highlight_matrix = np.zeros_like(user_count_matrix)

# Set all bins with the highest user count in the highlight matrix
for bin_key in max_bins:
    highlight_matrix[bin_key[0], bin_key[1]] = max_user_count

fig, ax = plt.subplots(figsize=(10, 8))
# Layer 1: Highlight all bins with the highest user count
img1 = plt.imshow(
    highlight_matrix.T,
    cmap="Reds",
    origin="lower",
    extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
    alpha=0.7,  # Slight transparency for the first layer
    label="High-Density Bins",
)

# Plot the heatmap of user counts in bins
# plt.figure(figsize=(10, 8))
# img2 = plt.imshow(
#     user_count_matrix.T,
#     cmap="Blues",
#     origin="lower",
#     extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
# )


plt.colorbar(label="User Count")
plt.title("User Density Heatmap (Distinct Users in Each Bin)")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")

plt.savefig("analysis/heatmap_last.pdf", dpi=600)


# ------------------------------------------------------


xedges = np.linspace(total_df["loc_x"].min(), total_df["loc_x"].max(), n_bins_x + 1)
yedges = np.linspace(total_df["loc_y"].min(), total_df["loc_y"].max(), n_bins_y + 1)

bin_x = np.digitize(total_df["loc_x"].values, xedges) - 1  # Get bin indices for x
bin_y = np.digitize(total_df["loc_y"].values, yedges) - 1  # Get bin indices for y
bin_x = np.clip(bin_x, 0, n_bins_x - 1)  # Clamp the values between 0 and n_bins_x - 1
bin_y = np.clip(bin_y, 0, n_bins_y - 1)  # Clamp the values between 0 and n_bins_y - 1

user_bins = {}

# Track unique users in bins using a set
for i, user_id in enumerate(total_df["user_id"]):
    bin_key = (bin_x[i], bin_y[i])
    if bin_key not in user_bins:
        user_bins[bin_key] = set()
    user_bins[bin_key].add(user_id)

# Convert user_bins to a 2D array of user counts
user_count_matrix = np.zeros((n_bins_x, n_bins_y), dtype=int)
for bin_key, users in user_bins.items():
    user_count_matrix[bin_key[0], bin_key[1]] = len(users)

max_user_count = max(len(users) for users in user_bins.values())

# Identify all bins with the highest user count
max_bins = [bin_key for bin_key, users in user_bins.items() if len(users) >= max_user_count-5]

# Print the result
print(f"Maximum User Count: {max_user_count}")
print(f"Bins with the highest user count: {max_bins}")

highlight_matrix = np.zeros_like(user_count_matrix)

# Set all bins with the highest user count in the highlight matrix
for bin_key in max_bins:
    highlight_matrix[bin_key[0], bin_key[1]] = max_user_count

fig, ax = plt.subplots(figsize=(10, 8))
# Layer 1: Highlight all bins with the highest user count
# img1 = plt.imshow(
#     highlight_matrix.T,
#     cmap="Reds",
#     origin="lower",
#     extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
#     alpha=0.7,  # Slight transparency for the first layer
#     label="High-Density Bins",
# )

# # Plot the heatmap of user counts in bins
plt.figure(figsize=(10, 8))
img2 = plt.imshow(
    user_count_matrix.T,
    cmap="Blues",
    origin="lower",
    extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
)


plt.colorbar(label="User Count")
plt.title("User Density Heatmap (Distinct Users in Each Bin)")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")

plt.savefig("analysis/heatmap_total.pdf", dpi=600)

# ------------------------------------------------------

polygons = []

# Process each cluster of bins
for bin_key in max_bins:
    # Get the coordinates for each cluster (use bin_x, bin_y)
    cluster_points = [(xedges[bin_key[0]], yedges[bin_key[1]]),
                      (xedges[bin_key[0] + 1], yedges[bin_key[1]]),
                      (xedges[bin_key[0] + 1], yedges[bin_key[1] + 1]),
                      (xedges[bin_key[0]], yedges[bin_key[1] + 1])]

    # Attempt to create a polygon from the cluster points
    polygon = create_polygon_from_cluster(np.array(cluster_points))

    # If valid polygon, add it to the list
    if polygon:
        polygons.append(polygon)

# At this point, 'polygons' should contain all valid polygons created from clusters
# Plot or further process the polygons as needed
for poly in polygons:
    print(f"Polygon: {poly}")
    
    
# bin_coords = [(bin_key[0], bin_key[1]) for bin_key in max_bins]

# # Apply DBSCAN to group bins into clusters
# db = DBSCAN(eps=1, min_samples=2)  # Set eps to 1 or suitable value to cluster adjacent bins
# clusters = db.fit_predict(bin_coords)

# # Create lists to hold the bin coordinates for each cluster
# clustered_bins = {}
# for idx, cluster_id in enumerate(clusters):
#     if cluster_id != -1:  # Ignore noise points (outliers)
#         if cluster_id not in clustered_bins:
#             clustered_bins[cluster_id] = []
#         clustered_bins[cluster_id].append(bin_coords[idx])



# # Create polygons from the clusters
# polygons = []
# for cluster_id, bins in clustered_bins.items():
#     # Create a polygon for each cluster
#     cluster_points = np.array(bins)
#     # Use ConvexHull to form a polygon around the cluster points
#     polygon = Polygon(cluster_points)
#     polygons.append(polygon)

# # If there are multiple polygons, we combine them
# if len(polygons) > 1:
#     combined_polygon = unary_union(polygons)
# else:
#     combined_polygon = polygons[0]




# # Plot the polygons
fig, ax = plt.subplots(figsize=(10, 8))

# # Plot the original polygon (optional, if you want to see the context)
x, y = polygon.exterior.xy
ax.plot(x, y, label="Original Polygon", color="blue", linewidth=2)

# # Plot the grid cells that belong to the high-density bins
for bin_key in max_bins:
    ax.plot([xedges[bin_key[0]], xedges[bin_key[0] + 1]], [yedges[bin_key[1]], yedges[bin_key[1]]], color='red', alpha=0.6)

# # Plot the clustered polygons
for poly in polygons:
    x, y = poly.exterior.xy
    ax.fill(x, y, alpha=0.5, label=f"Cluster {len(polygons)}")

plt.title("Clustered Bins and Polygons")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
plt.legend()
# plt.grid(True)

plt.savefig("analysis/clustered_polygons.pdf", dpi=600)
# # plt.show()

# # Print results
# for i, poly in enumerate(polygons):
#     print(f"Polygon {i+1}: {poly}")