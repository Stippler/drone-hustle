from typing import List
import numpy as np
import logging
from drone.battery import Battery
import drone.config as config
from drone.custom_types import ChargingBatteries, FinishedBatteries, WaitingBatteries

logger = logging.getLogger(__name__)


class Schedule:

    def __init__(self, slots: int = config.slot_count):
        self.optimized_schedule: np.ndarray = np.ones((1, slots), int) * -1
        self.unoptimized_schedule = np.ones((1, slots), int) * -1
        self.demand: np.ndarray = np.zeros(self.optimized_schedule.shape, int)
        self.charging_constraints = np.zeros(self.optimized_schedule.shape, dtype=bool)
        self.demand_estimation = None

    def update_schedule(self,
                        waiting_batteries: WaitingBatteries,
                        charging_batteries: ChargingBatteries,
                        finished_batteries: FinishedBatteries,
                        demand_estimation,
                        charging_constraints) -> bool:

        assert np.all(self.optimized_schedule.shape == charging_constraints.shape)
        self.demand_estimation = demand_estimation
        self.charging_constraints = charging_constraints

        # charge batteries with the highest SoC first
        waiting_batteries.sort(key=lambda battery: battery.soc, reverse=True)
        self.optimized_schedule: np.ndarray = np.ones(self.optimized_schedule.shape, int) * -1
        i = 0

        for charging_battery in charging_batteries:
            # calculate amount of timestamps needed and ceil
            timesteps = charging_battery.remaining_timesteps(
                self.charging_constraints[:, i:]
            )

            if timesteps < 0:
                self.optimized_schedule[0, i:] = charging_battery.id
                i = self.optimized_schedule.shape[1]
                break
            else:
                self.optimized_schedule[0, i:i + timesteps] = charging_battery.id
            i += timesteps
        if i < self.optimized_schedule.shape[1]:
            for waiting_battery in waiting_batteries:
                timesteps = waiting_battery.remaining_timesteps(
                    self.charging_constraints[:, i:])
                # calculate amount of timestamps needed and ceil
                if timesteps < 0:
                    self.optimized_schedule[0, i:] = waiting_battery.id
                    i = self.optimized_schedule.shape[1]
                    break
                else:
                    self.optimized_schedule[0, i:i + timesteps] = waiting_battery.id
                i += timesteps

        # check conformance with demand estimation
        swapped_battery_events = np.insert(np.diff(self.optimized_schedule[0]), 0, 0)
        swapped_battery_sum = np.cumsum(swapped_battery_events != 0)
        return np.all(demand_estimation <= swapped_battery_sum)

    def make_unoptimized_schedule(self,
                                  waiting_batteries: WaitingBatteries,
                                  charging_batteries: ChargingBatteries,
                                  finished_batteries: FinishedBatteries) -> bool:

        unoptimized_schedule: np.ndarray = np.ones(self.optimized_schedule.shape, int) * -1
        charging_constraints = np.zeros((1, config.slot_count), dtype=bool)
        assert np.all(unoptimized_schedule.shape == charging_constraints.shape)

        # charge batteries with the highest SoC first
        waiting_batteries.sort(key=lambda battery: battery.soc, reverse=True)
        i = 0

        for charging_battery in charging_batteries:
            # calculate amount of timestamps needed and ceil
            timesteps = charging_battery.remaining_timesteps(
                charging_constraints[:, i:]
            )

            if timesteps < 0:
                unoptimized_schedule[0, i:] = charging_battery.id
                i = unoptimized_schedule.shape[1]
                break
            else:
                unoptimized_schedule[0, i:i + timesteps] = charging_battery.id
            i += timesteps
        if i < unoptimized_schedule.shape[1]:
            for waiting_battery in waiting_batteries:
                timesteps = waiting_battery.remaining_timesteps(
                    charging_constraints[:, i:])
                # calculate amount of timestamps needed and ceil
                if timesteps < 0:
                    unoptimized_schedule[0, i:] = waiting_battery.id
                    i = unoptimized_schedule.shape[1]
                    break
                else:
                    unoptimized_schedule[0, i:i + timesteps] = waiting_battery.id
                i += timesteps

        self.unoptimized_schedule = unoptimized_schedule
        return True

    def get_load_curve(self, batteries: List[Battery], optimized: bool):
        load_curve = np.zeros(self.optimized_schedule.shape)
        if optimized:
            schedule = self.optimized_schedule
        else:
            schedule = self.unoptimized_schedule

        for i in range(schedule.shape[1]):
            if (optimized and self.charging_constraints[0][i]) or schedule[0][i] == -1:
                load_curve[0][i] = 0
            else:
                battery_id = schedule[0][i]
                charging_battery = next((battery for battery in batteries if battery.id == battery_id), None)
                load_curve[0][i] = charging_battery.actual_power
            print(f'Optimized? {optimized}, schedule entry: {schedule[0][i]}, '
                  f'charging constraint: {self.charging_constraints[0][i]} --> load curve entry: {load_curve[0][i]}')

        return load_curve

    def format_schedule(self) -> str:
        schedule_strs = []
        for charger_idx, charger in enumerate(self.optimized_schedule):
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
