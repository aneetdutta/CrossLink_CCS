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
    
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

df = pd.read_csv("data/raw_user_data_scenario_sumo_512.csv")

df_sorted = df.sort_values(by=["user_id", "timestep"])

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