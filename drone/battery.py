import drone.config as config
import numpy as np

class Battery:
    def __init__(self, id: int, soc: float, capacity: float, resolution=config.resolution, max_power=config.max_power):
        """
        soc - state of charge in ws
        """
        self.soc = soc
        self.capacity = capacity
        self.max_power = max_power
        self.soc_delta_per_timestep = None
        self.resolution = resolution
        self.id = id
    
    def set_charging_power(self, charging_power):
        """
        charging_power - set charging power of battery
        """
        if charging_power>self.max_power:
            raise ValueError(f'charging poer {charging_power} is out of bounds {self.max_power}')
        self.soc_delta_per_timestep = charging_power*self.resolution/self.capacity

    def update(self):
        """
        charging_power - update soc once per timestep
        """
        self.soc += self.soc_delta_per_timestep