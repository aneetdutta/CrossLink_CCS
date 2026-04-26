from dataclasses import dataclass, field
from modules.user import User
from collections import deque
# from env import *
from math import sqrt

@dataclass
class Sniffer:
    id: int
    location: tuple
    bluetooth_range: int
    wifi_range: int
    lte_range: int
    detected_devices: list = field(default_factory=list)
    sniffed_devices: dict = field(default_factory=dict)

    def detect_raw_users(self, user_id, timestep, user_location, user_lte_id = None, user_wifi_id=None, user_bluetooth_id = None, transmit_ble=None, transmit_wifi=None, transmit_lte=None):
        
        distance = sqrt(
            (float(self.location[0]) - float(user_location[0])) ** 2
            + (float(self.location[1]) - float(user_location[1])) ** 2
        )
        # List of detected users
        detected_users = [None] * 3
        index = 0

        f = False
        if distance <= self.bluetooth_range and transmit_ble:
            f = True
            detected_users[index] = {
                # **common_info,
                # "_id": ObjectId(),
                "timestep": timestep,# + round(random.uniform(0, 1), 6),
                "user_id": user_id,
                "sniffer_id": self.id,
                "sl_x": self.location[0],
                "sl_y": self.location[1],
                "ul_x": user_location[0],
                "ul_y": user_location[1],
                "protocol": "Bluetooth",
                "id": user_bluetooth_id,
            }
            index += 1

        if distance <= self.wifi_range and transmit_wifi:
            detected_users[index] = {
                # **common_info,
                # "_id": ObjectId(),
                "timestep": timestep,# + round(random.uniform(0, 1), 6),
                "user_id": user_id,
                "sniffer_id": self.id,
                "sl_x": self.location[0],
                "sl_y": self.location[1],
                "ul_x": user_location[0],
                "ul_y": user_location[1],
                "protocol": "WiFi",
                "id": user_wifi_id,
            }
            index += 1

        if distance <= self.lte_range and transmit_lte:
            detected_users[index] = {
                # **common_info,
                # "_id": ObjectId(),
                "timestep": timestep,# + round(random.uniform(0, 1), 6),
                "user_id": user_id,
                "sniffer_id": self.id,
                "sl_x": self.location[0],
                "sl_y": self.location[1],
                "ul_x": user_location[0],
                "ul_y": user_location[1],
                "protocol": "LTE",
                "id": user_lte_id,
               
            }
            index += 1

        # if f:
        #     print(detected_users[:index])
        # Remove excess None values in the preallocated list
        return detected_users[:index]
