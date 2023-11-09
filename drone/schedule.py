from typing import List
import numpy as np
import logging
from drone.battery import Battery
import drone.config as config
from drone.types import ChargingBatteries, FinishedBatteries, WaitingBatteries

logger = logging.getLogger(__name__)

# TODO: rename Scheduler to schedule and make immutable
class Schedule:

    def __init__(self, slots: int = config.slot_count):
        self.schedule: np.ndarray = np.ones((1, slots), int)*-1
        self.demand: np.ndarray = np.zeros((1, slots), int)
        self.charging_constraints = np.ones(self.schedule.shape, int)

    def update_schedule(self,
                        waiting_batteries: WaitingBatteries,
                        charging_batteries: ChargingBatteries,
                        finished_batteries: FinishedBatteries,
                        demand_estimation,
                        charging_constraints) -> WaitingBatteries:

        self.demand_estimation = demand_estimation
        self.charging_constraints = np.ones(self.schedule.shape, bool)
        # TODO: check somewhere if charging constraint array is too long (longer than schedule)
        self.charging_constraints[0:charging_constraints.shape[0], :] = charging_constraints
        # print('charging constraints: ', self.charging_constraints[0, :90])
        # print('demand estimation: ', self.demand_estimation[:90])

        waiting_batteries.sort(key=lambda battery: battery.soc, reverse=True)
        self.schedule: np.ndarray = np.ones(self.schedule.shape, int)*-1
        i = 0
        for charging_battery in charging_batteries:
            # calculate amount of timestamps needed and ceil
            timesteps = charging_battery.remaining_timesteps(
                self.charging_constraints[:, i:]
            )
            if timesteps<0:
                self.schedule[0, i:] = charging_battery.id
                i = self.schedule.shape[1]
                break
            else:
                self.schedule[0, i:i+timesteps] = charging_battery.id
            i += timesteps
        if i<self.schedule.shape[1]:
            for waiting_battery in waiting_batteries:
                timesteps = waiting_battery.remaining_timesteps(
                    self.charging_constraints[:, i:])
                # calculate amount of timestamps needed and ceil
                if timesteps<0:
                    self.schedule[0, i:] = waiting_battery.id
                    i = self.schedule.shape[1]
                    break
                else:
                    self.schedule[0, i:i+timesteps] = waiting_battery.id
                i += timesteps

        # check conformance with demand estimation
        swapped_battery_events = np.insert(np.diff(self.schedule[0]), 0, 0)
        swapped_battery_sum = np.cumsum(swapped_battery_events!=0)
        return np.all(demand_estimation<=swapped_battery_sum)

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

        return f"Charging Schedule: {'   |   '.join(schedule_strs)}"
