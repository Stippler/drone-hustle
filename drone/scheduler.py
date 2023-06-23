from typing import List
import numpy as np
import logging
from drone.battery import Battery
import drone.config as config
from drone.types import ChargingBatteries, FinishedBatteries, WaitingBatteries

logger = logging.getLogger(__name__)

class Scheduler:

    def __init__(self, slots: int = config.slot_count):
        self.schedule: np.ndarray = np.ones((1, slots), int)*-1
        self.charging_constraints = np.ones(self.schedule.shape, int)
        self.batteries: List[Battery] = []


        self.waiting_batteries = []
        self.charging_batteries = []
        self.finished_batteries = []


    def check_constraint(self, charging_constraints):
        """
        charging_constraint - numpy array of shape
        """
        if charging_constraints is not None:
            self.charging_constraints = charging_constraints
        # self.update_schedule()

    def check_battery(self, batteries: List[Battery]):
        pass

    def update_schedule(self, waiting_batteries: WaitingBatteries,
                        charging_batteries: ChargingBatteries,
                        finished_batteries: FinishedBatteries) -> WaitingBatteries:
        waiting_batteries.sort(key=lambda battery: battery.soc, reverse=True)
        self.schedule: np.ndarray = np.ones(self.schedule.shape, int)*-1
        i = 0
        for charging_battery in charging_batteries:
            # calculate amount of timestamps needed and ceil
            timesteps = charging_battery.remaining_timesteps(
                self.charging_constraints[i:]
            )
            self.schedule[0, i:i+timesteps] = charging_battery.id
            i += timesteps
        for waiting_battery in waiting_batteries:
            # calculate amount of timestamps needed and ceil
            timesteps = waiting_battery.remaining_timesteps(
                self.charging_constraints[i:])
            self.schedule[0, i:i+timesteps] = waiting_battery.id
            i += timesteps

        # Log the schedule
        formatted_schedule = self.format_schedule()
        if formatted_schedule:
            logger.info(formatted_schedule)

        self.waiting_batteries = waiting_batteries
        self.charging_batteries = charging_batteries
        self.finished_batteries = finished_batteries

        return waiting_batteries
    
    def check_request(self, charge_request: any):
        # TODO: calculate actual finished_batteries in the future do not base on current...
        # TODO: add type hints
        return len(self.finished_batteries)>0

    def format_schedule(self) -> str:
        schedule_strs = []
        for charger_idx, charger in enumerate(self.schedule):
            i = 0
            charger_strs = []
            while i < len(charger):
                battery_id = charger[i]
                if battery_id == -1:
                    break
                start = i
                while i < len(charger) and charger[i] == battery_id:
                    i += 1
                end = i - 1
                charger_strs.append(f"(B {battery_id}: {start}-{end})")
            if charger_strs:
                schedule_strs.append(
                    f"C {charger_idx} -> " + ', '.join(charger_strs))

        return f"Waiting: {len(self.waiting_batteries)} Finished: {len(self.finished_batteries)} Charging Schedule: {'   |   '.join(schedule_strs)}"
