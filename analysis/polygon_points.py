import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
from shapely.geometry import Polygon, Point
from matplotlib.patches import Circle
import json
# Function to calculate the distance between two points
def distance(p1, p2):
    return np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Function to interpolate points between two vertices
def interpolate_points(p1, p2, step):
    d = distance(p1, p2)
    num_points = int(d // step)
    return [(p1[0] + i * (p2[0] - p1[0]) / num_points, 
             p1[1] + i * (p2[1] - p1[1]) / num_points) for i in range(num_points)]

# Function to calculate all points along the polygon edges
def points_on_polygon(polygon_coords, step):
    points = []
    for i in range(len(polygon_coords)):
        p1 = polygon_coords[i]
        p2 = polygon_coords[(i + 1) % len(polygon_coords)]  # Next vertex, wrapping around
        points.extend(interpolate_points(p1, p2, step))
    return points

# Polygon coordinates
polygon_coords = [
    (3499.77, 1500.07),
    (5798.43, 3799.93),
    (6452.11, 3150.56),
    (5401.44, 2099.71),
    (5751.91, 1749.63),
    (4500.10, 498.92),
]

polygon_original = Polygon(polygon_coords)

# Generate points lying on the polygon
step_distance = 100  # in meters
polygon_points = points_on_polygon(polygon_coords, step_distance)

# Extract x and y coordinates for plotting
x_coords, y_coords = zip(*polygon_coords)
x_points, y_points = zip(*polygon_points)

buffer = 100  # Increase the buffer to widen the axes
x_min, x_max = min(x_coords) - buffer, max(x_coords) + buffer
y_min, y_max = min(y_coords) - buffer, max(y_coords) + buffer

# Label each point
for i, (x, y) in enumerate(zip(x_points, y_points), start=1):
    plt.text(x, y, str(i), fontsize=8, ha='right', color='black')

# Print the coordinates of the points
for i, (x, y) in enumerate(zip(x_points, y_points), start=1):
    print(f"Point {i}: ({x:.2f}, {y:.2f})")

# Define the labels and the corresponding vertices
polygon1_labels = [56, 18, 6, 72]  # Example polygon 1 label indices
polygon2_labels = [46, 29, 33, 42]  # Example polygon 2 label indices

# Create polygon 1 by selecting vertices based on labels
polygon1_coords = [polygon_points[label - 1] for label in polygon1_labels]
# Create polygon 2 by selecting vertices based on labels
polygon2_coords = [polygon_points[label - 1] for label in polygon2_labels]


polygon_1 = Polygon(polygon1_coords)
polygon_2 = Polygon(polygon2_coords)

print(f"Area of Polygon (Original): {polygon_original.area}")
print(f"Area of Polygon 1: {polygon_1.area}")
print(f"Area of Polygon 2: {polygon_2.area}")


print(f"Percentage: {(polygon_1.area + polygon_2.area)/polygon_original.area}")
# Plot the polygon and the points
plt.figure(figsize=(10, 8))

plt.plot(x_coords + (x_coords[0],), y_coords + (y_coords[0],), label='Polygon', linestyle='--', color='blue')  # Close the polygon
plt.scatter(x_points, y_points, color='red', s=10, label='Points on Polygon')

# Label each point
for i, (x, y) in enumerate(zip(x_points, y_points), start=1):
    plt.text(x, y, str(i), fontsize=8, ha='right', color='black')

# Plot the selected polygons (polygon1 and polygon2)
polygon1_x, polygon1_y = zip(*polygon1_coords)
polygon2_x, polygon2_y = zip(*polygon2_coords)

plt.plot(polygon1_x + (polygon1_x[0],), polygon1_y + (polygon1_y[0],), label='Polygon 1', linestyle='-', color='green')
plt.plot(polygon2_x + (polygon2_x[0],), polygon2_y + (polygon2_y[0],), label='Polygon 2', linestyle='-', color='orange')

# Label the axes and title
plt.xlabel('X Coordinates')
plt.ylabel('Y Coordinates')
plt.title('Points on Polygon with Labeled Vertices')
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("analysis/polygon_points2.pdf", dpi=600)
# plt.show()

# Print the coordinates of the selected vertices for polygons
print("Coordinates of Polygon 1:")
for label, (x, y) in zip(polygon1_labels, polygon1_coords):
    print(f"Vertex {label}: ({x:.2f}, {y:.2f})")

print("\nCoordinates of Polygon 2:")
for label, (x, y) in zip(polygon2_labels, polygon2_coords):
    print(f"Vertex {label}: ({x:.2f}, {y:.2f})")



with open('sniffer_location/full_coverage_wifi_sniffer_location.json') as f:
    sniffer_coordinates = json.load(f)["sniffer_location"]
    print(len(sniffer_coordinates))

partial_sniffer_coordinates = []

for point in sniffer_coordinates:
    if polygon_1.contains(Point(point)) or polygon_2.contains(Point(point)):
        partial_sniffer_coordinates.append(point)
    
min_x, min_y, max_x, max_y = polygon_original.bounds

radius = 30
hex_height = radius * np.sqrt(3)
hex_width = 2 * radius
horiz_spacing = hex_width * 3/4
vert_spacing = hex_height

# Generate points in a hexagonal grid
x_range = np.arange(min_x, max_x + horiz_spacing, horiz_spacing)
y_range = np.arange(min_y, max_y + vert_spacing, vert_spacing)

fig, ax = plt.subplots()
ax.set_aspect('equal')

from matplotlib.patches import Polygon
# Draw the polygon
poly_patch = Polygon(polygon_coords, closed=True, fill=None, edgecolor='r')
ax.add_patch(poly_patch)

# Draw the circles
for center in partial_sniffer_coordinates:
    circle_patch = Circle(center, radius, fill=None, edgecolor='b', linestyle='--')
    ax.add_patch(circle_patch)

plt.xlim(min_x - 50, max_x + 50)
plt.ylim(min_y - 50, max_y + 50)
plt.gca().set_aspect('equal', adjustable='box')
# plt.legend()
# plt.axis('off')
# # plt.show()
plt.savefig("analysis/polygon_with_sniffers.pdf", dpi=600)

print(len(partial_sniffer_coordinates))
partial_sniffer_coords_dict = {"sniffer_location": partial_sniffer_coordinates}

# Output the new JSON
output_json = json.dumps(partial_sniffer_coords_dict, indent=4)
# print(output_json)

# Optionally, save to a file
with open("sniffer_location/partial_coverage.json", "w") as output_file:
    output_file.write(output_json)