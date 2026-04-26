import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.sniffer import Sniffer
import traceback
import numpy as np
from modules.general import extract_orjson, str_to_bool
from collections import deque
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import itertools
from typing import List, Dict, Any
import polars as pl
import pandas as pd

import os.path

SCENARIO_NAME = os.getenv("SCENARIO_NAME")
ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))

SNIFFER_DATA_SOURCE = os.getenv("SNIFFER_DATA_SOURCE")

if SNIFFER_DATA_SOURCE:
    print(SNIFFER_DATA_SOURCE)
    sniffed_file = f"data/{SNIFFER_DATA_SOURCE}/raw_sniffed_data_{SNIFFER_DATA_SOURCE}.csv"
    print(sniffed_file)
    if not os.path.isfile(sniffed_file):
        sniffed_file = f"data/{SCENARIO_NAME}/raw_sniffed_data_{SCENARIO_NAME}.csv"
else:
    sniffed_file = f"data/{SCENARIO_NAME}/raw_sniffed_data_{SCENARIO_NAME}.csv"
    

# Load the CSV file using Polars
df = pl.read_csv(sniffed_file)

# Filter rows based on enabled protocols
if not ENABLE_BLUETOOTH:
    df = df.filter(df['protocol'] != 'Bluetooth')
if not ENABLE_WIFI:
    df = df.filter(df['protocol'] != 'WiFi')
if not ENABLE_LTE:
    df = df.filter(df['protocol'] != 'LTE')

folder_path = f'data/{SCENARIO_NAME}/'
file_path = os.path.join(folder_path, f'sniffed_data_{SCENARIO_NAME}.csv')
os.makedirs(folder_path, exist_ok=True)

# Save the filtered data to a new file
df.write_csv(file_path)

print(f"Filtered data saved to: {file_path}")
