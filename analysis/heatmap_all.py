import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import seaborn as sns
from shapely.geometry import Point, Polygon
from matplotlib.patches import Polygon as MplPolygon

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

df = pd.read_csv("data/raw_user_data_scenario_sumo_512.csv")

# Define polygon coordinates
polygon_coords = [(3499.77, 1500.07), (5798.43, 3799.93), (6452.11, 3150.56), (5401.44, 2099.71), (5751.91, 1749.63), (4500.10, 498.92)]
polygon = Polygon(polygon_coords)

# Extract x and y coordinates
# x = df['loc_x']
# y = df['loc_y']


# kde = gaussian_kde(np.vstack([x, y]), bw_method='scott')  # Adjust bandwidth method
# x_mesh, y_mesh = np.meshgrid(
#     np.linspace(x.min(), x.max(), 20),  # Increase grid resolution
#     np.linspace(y.min(), y.max(), 20)   # Increase grid resolution
# )
# density_values = kde(np.vstack([x_mesh.ravel(), y_mesh.ravel()]))

# # Rescale the density values to represent user counts
# density_values_scaled = density_values * len(x)  # Scale by the number of users
# density_values_scaled[density_values_scaled < 0] = 0  # Clip negative densities (if any)

# # Reshape into a grid for visualization
# density_grid = density_values_scaled.reshape(x_mesh.shape)

# # Plot the density map
# plt.figure(figsize=(10, 8))
# plt.imshow(density_grid, cmap="Blues", origin="lower", extent=[x.min(), x.max(), y.min(), y.max()])
# plt.colorbar(label="User Density (scaled to counts)")
# plt.title("User Density Heatmap")
# plt.savefig("analysis/Heatmap1.pdf", dpi=600)
# plt.show()


# user_positions = df[['loc_x', 'loc_y']].apply(lambda row: Point(row['loc_x'], row['loc_y']), axis=1)
# inside_polygon_mask = user_positions.apply(lambda point: polygon.contains(point))


# Define the number of bins (resolution) and edges for the histogram
# Define the number of bins (resolution) and edges for the histogram
# Define the number of bins (resolution) and edges for the histogram
x_range = df['loc_x'].max() - df['loc_x'].min()
y_range = df['loc_y'].max() - df['loc_y'].min()

n_bins_x = int(np.ceil(x_range / 20))  # Number of bins for x-axis
n_bins_y = int(np.ceil(y_range / 20))  # Number of bins for y-axis


print(n_bins_x, n_bins_y)
# Define the bin edges
xedges = np.linspace(df['loc_x'].min(), df['loc_x'].max(), n_bins_x + 1)
yedges = np.linspace(df['loc_y'].min(), df['loc_y'].max(), n_bins_y + 1)

# n_bins = 100
# xedges = np.linspace(df['loc_x'].min(), df['loc_x'].max(), n_bins)
# yedges = np.linspace(df['loc_y'].min(), df['loc_y'].max(), n_bins)

# Use numpy.digitize to vectorize the binning process for loc_x and loc_y
# Use numpy.digitize to vectorize the binning process for loc_x and loc_y
bin_x = np.digitize(df['loc_x'].values, xedges) - 1  # Get bin indices for x
bin_y = np.digitize(df['loc_y'].values, yedges) - 1  # Get bin indices for y
# Ensure that bin_x and bin_y are within the correct range
bin_x = np.clip(bin_x, 0, n_bins_x - 1)  # Clamp the values between 0 and n_bins_x - 1
bin_y = np.clip(bin_y, 0, n_bins_y - 1)  # Clamp the values between 0 and n_bins_y - 1

# Create a dictionary to store unique users per bin using sets
user_bins = {}

# Track unique users in bins using a set
for i, user_id in enumerate(df['user_id']):
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
max_bins = [bin_key for bin_key, users in user_bins.items() if len(users) >= max_user_count -10]

highlight_matrix = np.zeros_like(user_count_matrix)

