import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from shapely.geometry import Point, Polygon

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

df = pd.read_csv("data/raw_user_data_scenario_sumo_512.csv")


# # Combine all timesteps and bin locations
# # Optionally, adjust bin size for your data scale
# df['loc_x_bin'] = (df['loc_x'] // 1).astype(int)
# df['loc_y_bin'] = (df['loc_y'] // 1).astype(int)

# # Group by binned locations and count user occurrences
# location_density = df.groupby(['loc_x_bin', 'loc_y_bin']).size().reset_index(name='user_count')

# # KDE for smoothing
# x = location_density['loc_x_bin']
# y = location_density['loc_y_bin']
# density = gaussian_kde(np.vstack([x, y]))
# x_mesh, y_mesh = np.meshgrid(np.linspace(x.min(), x.max(), 100),
#                              np.linspace(y.min(), y.max(), 100))
# density_values = density(np.vstack([x_mesh.ravel(), y_mesh.ravel()]))

# # Reshape density to match grid for plotting
# density_grid = density_values.reshape(x_mesh.shape)

# # Plotting the density
# plt.figure(figsize=(10, 8))
# sns.heatmap(density_grid, cmap="Blues", cbar=True, 
#             xticklabels=False, yticklabels=False)
# plt.title("Most Traversed User Path Density")
# plt.xlabel("loc_x")
# plt.ylabel("loc_y")

# plt.savefig("analysis/Conclave.pdf", dpi=600)
# # plt.show()


# Define the polygon and load the data
polygon_coords = [(3499.77, 1500.07), (5798.43, 3799.93), (6452.11, 3150.56),
                  (5401.44, 2099.71), (5751.91, 1749.63), (4500.10, 498.92)]
polygon = Polygon(polygon_coords)


# Filter points within the polygon
# print("Hello")
# df['inside_polygon'] = df.apply(
#     lambda row: polygon.contains(Point(row['loc_x'], row['loc_y'])),
#     axis=1
# )
# print("Hello1")

import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from scipy.stats import gaussian_kde
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
import alphashape

# Define the polygon coordinates
polygon_coords = [(3499.77, 1500.07), (5798.43, 3799.93), (6452.11, 3150.56),
                  (5401.44, 2099.71), (5751.91, 1749.63), (4500.10, 498.92)]
polygon = Polygon(polygon_coords)

df_in_polygon = df

# Extract x and y coordinates
x = df_in_polygon['loc_x']
y = df_in_polygon['loc_y']

# Compute KDE
kde = gaussian_kde(np.vstack([x, y]))
x_mesh, y_mesh = np.meshgrid(
    np.linspace(x.min(), x.max(), 50),
    np.linspace(y.min(), y.max(), 50)
)
density_values = kde(np.vstack([x_mesh.ravel(), y_mesh.ravel()]))
density_grid = density_values.reshape(x_mesh.shape)

# Identify dense points (top 5% density)
threshold = np.percentile(density_values, 95)
dense_points = np.vstack([x_mesh.ravel(), y_mesh.ravel()]).T[density_values > threshold]

# Cluster the dense points using DBSCAN
clustering = DBSCAN(eps=300, min_samples=5).fit(dense_points)
dense_points_df = pd.DataFrame(dense_points, columns=["x", "y"])
dense_points_df['cluster'] = clustering.labels_

# Rank clusters by density
cluster_densities = {}
for cluster_id in np.unique(dense_points_df['cluster']):
    if cluster_id == -1:  # Ignore noise
        continue
    cluster_points = dense_points_df[dense_points_df['cluster'] == cluster_id]
    cluster_density = kde(np.vstack([cluster_points['x'], cluster_points['y']])).sum()
    cluster_densities[cluster_id] = cluster_density

# Get top 2 clusters
top_clusters = sorted(cluster_densities.items(), key=lambda x: x[1], reverse=True)[:2]

# Generate concave hulls for top clusters
concave_hulls = []
for cluster_id, _ in top_clusters:
    cluster_points = dense_points_df[dense_points_df['cluster'] == cluster_id][['x', 'y']].values
    if len(cluster_points) < 3:  # Skip if fewer than 3 points
        print(f"Cluster {cluster_id} has too few points for a concave hull.")
        concave_hulls.append(None)
        continue
    alpha = 1.0  # Start with a larger alpha value
    hull = alphashape.alphashape(cluster_points, alpha)
    if hull.is_empty:  # Handle empty geometry
        print(f"Cluster {cluster_id} produced an empty geometry. Adjusting alpha.")
        alpha = 5.0  # Increase alpha
        hull = alphashape.alphashape(cluster_points, alpha)
    concave_hulls.append(hull)

# Visualize the result
plt.figure(figsize=(10, 8))
sns.heatmap(density_grid, cmap="Blues", cbar=True, xticklabels=False, yticklabels=False)

# Overlay concave hulls
for i, hull in enumerate(concave_hulls, 1):
    if hull:
        x_hull, y_hull = hull.exterior.xy
        plt.plot(
            (x_hull - x.min()) / (x.max() - x.min()) * 100,
            (y_hull - y.min()) / (y.max() - y.min()) * 100,
            label=f'Concave {i}', linewidth=2, color=f'C{i}'
        )

plt.title("Top 2 Concaves by User Density")
plt.legend()
plt.savefig("analysis/concave.pdf", dpi=600)


# Output the concave hulls
for idx, hull in enumerate(concave_hulls, 1):
    print(f"Concave {idx}: {hull}")
