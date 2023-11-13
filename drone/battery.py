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
                f'charging power {charging_power} is out of bounds {self.max_power}')
        self.actual_power = charging_power
        self.soc_delta_per_timestep = charging_power * (self.resolution / 3600) / (self.capacity * 1000)

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
        """
        Calculates the number of remaining time steps based on charging constraints.

        Parameters:
        charging_constraints (np.ndarray): An array representing charging constraints.

        Returns:
        int: The number of remaining time steps if constraints allow charging within those steps.
             Returns -1 if constraints exceed the available number of time steps.
        """
        needed_charge = 1 - self.soc  # Calculate the remaining charge
        minimum_needed_time_steps = ceil(needed_charge / self.soc_delta_per_timestep)  # Calculate remaining time steps

        # Count the number of time steps needed to get the minimum number of unconstrained charging time steps
        count_false = 0
        for i, val in enumerate(charging_constraints[0]):
            if not val:
                count_false += 1
            if count_false >= minimum_needed_time_steps:
                return i + 1  # returning the number of indices including the current one

        return -1  # Return -1 if needed steps are not available

    def __str__(self):
        return f"B {self.id}: soc {self.soc*100}%, capacity {self.capacity}kWh, " \
               f"charging power {self.actual_power}W/{self.max_power}W, " \
               f"soc increase per timestep {self.soc_delta_per_timestep}"
