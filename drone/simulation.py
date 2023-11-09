from typing import Callable, List
from threading import Lock
from time import time, sleep

from drone.battery import Battery
from drone import config
from datetime import datetime
import copy

import numpy as np

import logging
from drone.schedule import Schedule

logger = logging.getLogger(__name__)

def convert_price_profile(profile) -> np.ndarray:
    """converts list of prices with certain resolution to simulation resolution

    Args:
        profile (PriceProfile): price profile and resolution

    Returns:
        np.ndarray: price profile in simulation resolution
    """
    price_profile_array = np.zeros(config.slot_count, dtype=float)

    profile_time_span_s = profile.resolution_ms
    slot_time_span_s = config.resolution

    profile_index = 0
    profile_end = (profile_index+1)*profile_time_span_s

    for slot in range(config.slot_count):
        slot_start = slot*slot_time_span_s
        slot_end = (slot+1)*slot_time_span_s

        # if outside of price profile skip:
        while slot_start>profile_end:
            profile_index += 1
            # profile_start = profile_index*profile_time_span_ms 
            profile_end = (profile_index+1)*profile_time_span_s

        # now slot_start < profile end
        if profile_index>=len(profile.price):
            break

        if slot_end<profile_end:
            # if inside of price profile slot
            price = profile.price[profile_index]
        else:
            # if partly in price profile
            price = 0
            slot_curr = slot_start
            while profile_end<slot_end:
                if profile_index>=len(profile.price):
                    break
                price+=(profile_end-slot_curr)/(slot_end-slot_start)*profile.price[profile_index]
                slot_curr = profile_end
                profile_index += 1
                profile_end = (profile_index+1)*profile_time_span_s
            if profile_index>=len(profile.price):
                break
            price += (slot_end-slot_curr)/(slot_end-slot_start)*profile.price[profile_index]
        price_profile_array[slot] = price
    return price_profile_array

