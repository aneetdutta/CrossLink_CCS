import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
from shapely.geometry import Point, Polygon as ShapelyPolygon, LineString
from modules.general import dump_orjson, extract_orjson
from modules.general import str_to_bool
import random
# Provided coordinates for the polygon
from modules.logger import MyLogger

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
ml = MyLogger(f"sl_coordinates_{SCENARIO_NAME}")

ENABLE_BLUETOOTH = True #str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
WIFI_RANGE = int(os.getenv("WIFI_RANGE", 30))
BLUETOOTH_RANGE = int(os.getenv("BLUETOOTH_RANGE", 10))
LTE_RANGE = int(os.getenv("LTE_RANGE", 100))


def is_point_inside_polygon(x, y, polygon):
    point = Point(x, y)
    return polygon.contains(point)

def circle_intersects_polygon(circle_center, radius, polygon):
    circle = Point(circle_center).buffer(radius)
    boundary = LineString(polygon.boundary.coords)
    return circle.intersects(boundary)

def generate_sniffer_locations():
    polygon_coords = [
        (3499.77, 1500.07),
        (5798.43, 3799.93),
        (6452.11, 3150.56),
        (5401.44, 2099.71),
        (5751.91, 1749.63),
        (4500.10, 498.92),
    ]
    
    polygon = ShapelyPolygon(polygon_coords)

    # Bounding box for the polygon
    min_x, min_y, max_x, max_y = polygon.bounds

    # Radius of circles
    if ENABLE_BLUETOOTH:
        radius = BLUETOOTH_RANGE
    else:
        radius = LTE_RANGE
        
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

    # Plotting the result
    # fig, ax = plt.subplots()
    # ax.set_aspect('equal')

    # # Draw the polygon
    # poly_patch = Polygon(polygon_coords, closed=True, fill=None, edgecolor='r')
    # ax.add_patch(poly_patch)

    # # Draw the circles
    # for center in circle_centers:
    #     circle_patch = Circle(center, radius, fill=None, edgecolor='b', linestyle='--')
    #     ax.add_patch(circle_patch)

    # plt.xlim(min_x - 50, max_x + 50)
    # plt.ylim(min_y - 50, max_y + 50)
    # plt.gca().set_aspect('equal', adjustable='box')
    # # plt.legend()
    # plt.axis('off')
    # # plt.show()
    # plt.savefig('monaco.png', transparent=True, dpi=600)

    ml.logger.info(f"Total number of sniffers placed: {num_circles}")
    print(f"Total number of sniffers placed: {num_circles}")
    dump_orjson('full_coverage_sniffer_location_ble.json', {"sniffer_location": circle_centers})
    
    
# generate_sniffer_locations()


def generate_partial_sniffer_coverage(num_sniffers = 200):
    full_coverage_sniffer_data = extract_orjson('sniffer_location/full_coverage_wifi_sniffer_location.json')
    sniffer_locations = full_coverage_sniffer_data["sniffer_location"]
    partial_coverage = []
    
    points = [
        (4408.45,2262.60),
        (4573.07,1705.79),
        (5989.28,3308.41),
        (5952.97,3625.55)
    ]
    polygon = ShapelyPolygon(points)
    
    partial_cov_temp = []
    for loc in sniffer_locations:
        if is_point_inside_polygon(loc[0], loc[1], polygon):
            partial_cov_temp.append(loc)
    
    print(len(partial_cov_temp))
    
    partial_coverage = random.sample(partial_cov_temp, num_sniffers)
    print(len(partial_coverage))
    dump_orjson('sniffer_location/partial_coverage_sniffer_location1.json', {"sniffer_location": partial_coverage})
    
    
    
generate_sniffer_locations()