# Set all bins with the highest user count in the highlight matrix
for bin_key in max_bins:
    highlight_matrix[bin_key[0], bin_key[1]] = max_user_count
    
    
# Print the result
print(f"Maximum User Count: {max_user_count}")
print(f"Bins with the highest user count: {max_bins}")

# Plot the heatmap of user counts in bins
plt.figure(figsize=(10, 8))


plt.imshow(
    highlight_matrix.T,
    cmap="Reds",
    origin="lower",
    extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],
    alpha=0.7,  # Slight transparency for the first layer
    label="High-Density Bins",
)




# plt.imshow(user_count_matrix.T, cmap="Blues", origin="lower", extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
plt.colorbar(label="User Count")
plt.title("User Density Heatmap (Distinct Users in Each Bin)")
plt.xlabel("X Coordinate")
plt.ylabel("Y Coordinate")
# plt.show()

# heatmap_data, xedges, yedges = np.histogram2d(df['loc_x'], df['loc_y'], bins=(100, 100), density=False)

# # Plot the heatmap with user counts
# plt.figure(figsize=(10, 8))
# plt.imshow(heatmap_data.T, cmap="Blues", origin="lower", aspect='auto', interpolation='nearest')
# plt.colorbar(label="User Count")
# plt.title("User Density Heatmap (User Count)")
# plt.xlabel("X Coordinate")
# plt.ylabel("Y Coordinate")
# plt.show()

# # heatmap_data = np.histogram2d(df['loc_x'], df['loc_y'], bins=(100, 100))

# # Visualize the heatmap
# plt.figure(figsize=(8, 6))
# sns.heatmap(heatmap_data[0], cmap='viridis', cbar=True)
# plt.title('User Movement Heatmap within Polygon')
# plt.xlabel('X')
# plt.ylabel('Y')
# polygon_patch = MplPolygon(polygon_coords, closed=True, fill=True, edgecolor='red', linewidth=2)
# plt.gca().add_patch(polygon_patch)
plt.savefig("analysis/heatmap_all.pdf", dpi=600)
# plt.show()



# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from shapely.geometry import Polygon
# from matplotlib.patches import Polygon as MplPolygon

# # Load the dataset
# df = pd.read_csv("data/raw_user_data_scenario_512_filtered.csv")

# # Define polygon coordinates
# polygon_coords = [(3499.77, 1500.07), (5798.43, 3799.93), (6452.11, 3150.56), 
#                   (5401.44, 2099.71), (5751.91, 1749.63), (4500.10, 498.92)]
# polygon = Polygon(polygon_coords)

# # Create a 2D heatmap grid using user x, y coordinates, ensuring the range covers the polygon
# x_min, x_max = min([x for x, y in polygon_coords]), max([x for x, y in polygon_coords])
# y_min, y_max = min([y for x, y in polygon_coords]), max([y for x, y in polygon_coords])

# # Generate 2D histogram/heatmap
# heatmap_data, x_edges, y_edges = np.histogram2d(df['loc_x'], df['loc_y'], bins=(20, 20), range=[[x_min, x_max], [y_min, y_max]])

# # Visualize the heatmap
# plt.figure(figsize=(8, 6))
# # Transpose the heatmap to align correctly with the x and y axes
# ax = sns.heatmap(heatmap_data.T, cmap='viridis', cbar=True, xticklabels=np.round(x_edges, 2), yticklabels=np.round(y_edges, 2))

# plt.title('User Movement Heatmap within Polygon')
# plt.xlabel('X')
# plt.ylabel('Y')

# # Add the polygon overlay
# polygon_patch = MplPolygon(polygon_coords, closed=True, fill=False, edgecolor='red', linewidth=2)
# plt.gca().add_patch(polygon_patch)

# # Ensure the plot limits match the polygon and data range
# plt.xlim(x_min, x_max)
# plt.ylim(y_min, y_max)

# # Show the plot
# plt.show()
