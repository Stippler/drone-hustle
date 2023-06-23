import numpy as np
from math import ceil

import drone.config as config


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
        # TODO: change once chargers are introduced
        self.actual_power = self.max_power
        self.set_charging_power(self.max_power)

    def set_charging_power(self, charging_power: float):
        """
        charging_power - set charging power of battery in watt
        """
        if charging_power > self.max_power:
            raise ValueError(
                f'charging poer {charging_power} is out of bounds {self.max_power}')
        self.actual_power = charging_power
        self.soc_delta_per_timestep = charging_power*(self.resolution/3600)/(self.capacity*1000)

    def update(self):
        """
        charging_power - update soc once per timestep
        """
        self.soc += self.soc_delta_per_timestep
        if self.soc >= 1.0:
            self.soc = 1.0
            return True
        return False

    def remaining_timesteps(self, charging_constraints: np.ndarray):
        # TODO: add charging_constraints for timesteps
        remaining_charge = 1-self.soc
        timesteps = ceil(remaining_charge/self.soc_delta_per_timestep)
        return timesteps
    
    def __str__(self):
        return f"B {self.id}: {self.soc} {self.capacity} {self.actual_power} {self.max_power} {self.soc_delta_per_timestep}"
