# from env import *
import os
from random import uniform, randint, random
from modules.general import random_identifier, str_to_bool
import numpy as np
import math

import csv
import math



class User:
    def __init__(
        self, user_id, location, bluetooth_id, wifi_id, lte_id, max_step_size=0.1
    ):
        self.user_id = user_id.replace("pedestrian", "P")
        self.bluetooth_id = bluetooth_id.replace("pedestrian", "P")
        self.wifi_id = wifi_id.replace("pedestrian", "P")
        self.lte_id = lte_id.replace("pedestrian", "P")
        
        self.temp_bluetooth_id = bluetooth_id.replace("pedestrian", "P")
        self.temp_wifi_id = wifi_id.replace("pedestrian", "P")
        self.temp_lte_id = lte_id.replace("pedestrian", "P")
        
        self.location = location
        self.max_step_size = max_step_size
        
        self.serving_cellid = None  # current serving base station (cellid)


        self.LTE_RANDOMIZATION_MODE = os.getenv("LTE_RANDOMIZATION_MODE", "time").lower()

        
        # self.mf = mf

        # self.pause_time = uniform(PAUSE_DURATION_MIN, PAUSE_DURATION_MAX)  # Random initial pause time
        # TODO: why do users start off paused?
        self.is_paused = True

        self.identifier_counter = 0
        
        self.timestep_checker = None
        
        self.lte_counter = 0
        
        self.transmit_bluetooth = True
        self.transmit_wifi = True
        self.transmit_lte = True
        
        self.next_bluetooth_transmit = 0
        self.next_wifi_transmit = 0
        self.next_lte_transmit = 0
        
        self.next_bluetooth_refresh = 0
        self.next_wifi_refresh = 0
        self.next_lte_refresh = 0
        
        self.next_protocol_refresh = 0
        
        self.randomized_bluetooth = False
        self.randomized_wifi = False
        self.randomized_lte = False
        self.randomized = False
    
        self.BLUETOOTH_MIN_TRANSMIT = float(os.getenv("BLUETOOTH_MIN_TRANSMIT",0))
        self.BLUETOOTH_MAX_TRANSMIT = float(os.getenv("BLUETOOTH_MAX_TRANSMIT", 0))
        self.WIFI_MIN_TRANSMIT = float(os.getenv("WIFI_MIN_TRANSMIT", 0))
        self.WIFI_MAX_TRANSMIT = float(os.getenv("WIFI_MAX_TRANSMIT", 0))
        self.LTE_MIN_TRANSMIT = float(os.getenv("LTE_MIN_TRANSMIT", 0))
        self.LTE_MAX_TRANSMIT = float(os.getenv("LTE_MAX_TRANSMIT", 0))
        self.BLUETOOTH_MIN_REFRESH = float(os.getenv("BLUETOOTH_MIN_REFRESH", 0))
        self.BLUETOOTH_MAX_REFRESH = float(os.getenv("BLUETOOTH_MAX_REFRESH", 0))
        self.WIFI_MIN_REFRESH = float(os.getenv("WIFI_MIN_REFRESH", 0))
        self.WIFI_MAX_REFRESH = float(os.getenv("WIFI_MAX_REFRESH", 0))
        self.LTE_MIN_REFRESH = float(os.getenv("LTE_MIN_REFRESH", 0))
        self.LTE_MAX_REFRESH = float(os.getenv("LTE_MAX_REFRESH", 0))
        self.ID_RANDOMIZATION = os.getenv("ID_RANDOMIZATION")
        self.ID_TRANSMISSION = os.getenv("ID_TRANSMISSION", None)
        self.ENABLE_PROXIMITY = str_to_bool(os.getenv("ENABLE_PROXIMITY", "false"))
        
        
        self.ENABLE_SYNCED_RANDOMIZATION = str_to_bool(os.getenv("ENABLE_SYNCED_RANDOMIZATION", "false"))
        self.ENABLE_LTE_RANDOMIZATION = str_to_bool(os.getenv("ENABLE_LTE_RANDOMIZATION", "false"))
        self.PROTOCOL_MIN_REFRESH = float(os.getenv("PROTOCOL_MIN_REFRESH", 0))
        self.PROTOCOL_MAX_REFRESH = float(os.getenv("PROTOCOL_MAX_REFRESH", 0))
        
        self.TRANSMIT_WHEN_RANDOMIZED = str_to_bool(os.getenv("TRANSMIT_WHEN_RANDOMIZED", "false"))
        
        if not self.ENABLE_SYNCED_RANDOMIZATION:
            self.set_next_bluetooth_refresh()
            self.set_next_wifi_refresh()
            self.set_next_lte_refresh()
        else:
            self.set_next_protocol_refresh()
        
    def set_next_bluetooth_transmit(self):
        if self.ID_TRANSMISSION == "exponential":
            rate_parameter = self.BLUETOOTH_MAX_TRANSMIT
            duration = math.ceil(np.random.exponential(scale=rate_parameter))
        else:
            duration = round(uniform(self.BLUETOOTH_MIN_TRANSMIT, self.BLUETOOTH_MAX_TRANSMIT))
        # rate_parameter = np.random.uniform(low=self.BLUETOOTH_MIN_TRANSMIT, high=self.BLUETOOTH_MAX_TRANSMIT, size=1)
        # duration = math.ceil(np.random.exponential(scale=1/rate_parameter))
        
        # duration=round(np.random.exponential(self.BLUETOOTH_MAX_TRANSMIT))
        if self.ENABLE_PROXIMITY:
            if self.next_bluetooth_transmit - self.identifier_counter < 60:
                self.next_bluetooth_transmit = self.identifier_counter + duration
        else:
            self.next_bluetooth_transmit = self.identifier_counter + duration

    def set_next_wifi_transmit(self):
        if self.ID_TRANSMISSION == "exponential":
            rate_parameter = self.WIFI_MAX_TRANSMIT
            #duration = math.ceil(np.random.exponential(scale=rate_parameter))
            duration = round(uniform(self.WIFI_MIN_TRANSMIT, self.WIFI_MAX_TRANSMIT))
            #print(duration)
        else:
            duration = round(uniform(self.WIFI_MIN_TRANSMIT, self.WIFI_MAX_TRANSMIT))
        # rate_parameter = np.random.uniform(low=self.WIFI_MIN_TRANSMIT, high=self.WIFI_MAX_TRANSMIT, size=1)
        # duration = math.ceil(np.random.exponential(scale=1/rate_parameter))       
        
        #duration=round(np.random.exponential(self.WIFI_MAX_TRANSMIT))
        if self.ENABLE_PROXIMITY:
            if self.next_wifi_transmit - self.identifier_counter < 60:
                self.next_wifi_transmit = self.identifier_counter + duration
            else:
                print(self.user_id, self.next_lte_transmit, self.identifier_counter)
        else:
            self.next_wifi_transmit = self.identifier_counter + duration

    def set_next_lte_transmit(self):
        if self.ID_TRANSMISSION == "exponential":
            # print("Entered")
            rate_parameter = self.LTE_MAX_TRANSMIT
            duration = math.ceil(np.random.exponential(scale=rate_parameter))
            #print(duration)
        else:
            duration = round(uniform(self.LTE_MIN_TRANSMIT, self.LTE_MAX_TRANSMIT))
        # rate_parameter = np.random.uniform(low=self.LTE_MIN_TRANSMIT, high=self.LTE_MAX_TRANSMIT, size=1)
        # duration = math.ceil(np.random.exponential(scale=rate_parameter))
        # print(self.user_id, duration, rate_parameter)
        #duration=round(np.random.exponential(self.LTE_MAX_TRANSMIT))
        if self.ENABLE_LTE_RANDOMIZATION:
            self.next_lte_transmit = self.lte_counter + duration
        else:
            if self.ENABLE_PROXIMITY:
                if self.next_lte_transmit - self.identifier_counter < 60:
                    self.next_lte_transmit = self.identifier_counter + duration
                else:
                    print(self.user_id, self.next_lte_transmit, self.identifier_counter)
            else:
                self.next_lte_transmit = self.identifier_counter + duration
            # self.next_lte_transmit = self.identifier_counter + duration

    def set_next_bluetooth_refresh(self):
        if self.ID_RANDOMIZATION == "exponential":
            # rate_parameter = np.random.uniform(low=self.BLUETOOTH_MIN_REFRESH, high=self.BLUETOOTH_MAX_REFRESH, size=1)
            rate_parameter = self.BLUETOOTH_MIN_REFRESH
            duration = math.ceil(np.random.exponential(scale=rate_parameter))
        elif self.ID_RANDOMIZATION == "uniform":
            duration = round(np.random.uniform(low=self.BLUETOOTH_MIN_REFRESH, high=self.BLUETOOTH_MAX_REFRESH))
        else:
            # Follow random
	    # randint cannot take float
            duration = randint(int(self.BLUETOOTH_MIN_REFRESH), int(self.BLUETOOTH_MAX_REFRESH))

        self.next_bluetooth_refresh = self.identifier_counter + duration

    def set_next_protocol_refresh(self):
        if self.ID_RANDOMIZATION == "exponential":
            # rate_parameter = np.random.uniform(low=self.PROTOCOL_MIN_REFRESH, high=self.PROTOCOL_MAX_REFRESH, size=1)
            rate_parameter = self.PROTOCOL_MIN_REFRESH
            duration = math.ceil(np.random.exponential(scale=rate_parameter))
        elif self.ID_RANDOMIZATION == "uniform":
            duration = round(np.random.uniform(low=self.PROTOCOL_MIN_REFRESH, high=self.PROTOCOL_MAX_REFRESH))
        else:
            # Follow random
            duration = randint(int(self.PROTOCOL_MIN_REFRESH), int(self.PROTOCOL_MAX_REFRESH))
            
        # rate_parameter = np.random.uniform(low=self.PROTOCOL_MIN_REFRESH, high=self.PROTOCOL_MAX_REFRESH, size=1)
        
        self.next_protocol_refresh = self.identifier_counter + duration
        
    def set_next_wifi_refresh(self):
        if self.ID_RANDOMIZATION == "exponential":
            # rate_parameter = np.random.uniform(low=self.WIFI_MIN_REFRESH, high=self.WIFI_MAX_REFRESH, size=1)
            #rate_parameter = self.WIFI_MIN_REFRESH
            #duration = math.ceil(np.random.exponential(scale=rate_parameter))
            duration = round(np.random.uniform(low=self.WIFI_MIN_REFRESH, high=self.WIFI_MAX_REFRESH))
        elif self.ID_RANDOMIZATION == "uniform":
            duration = round(np.random.uniform(low=self.WIFI_MIN_REFRESH, high=self.WIFI_MAX_REFRESH))
        else:
            # Follow random
            duration = randint(int(self.WIFI_MIN_REFRESH), int(self.WIFI_MAX_REFRESH))
            
        self.next_wifi_refresh = self.identifier_counter + duration

    def set_next_lte_refresh(self):
        if self.ID_RANDOMIZATION == "exponential":
            # rate_parameter = np.random.uniform(low=self.LTE_MIN_REFRESH, high=self.LTE_MAX_REFRESH, size=1)
            rate_parameter = self.LTE_MIN_REFRESH
            duration = math.ceil(np.random.exponential(scale=rate_parameter))
        elif self.ID_RANDOMIZATION == "uniform":
            rate_parameter = self.LTE_MIN_REFRESH
            duration = math.ceil(np.random.exponential(scale=rate_parameter))
            #duration = round(np.random.uniform(low=self.LTE_MIN_REFRESH, high=self.LTE_MAX_REFRESH))
        else:
            # Follow random
            duration = randint(int(self.LTE_MIN_REFRESH), int(self.LTE_MAX_REFRESH))
            
        if self.ENABLE_LTE_RANDOMIZATION:
            self.next_lte_refresh = self.lte_counter + duration
        else:
            self.next_lte_refresh = self.identifier_counter + duration
            

    def randomize_identifiers(self, reset_timers = False,serving_cellid=None):    
        self.identifier_counter += 1
        if self.ENABLE_SYNCED_RANDOMIZATION:
            if reset_timers:
                # self.next_bluetooth_transmit =  self.next_bluetooth_transmit - self.identifier_counter
                # self.next_lte_transmit = self.next_lte_transmit - self.identifier_counter
                # self.next_wifi_transmit = self.next_wifi_transmit - self.identifier_counter
                if self.ENABLE_PROXIMITY:
                    if self.identifier_counter >= self.next_protocol_refresh:
                        self.next_protocol_refresh = self.next_protocol_refresh + self.identifier_counter
                else:
                    self.next_protocol_refresh = self.next_protocol_refresh + self.identifier_counter
                # self.identifier_counter = 0
                self.set_next_protocol_refresh()
                self.temp_bluetooth_id = f"{self.user_id}_B_{random_identifier()}"
                self.temp_lte_id = f"{self.user_id}_L_{random_identifier()}"
                self.temp_wifi_id = f"{self.user_id}_W_{random_identifier()}"
                self.randomized = True
                self.randomized_bluetooth = True
                self.randomized_wifi = True
                self.randomized_lte = True
            else:
                if self.identifier_counter >= self.next_protocol_refresh:
                    self.set_next_protocol_refresh()
                    self.temp_bluetooth_id = f"{self.user_id}_B_{random_identifier()}"
                    self.temp_lte_id = f"{self.user_id}_L_{random_identifier()}"
                    self.temp_wifi_id = f"{self.user_id}_W_{random_identifier()}"
                    self.randomized = True
                    self.randomized_bluetooth = True
                    self.randomized_wifi = True
                    self.randomized_lte = True
                else:
                    self.randomized_bluetooth = False
                    self.randomized_wifi = False
                    self.randomized_lte = False
                    self.randomized = False
            return
            
        
        if self.identifier_counter >= self.next_bluetooth_refresh:
            # print("Randomized ble")
            self.set_next_bluetooth_refresh()
            self.temp_bluetooth_id = f"{self.user_id}_B_{random_identifier()}"
            self.randomized_bluetooth = True
        else:
            self.randomized_bluetooth = False

        if self.identifier_counter >= self.next_wifi_refresh:
            # print("randomized wifi")
            self.set_next_wifi_refresh()
            self.temp_wifi_id = f"{self.user_id}_W_{random_identifier()}"
            self.randomized_wifi = True
        else:
            self.randomized_wifi = False
            
        if self.ENABLE_LTE_RANDOMIZATION:
            self.lte_counter += 1
        if self.LTE_RANDOMIZATION_MODE == "handover":
            # serving_cellid is provided by the caller (generate_user_data loop)
            prev_cellid = self.serving_cellid
            self.serving_cellid = serving_cellid

            # Optional: allow reset_timers to force a randomization
            if reset_timers:
                self.temp_lte_id = f"{self.user_id}_L_{random_identifier()}"
                self.randomized_lte = True

            else:
                 # Policy: randomize ONLY on A -> B (both not None)
                if prev_cellid is not None and serving_cellid is not None and serving_cellid != prev_cellid:
                    self.temp_lte_id = f"{self.user_id}_L_{random_identifier()}"
                    self.randomized_lte = True
                else:
                    self.randomized_lte = False
        else:
            if self.ENABLE_LTE_RANDOMIZATION:   
                if reset_timers:
                    self.lte_counter = 0
                    self.randomized = True
                    self.set_next_lte_refresh()
                    self.temp_lte_id = f"{self.user_id}_L_{random_identifier()}"
                    self.randomized_lte = True
                else:
                    if self.lte_counter >= self.next_lte_refresh:
                    # print("randomized lte")
                        self.set_next_lte_refresh()
                        self.randomized = True
                        self.temp_lte_id = f"{self.user_id}_L_{random_identifier()}"
                        self.randomized_lte = True
                    else:
                        self.randomized = False
                        self.randomized_lte = False
            else:
                if self.identifier_counter >= self.next_lte_refresh:
                # print("randomized lte")
                    self.set_next_lte_refresh()
                    self.temp_lte_id = f"{self.user_id}_L_{random_identifier()}"
                    self.randomized_lte = True
                else:
                    self.randomized_lte = False
            
            
    def transmit_identifiers_force(self):
        self.transmit_bluetooth = True
        self.transmit_wifi = True
        self.transmit_lte = True
        self.randomized_bluetooth = False
        self.randomized_wifi = False
        self.randomized_lte = False
        self.bluetooth_id = self.temp_bluetooth_id
        self.wifi_id = self.temp_wifi_id
        self.lte_id = self.temp_lte_id
        
        
    def transmit_identifiers(self, timestep_checker = None):
            
        ''' since identifier count is increased in randomize identifiers, not increasing during transmit '''

        # if self.user_id == "P_1-1-pt_7123" or self.user_id == "pedestrian_1-1-pt_7123":
        #     print(self.identifier_counter, self.next_bluetooth_transmit, self.next_wifi_transmit, self.next_lte_transmit)
            
        if self.identifier_counter >= self.next_bluetooth_transmit or (self.randomized_bluetooth == True and self.TRANSMIT_WHEN_RANDOMIZED):
            if self.ENABLE_PROXIMITY:
                if self.timestep_checker != timestep_checker:
                    self.timestep_checker = timestep_checker
                    self.set_next_bluetooth_transmit()
            else:
                self.set_next_bluetooth_transmit()
            self.bluetooth_id = self.temp_bluetooth_id
            self.transmit_bluetooth = True
        else:
            self.bluetooth_id = None
            self.transmit_bluetooth = False
            
        if self.identifier_counter >= self.next_wifi_transmit or (self.randomized_wifi == True and self.TRANSMIT_WHEN_RANDOMIZED):
            if self.ENABLE_PROXIMITY:
                if self.timestep_checker != timestep_checker:
                    self.timestep_checker = timestep_checker
                    self.set_next_wifi_transmit()
            else:
                self.set_next_wifi_transmit()
            self.wifi_id = self.temp_wifi_id
            self.transmit_wifi = True
        else:
            self.wifi_id = None
            self.transmit_wifi = False

        if self.ENABLE_LTE_RANDOMIZATION:
            if self.lte_counter >= self.next_lte_transmit or (self.randomized_lte == True and self.TRANSMIT_WHEN_RANDOMIZED):
                self.set_next_lte_transmit()
                self.lte_id = self.temp_lte_id
                self.transmit_lte = True
            else:
                self.lte_id = None
                self.transmit_lte = False
        else:
            if self.identifier_counter >= self.next_lte_transmit or (self.randomized_lte == True and self.TRANSMIT_WHEN_RANDOMIZED):
                if self.ENABLE_PROXIMITY:
                    if self.timestep_checker != timestep_checker:
                        self.timestep_checker = timestep_checker
                        self.set_next_lte_transmit()
                else:
                    self.set_next_lte_transmit()
                self.lte_id = self.temp_lte_id
                self.transmit_lte = True
            else:
                self.lte_id = None
                self.transmit_lte = False
