import os, sys
sys.path.append(os.getcwd())

import networkx as nx
import matplotlib.pyplot as plt
import random, json
import numpy as np
from shapely.geometry import Polygon, Point, LineString
from scipy.spatial import KDTree
from networkx.readwrite import json_graph
from scipy.spatial import cKDTree
from collections import defaultdict
from modules.general import *

CELL_SPACING = int(os.getenv("CELL_SPACING"))
SCENARIO_NAME = os.getenv("SCENARIO_NAME")
POLYGON_COORDS = eval(os.getenv("POLYGON_COORDS"))

# Step 1: Define the provided polygon coordinates
polygon_coords = POLYGON_COORDS
polygon = Polygon(polygon_coords)

print("Polygon area in mtr2 ", polygon.area)

# Step 2: Generate random points inside the polygon
def random_point_in_polygon(polygon, num_points):
    # Step 1: Get the bounding box of the polygon
    minx, miny, maxx, maxy = polygon.bounds
    
    # Step 2: Estimate grid resolution
    # Calculate the grid step size based on the number of points
    grid_size = int(np.ceil(np.sqrt(num_points)))
    step_x = (maxx - minx) / grid_size
    step_y = (maxy - miny) / grid_size
    
    print(step_x, step_y)
    # Step 3: Generate grid points inside the bounding box
    grid_points = []
    for i in range(grid_size):
        for j in range(grid_size):
            x = minx + i * step_x
            y = miny + j * step_y
            point = Point(x, y)
            if polygon.contains(point):  # Ensure the point lies inside the polygon
                grid_points.append((x, y))
    
    # Step 4: Ensure we return the correct number of points
    # If we have more points than needed, randomly sample from the grid points
    if len(grid_points) > num_points:
        grid_points = random.sample(grid_points, num_points)
    
    return grid_points

def generate_equidistant_graph(polygon, spacing=CELL_SPACING):
    # Step 1: Get the bounding box of the polygon
    minx, miny, maxx, maxy = polygon.bounds
    
    # Step 2: Create a grid of points
    x_coords = np.arange(minx, maxx, spacing)
    y_coords = np.arange(miny, maxy, spacing)
    
    grid_points = []
    for x in x_coords:
        for y in y_coords:
            point = Point(x, y)
            if polygon.contains(point):  # Ensure the point lies inside the polygon
                grid_points.append((x, y))
                
    return grid_points
                
grid_points = generate_equidistant_graph(polygon)

print("total vertices", len(grid_points))

grid_index = create_grid_index(grid_points, CELL_SPACING)

G = nx.Graph()
for idx, point in enumerate(grid_points):
    G.add_node(idx, pos=point)

total_edges = 0
for (cell_x, cell_y), points in grid_index.items():
    # Check points in the current cell and neighboring cells
    neighboring_cells = [
        (cell_x + dx, cell_y + dy)
        for dx in [-1, 0, 1]
        for dy in [-1, 0, 1]
    ]
    for cell in neighboring_cells:
        if cell not in grid_index:
            continue
        for idx1, point1 in points:
            for idx2, point2 in grid_index[cell]:
                if idx1 >= idx2:
                    continue  # Avoid duplicate or reverse comparisons
                # Check the exact distance
                distance = np.linalg.norm(np.array(point1) - np.array(point2))
                if np.isclose(distance, CELL_SPACING, atol=1e-6):  # Allow for floating-point precision
                    edge = LineString([point1, point2])
                    if polygon.contains(edge):  # Ensure the edge lies inside the polygon
                        total_edges +=1
                        G.add_edge(idx1, idx2)
                
num_edges_to_remove = (len(grid_points) // 100) * 5
print("num_edges_to_remove", num_edges_to_remove, " of ", total_edges)
removed_edges = remove_random_edges(G, num_edges_to_remove)

nx.node_link_data(G, edges="edges")
graph_data = json_graph.node_link_data(G)
graph_data = convert_numpy_types(graph_data)

folder_path = f'data/{SCENARIO_NAME}/'
file_path = os.path.join(folder_path, f'graph_{SCENARIO_NAME}.json')
os.makedirs(folder_path, exist_ok=True)

output_file_path = file_path

with open(output_file_path, "w") as f:
    json.dump(graph_data, f, indent=4)

print(f"Generated {output_file_path}.json")
# Step 6: Visualize the graph and save the figure
pos = nx.get_node_attributes(G, 'pos')
plt.figure(figsize=(10, 10))
nx.draw(G, pos, with_labels=False, node_size=50, node_color="blue", edge_color="gray")
polygon_patch = plt.Polygon(polygon_coords, fill=None, edgecolor='black', linewidth=2)
plt.gca().add_patch(polygon_patch)
plt.title("Connected Graph with Edges Inside the Polygon")
plt.xlabel("X")
plt.ylabel("Y")

# Save the plot as an image
plt.savefig(f"data/{SCENARIO_NAME}/graph_{SCENARIO_NAME}.pdf", dpi=600)
print(f"Graph plot saved as 'graph_{SCENARIO_NAME}.pdf'")
