import numpy as np
import json
from pymongo import MongoClient
import csv
import polars as pl
import os, sys
sys.path.append(os.getcwd())
import os.path

SCENARIO_NAME = os.getenv("SCENARIO_NAME")

MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB URI
DATABASE_NAME = SCENARIO_NAME           # Replace with your database name
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

def import_json_to_mongodb(json_file_path, collection):
    # Open and load JSON file
    with open(json_file_path, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    # Ensure data is a list of documents
    if isinstance(data, dict):  # If the JSON is a single dictionary
        data = [data]

    # Insert data into MongoDB
    if data:
        collection.drop()
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")

def import_dict_to_mongodb(dict_, collection):
    data = dict_
    # Ensure data is a list of documents
    if isinstance(data, dict):  # If the JSON is a single dictionary
        data = [data]
    # Insert data into MongoDB
    if data:
        collection.drop()
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")

def import_csv_to_mongodb(csv_file_path, collection):
    # Open the CSV file
    with open(csv_file_path, "r", encoding="utf-8") as csv_file:
        # Read CSV data
        reader = csv.DictReader(csv_file)  # Read as a dictionary per row
        data = [row for row in reader]    # Convert to list of dictionaries

    # Insert data into MongoDB
    if data:
        collection.drop()
        result = collection.insert_many(data)
        print(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")
        

CSV_PATH = f"data/{SCENARIO_NAME}/user_data_{SCENARIO_NAME}.csv"
if os.path.isfile(CSV_PATH):
    import_csv_to_mongodb(CSV_PATH, db[f"user_data_{SCENARIO_NAME}"])
    
CSV_PATH = f"data/{SCENARIO_NAME}/sniffed_data_{SCENARIO_NAME}.csv"
if os.path.isfile(CSV_PATH):
    import_csv_to_mongodb(CSV_PATH, db[f"sniffed_data_{SCENARIO_NAME}"])

# File paths


NPY_FILE_PATH = f"data/{SCENARIO_NAME}/filtered_intramap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if os.path.isfile(NPY_FILE_PATH):
    data = np.load(NPY_FILE_PATH, allow_pickle=True).item()
    json_data = [{"_id": i, "mapping_list": list(item)} for i, item in data.items()]
    import_dict_to_mongodb(json_data, db[f"filtered_intra_{SCENARIO_NAME}"])

NPY_FILE_PATH = f"data/{SCENARIO_NAME}/filtered_intramap_single_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if os.path.isfile(NPY_FILE_PATH):
    data = np.load(NPY_FILE_PATH, allow_pickle=True).item()
    json_data = [{"_id": i, "mapping_list": list(item)} for i, item in data.items()]
    import_dict_to_mongodb(json_data, db[f"filtered_intra_single_{SCENARIO_NAME}"])


NPY_FILE_PATH = f"data/{SCENARIO_NAME}/refined_intramap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if os.path.isfile(NPY_FILE_PATH):
    data = np.load(NPY_FILE_PATH, allow_pickle=True).item()
    json_data = [{"_id": i, "mapping_list": list(item)} for i, item in data.items()]
    import_dict_to_mongodb(json_data, db[f"refined_intra_{SCENARIO_NAME}"])

NPY_FILE_PATH = f"data/{SCENARIO_NAME}/intramap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if os.path.isfile(NPY_FILE_PATH):
    data = np.load(NPY_FILE_PATH, allow_pickle=True).item()
    json_data = [{"_id": i, "mapping_list": list(item)} for i, item in data.items()]
    import_dict_to_mongodb(json_data, db[f"intra_{SCENARIO_NAME}"])

NPY_FILE_PATH = f"data/{SCENARIO_NAME}/refined_intermap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if os.path.isfile(NPY_FILE_PATH):
    data = np.load(NPY_FILE_PATH, allow_pickle=True).item()
    json_data = [{"_id": i, "mapping_list": {k: list(v) for k, v in item.items()}} for i, item in data.items()]
    import_dict_to_mongodb(json_data, db[f"refined_inter_{SCENARIO_NAME}"])

NPY_FILE_PATH = f"data/{SCENARIO_NAME}/intermap_{SCENARIO_NAME}.npy"  # Replace with your .npy file path
if os.path.isfile(NPY_FILE_PATH):
    data = np.load(NPY_FILE_PATH, allow_pickle=True).item()
    json_data = [{"_id": i, "mapping_list": {k: list(v) for k, v in item.items()}} for i, item in data.items()]
    import_dict_to_mongodb(json_data, db[f"inter_{SCENARIO_NAME}"])


PARQUET_FILE_PATH = f"data/{SCENARIO_NAME}/aggregated_id_{SCENARIO_NAME}.parquet"
if os.path.isfile(PARQUET_FILE_PATH):
    df = pl.read_parquet(PARQUET_FILE_PATH)
    data = df.to_dicts()
    import_dict_to_mongodb(data, db[f"aggregated_id_{SCENARIO_NAME}"])

PARQUET_FILE_PATH = f"data/{SCENARIO_NAME}/aggregated_users_{SCENARIO_NAME}.parquet"
if os.path.isfile(PARQUET_FILE_PATH):
    df = pl.read_parquet(PARQUET_FILE_PATH)
    data = df.to_dicts()
    import_dict_to_mongodb(data, db[f"aggregated_users_{SCENARIO_NAME}"])