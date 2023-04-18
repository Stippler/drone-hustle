from typing import List
import numpy as np
from drone.battery import Battery
import drone.config as config

class Scheduler:

    def __init__(self, slots: int=config.slot_count):
        self.schedule: np.ndarray = np.ones((1, slots), np.float32)
        self.batteries: List[Battery] = []

    def check_constraint(self, charging_constraints):
        """
        charging_constraint - numpy array of shape
        """
        if charging_constraints is not None:
            self.charging_constraints = charging_constraints
        self.update_schedule()

    def check_battery(self, batteries: List[Battery]):

    def update_schedule(self):
        pass
