from matplotlib.patches import Polygon, Circle
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point, Polygon as ShapelyPolygon, LineString

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def circle_intersects_polygon(circle_center, radius, polygon):
    circle = Point(circle_center).buffer(radius)
    boundary = LineString(polygon.boundary.coords)
    return circle.intersects(boundary)

def is_point_inside_polygon(x, y, polygon):
    point = Point(x, y)
    return polygon.contains(point)

polygon_coords = [
    (3499.77, 1500.07),
    (5798.43, 3799.93),
    (6452.11, 3150.56),
    (5401.44, 2099.71),
    (5751.91, 1749.63),
    (4500.10, 498.92),
]
polygon = Polygon(polygon_coords)
polygon = ShapelyPolygon(polygon_coords)

# Bounding box for the polygon
min_x, min_y, max_x, max_y = polygon.bounds

radius = 100
hex_height = radius * np.sqrt(3)
hex_width = 2 * radius
horiz_spacing = hex_width * 3/4
vert_spacing = hex_height

# Generate points in a hexagonal grid
x_range = np.arange(min_x, max_x + horiz_spacing, horiz_spacing)
y_range = np.arange(min_y, max_y + vert_spacing, vert_spacing)
circle_centers = []

for i, x in enumerate(x_range):
    for j, y in enumerate(y_range):
        # Offset every other row by half the width of a circle
        if i % 2 == 0:
            circle_center = (x, y)
        else:
            circle_center = (x, y + vert_spacing / 2)
        if polygon.contains(Point(circle_center)) or circle_intersects_polygon(circle_center, radius, polygon):
            circle_centers.append(circle_center)

# Number of circles required
num_circles = len(circle_centers)

fig, ax = plt.subplots()
ax.set_aspect('equal')

# Draw the polygon
poly_patch = Polygon(polygon_coords, closed=True, fill=None, edgecolor='r')
ax.add_patch(poly_patch)

# Draw the circles
for center in circle_centers:
    circle_patch = Circle(center, radius, fill=None, edgecolor='b', linestyle='--')
    ax.add_patch(circle_patch)

plt.xlim(min_x - 50, max_x + 50)
plt.ylim(min_y - 50, max_y + 50)
plt.gca().set_aspect('equal', adjustable='box')
# plt.legend()
# plt.axis('off')
# # plt.show()
plt.savefig("analysis/polygon_with_grid_inside.pdf", dpi=600)