class Simulation:

    def __init__(self, time_factor=config.simulation_time_factor, charger_count: int = 1):
        self.time_factor = time_factor

        self.waiting_batteries: List[Battery] = []
        self.charging_batteries: List[Battery] = []
        self.finished_batteries: List[Battery] = []
        self.demand_event_list = [i*60*60 for i in range(24)]

        self.requests = {}
        self.charger_count = charger_count

        self.lock = Lock()
        self.id_counter = 0

        self.constraints = np.zeros((1, config.slot_count), dtype=bool)
        self.price_profile = np.zeros(config.slot_count, dtype=float)
        
        self.schedule = Schedule()
    
    def get_batteries(self):
        with self.lock:
            batteries = {
                'requests': [],
                'waiting_batteries': [],
                'finished_batteries': [],
                'charging_batteries': []
            }
            for key, battery in self.requests.items():
                batteries['requests'].append({
                        'drone_id': key,
                        'battery_id': battery.id,
                        'soc': battery.soc,
                        'capacity': battery.capacity,
                        'max_power': battery.max_power,
                    }
                )
            for battery in self.waiting_batteries:
                batteries['waiting_batteries'].append({
                        'battery_id': battery.id,
                        'soc': battery.soc,
                        'capacity': battery.capacity,
                        'max_power': battery.max_power,
                    }
                )
            for battery in self.charging_batteries:
                batteries['charging_batteries'].append({
                        'battery_id': battery.id,
                        'soc': battery.soc,
                        'capacity': battery.capacity,
                        'max_power': battery.max_power,
                    }
                )
            for battery in self.finished_batteries:
                batteries['finished_batteries'].append({
                        'battery_id': battery.id,
                        'soc': battery.soc,
                        'capacity': battery.capacity,
                        'max_power': battery.max_power,
                    }
                )
        return batteries

    def get_schedules(self):
        return self.schedule.schedule

    def set_demand(self, demand):
        self.demand_event_list = demand.demand
        self.demand_event_list.sort()
        self.create_schedule(self.current_time, 0)
    
    def set_price_profile(self, price_profile):
        self.price_profile = convert_price_profile(price_profile)
        self.create_schedule(self.current_time, 0)
    
    def get_price_profile(self):
        return self.price_profile

    def check_request(self, charge_request: any):
        return len(self.finished_batteries)>0

    def take_battery(self):
        with self.lock:
            if self.finished_batteries:
                battery = self.finished_batteries.pop(0)
                return True, battery
            else:
                return False, None

    def add_request(self, request):
        with self.lock:
            if self.finished_batteries:
                battery = self.finished_batteries.pop(0)
                self.requests[request.drone_id] = {
                    'charged_battery': battery,
                    'new_battery': Battery(
                        self.id_counter,
                        request.state_of_charge,
                        request.capacity_kwh,
                        max_power=request.max_power_watt
                    )
                }
                self.id_counter += 1
                return True
            else:
                return False

    def clear_batteries(self):
        with self.lock:
            self.waiting_batteries.clear()
            self.charging_batteries.clear()
            self.finished_batteries.clear()
            self.requests.clear()

    def add_battery(self, battery: Battery):
        with self.lock:
            self.waiting_batteries.append(battery)
            self.create_schedule(self.current_time, 0)

    def create_battery(self, battery):
        with self.lock:
            new_battery = Battery(
                id=self.id_counter,
                soc=battery.state_of_charge,
                capacity=battery.capacity_kwh,
                max_power=battery.max_power_watt
            )
            self.id_counter += 1
            if battery.state_of_charge==1:
                self.finished_batteries.append(new_battery)
            else:
                self.waiting_batteries.append(new_battery)
            return new_battery

    def exchange_battery(self, exchange_request):
        with self.lock:
            request = self.requests.pop(exchange_request.drone_id)
            new_battery = request['new_battery']
            self.waiting_batteries.append(new_battery)
            self.create_schedule(self.current_time, 0)
            return request['charged_battery']

    def create_schedule(self, current_time, time_budget):
        # check the most expensive unblocked timeslot and block it until no schedule is feasible
        # if schedule is not feasible unblock least expensive timeslot until feasible

        time_budget *= 0.9
        tik = time()

        demand_array = np.zeros(config.slot_count)
        current_datetime = datetime.fromtimestamp(current_time)
        seconds_since_midnight = (current_datetime.hour * 3600) + (current_datetime.minute * 60) + current_datetime.second

        # self.constraints = np.zeros((1, config.slot_count), dtype=bool)
        # self.price_profile = np.zeros(config.slot_count, dtype=float)

        demand_list = [demand-seconds_since_midnight for demand in self.demand_event_list if demand>=seconds_since_midnight]+\
                      [demand-seconds_since_midnight+24*60*60 for demand in self.demand_event_list if demand<seconds_since_midnight]
        for demand in demand_list[:self.total_batteries()]:
            demand_slot_index = int(demand/config.resolution)
            if demand_slot_index<config.slot_count:
                demand_array[demand_slot_index] += 1

        # TODO: what happens when a drone does not get the battery in time?
        # demand_array:   [ 0, 0, 2, 0, 0, 0, 1]
        # cumsum:         [ 0, 0, 2, 2, 2, 2, 3]
        # after requests: [-1,-1, 1, 1, 1, 1, 2]
        # cumsum after 2 timesteps without exchange: [-1,-1,-1, 0]
        # cumsum after 2 timesteps with    exchange: [ 0, 0, 0, 1]

        demand_array = np.array(np.cumsum(demand_array)-len(self.requests)-len(self.finished_batteries))
        constraint_idx = int(seconds_since_midnight/config.resolution)
        works = self.schedule.update_schedule(
            self.waiting_batteries,
            self.charging_batteries,
            self.finished_batteries,
            demand_array,
            np.concatenate([self.constraints[:, constraint_idx:], self.constraints[:, :constraint_idx]], axis=1)
        )

        if not works:
            self.constraints[:, :]=False
            works = self.schedule.update_schedule(
                self.waiting_batteries,
                self.charging_batteries,
                self.finished_batteries,
                demand_array,
                np.concatenate([self.constraints[:, constraint_idx:], self.constraints[:, :constraint_idx]], axis=1)
            )
            if not works:
                logger.warn('cannot generate a feasible schedule')
                return False

        # Optimize as long as possible:
        sorted_indices = np.argsort(self.price_profile)
        idx = 0
        while time()-tik<time_budget and idx<len(sorted_indices):
            self.constraints[0, sorted_indices[idx]]=True
            works = self.schedule.update_schedule(
                self.waiting_batteries,
                self.charging_batteries,
                self.finished_batteries,
                demand_array,
                np.concatenate([self.constraints[:, constraint_idx:], self.constraints[:, :constraint_idx]], axis=1)
            )
            if not works:
                self.constraints[0, sorted_indices[idx]]=False
                break
            idx+=1
        return True

    def total_batteries(self):
        total_batteries = len(self.finished_batteries)+\
                          len(self.waiting_batteries)+\
                          len(self.charging_batteries)+\
                          len(self.requests)
        return total_batteries

    def start(self):
        index = 0
        index_time = time()
        while True:
            current = time()
            last = current
            self.current_time = index_time

            # current_datetime = datetime.fromtimestamp(current)
            # seconds_since_midnight = (current_datetime.hour * 3600) + (current_datetime.minute * 60) + current_datetime.second
            # curr_slot = int(seconds_since_midnight/config.resolution)

            # while config.resolution < event_time:
            # fire event
            with self.lock:
                # swap fully charged batteries to finished
                swap_batteries = []

                for charging_battery in self.charging_batteries:
                    if not self.constraints[0, 0]:
                        if charging_battery.update():
                            # battery is fully charged
                            swap_batteries.append(charging_battery)
                for swap_battery in swap_batteries:
                    self.charging_batteries.remove(swap_battery)
                    self.finished_batteries.append(swap_battery)

                # swap waiting batteries to charging
                swap_count = self.charger_count - \
                    len(self.charging_batteries)
                swap_batteries = self.waiting_batteries[:swap_count]
                for waiting_battery in swap_batteries:
                    self.charging_batteries.append(waiting_battery)
                    self.waiting_batteries.remove(waiting_battery)
                
                # 

                current = time()
                # remaining time 
                remaining = config.resolution/self.time_factor-(current-last)
                self.create_schedule(last, remaining)
                # Log the schedule
                formatted_schedule = \
                    f'Waiting Batteries: {len(self.waiting_batteries)}, '+\
                    f'Finished Batteries: {len(self.finished_batteries)}, '+\
                    f'Requests: {len(self.requests)} '+self.schedule.format_schedule()
                print(formatted_schedule)
                if formatted_schedule:
                    logger.info(formatted_schedule)

            current = time()
            time_to_sleep = config.resolution/self.time_factor-(current-last)
            if time_to_sleep>0:
                sleep(time_to_sleep)
            else:
                print('warning: simulation is too slow...')
            