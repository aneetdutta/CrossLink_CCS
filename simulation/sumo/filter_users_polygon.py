import os, sys
sys.path.append(os.getcwd())

from collections import deque
from modules.general import str_to_bool
import polars as pl
from modules.general import is_point_inside_polygon
from modules.logger import MyLogger
from collections import defaultdict
from shapely.geometry import Polygon, Point
import csv
from tqdm import tqdm

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
POLYGON_COORDS = eval(os.getenv("POLYGON_COORDS"))

ml = MyLogger(f"filter_user_polygon_{SCENARIO_NAME}")
INPUT_CSV_PATH = f"data/raw_user_data_{SCENARIO_NAME}.csv"
OUTPUT_CSV_PATH = f"data/raw_user_data_filter_polygon_{SCENARIO_NAME}.csv"
chunk_size = 10000
# print("Data loaded")
polygon = Polygon(POLYGON_COORDS)

""" If not person id , save the person id and discard if visited next time"""
visited_person: set = set()

visited_person = set()

# Open the CSV file and read row by row
# Batch write rows for efficiency
batch_size = 10000
batch = []

with open(INPUT_CSV_PATH, "r", encoding="utf-8") as input_csv, \
     open(OUTPUT_CSV_PATH, "w", encoding="utf-8", newline="") as output_csv:
    
    reader = csv.reader(input_csv)
    writer = csv.writer(output_csv)

    # Copy the header row to the new CSV
    header = next(reader)
    writer.writerow(header)

    # Process each row
    for i, row in enumerate(reader, start=1):
        #print("Aneet")
        if i % 10000 == 0:
            print(f"Processed {i} rows...")

        try:
            # Extract user ID and coordinates
            user_id = str(row[1])
            if user_id in visited_person:
                continue
            
            loc_x = float(row[2])
            loc_y = float(row[3])
            point = Point(loc_x, loc_y)

            # Skip if the point is not inside the polygon
            if not polygon.contains(point):
                visited_person.add(user_id)
                continue

            # Add to batch
            batch.append(row)

            # Write batch to the output CSV
            if len(batch) >= batch_size:
                writer.writerows(batch)
                batch = []

        except ValueError:
            print(f"Skipping row due to invalid data: {row}")

    # Write any remaining rows in the batch
    if batch:
        writer.writerows(batch)

print("Processing complete!")
