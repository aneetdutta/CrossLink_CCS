import os, sys, libsumo as traci
sys.path.append(os.getcwd())

import traceback
from collections import deque
import time
import csv
from collections import defaultdict
import pathlib

#from modules.general import load_base_stations_xy

from modules.logger import MyLogger

SUMO_BIN_PATH = "/usr/bin/"
SUMO_CFG_FILE = f"{pathlib.Path().resolve()}/{'simulation/sumo/sumo_scenario/most.sumocfg'}"
USER_TIMESTEPS = int(os.getenv("USER_TIMESTEPS"))
SCENARIO_NAME = os.getenv("SCENARIO_NAME")
ml = MyLogger(f"sumo_simulation_{SCENARIO_NAME}")
""" If not person id , save the person id and discard if visited next time"""
visited_person: set = set()

visited_dict = defaultdict(set)

sumo_cmd = [os.path.join(SUMO_BIN_PATH, "sumo"), "-c", SUMO_CFG_FILE]

user_file = f"data/raw_user_data_{SCENARIO_NAME}.csv"

with open(user_file, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=["timestep", "user_id", "loc_x", "loc_y"])
    writer.writeheader()

""" Start TRACI """
traci.start(sumo_cmd)

try:
    # Simulation loop
    user_data, users = deque(), dict()
    timestep = 17999
    #BS_XY_CSV = f"data/opencellid_cells_demo_LTE_212_10_uniqueLoc_XY.csv"
    #stations, stations_by_id = load_base_stations_xy(BS_XY_CSV)

    """timestep - Get current simulation time
    user_ids - Get list of user IDs """
    now = time.time()
    while timestep < USER_TIMESTEPS:
        timestep = traci.simulation.getTime()
        user_ids = traci.person.getIDList()
        # print(len(user_ids))
        if timestep % 50 == 0:
            print(len(user_ids), timestep)
            
        for user_id in user_ids:
            user_location = traci.person.getPosition(user_id)
            #ux, uy = user_location[0], user_location[1]
            user_data.append(
                {
                    "timestep": timestep,
                    "user_id": user_id,
                    "loc_x": user_location[0],
                    "loc_y": user_location[1]
                }
            )        
        
        # Set the speed for all vehicles
        for vehicle_id in traci.vehicle.getIDList():
            traci.vehicle.setMaxSpeed(vehicle_id, 0.2)
            # traci.vehicle.setSpeed(vehicle_id, 1.0)

        # Set the speed for all pedestrians
        for person_id in traci.person.getIDList():
            traci.person.setMaxSpeed(person_id, 0.2)
            # traci.person.setSpeed(person_id, 1.0)
        
        if timestep % 10 == 0:
            with open(user_file, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=["timestep", "user_id", "loc_x", "loc_y"])
                writer.writerows(user_data)
                user_data = deque()
        
        traci.simulationStep()
        
        # for lane in traci.lane.getIDList():
        #     traci.lane.setMaxSpeed(lane, 0.8)
        
    print("Time taken: ", time.time() - now)
    traci.close()
except Exception as e:
    print(f"Error: {e}")
    print(traceback.format_exc())
    traci.close()
    sys.exit(1)

ml.logger.info("Total time take to fetch user_data from sumo_simulation: ", time.time() - now)
