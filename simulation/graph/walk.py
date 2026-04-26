import os, sys
sys.path.append(os.getcwd())

import networkx as nx
import random
import numpy as np
import json
from tqdm import tqdm
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from networkx.readwrite import json_graph
from collections import defaultdict
import matplotlib.colors as mcolors

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
USER_TIMESTEPS = int(os.getenv("USER_TIMESTEPS"))
TOTAL_NUMBER_OF_USERS = int(os.getenv("TOTAL_NUMBER_OF_USERS"))
MAX_MOBILITY_FACTOR = float(os.getenv('MAX_MOBILITY_FACTOR'))
MIN_MOBILITY_FACTOR = 0

n_users = TOTAL_NUMBER_OF_USERS  # Set the number of users (you can change this number)

with open(f"data/{SCENARIO_NAME}/graph_{SCENARIO_NAME}.json", "r") as f:
    graph_data = json.load(f)

G = json_graph.node_link_graph(graph_data)

print("Number of nodes:", G.number_of_nodes())
print("Number of edges:", G.number_of_edges())

# Function to get the position along the edge between two vertices
def get_position_on_edge(start_pos, end_pos, distance):
    # Calculate the vector between start and end
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    # Normalize the vector and scale it by the distance
    length = np.sqrt(dx**2 + dy**2)
    scale = distance / edge_length if edge_length > 0 else 0  # Avoid division by zero
    # dx /= length
    # dy /= length
    # Move from start position along the edge
    new_x = start_pos[0] + dx * scale
    new_y = start_pos[1] + dy * scale
    dislength = np.sqrt((new_x - start_pos[0]) **2 + (new_y - start_pos[1])**2)
    
    return (new_x, new_y), dislength

# Step 2: Randomly assign start and destination nodes for each user
users = {}
for i in range(n_users):
    start_node = random.choice(list(G.nodes))
    end_node = random.choice(list(G.nodes))
    users[i] = {
        'start_node': start_node,
        'end_node': end_node,
        'current_node': start_node,
        'current_pos': G.nodes[start_node]['pos'],
        'remaining_distance': 0,  # Distance to move along the current edge
        'positions': [],  # List to store the user's positions at each timestep
        'velocity': round(random.uniform(MIN_MOBILITY_FACTOR, MAX_MOBILITY_FACTOR), 2),  # Users move at 0.8 m/s
    }

# Step 2: Calculate the shortest paths using Dijkstra's algorithm for each user
for i in range(n_users):
    users[i]['path'] = nx.shortest_path(G, source=users[i]['start_node'], target=users[i]['end_node'])

# Simulate movement for all users
for timestep in tqdm(range(USER_TIMESTEPS), total=USER_TIMESTEPS):
    # print("Timestep", timestep)
    for i in range(n_users):
        current_user = users[i]
        if current_user['current_node'] == current_user['end_node']:
            # User reached the end node, reassign new end node and recompute path
            new_end_node = random.choice(list(G.nodes))
            while new_end_node == current_user['current_node']:  # Ensure the new end node is not the same as the current node
                new_end_node = random.choice(list(G.nodes))
            
            current_user['end_node'] = new_end_node
            current_user['path'] = nx.shortest_path(G, source=current_user['current_node'], target=new_end_node)

        next_node = current_user['path'][current_user['path'].index(current_user['current_node']) + 1]
        edge = (current_user['current_node'], next_node)
        edge_length_real = np.linalg.norm(np.array(G.nodes[edge[1]]['pos']) - np.array(G.nodes[edge[0]]['pos']))
        edge_length = np.linalg.norm(np.array(G.nodes[next_node]['pos']) - np.array(current_user['current_pos']))

        # print(timestep, current_user['remaining_distance'], edge_length, edge_length_real)
        # print(current_user)
        
        if current_user['remaining_distance'] <= edge_length_real:
            velocity = round(random.uniform(MIN_MOBILITY_FACTOR, MAX_MOBILITY_FACTOR), 2)
            # Move in this edge
            new_position, dislength = get_position_on_edge(current_user['current_pos'], G.nodes[next_node]['pos'], velocity)
            current_user['positions'].append(new_position)
            current_user['current_pos'] = new_position
            current_user['remaining_distance'] += dislength#current_user['velocity']
        else:
            # Move to the next node
            current_user['remaining_distance'] = 0
            current_user['current_node'] = next_node
            current_user['current_pos'] = G.nodes[current_user['current_node']]['pos']
            current_user['positions'].append(current_user['current_pos'])

user_dict = defaultdict(list)

for i in range(n_users):
    print(i, len(users[i]['positions']))
    for j, user_pos in enumerate(users[i]['positions']):
        user_dict[f"P{i}"].append([float(user_pos[0]), float(user_pos[1])])

# Save the user_dict as a JSON file
with open(f"data/graph_user_positions_{SCENARIO_NAME}_{TOTAL_NUMBER_OF_USERS}.json", "w") as json_file:
    json.dump(user_dict, json_file, indent=4)
    
