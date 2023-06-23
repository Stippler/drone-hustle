from typing import Callable, List
from threading import Lock
from time import time, sleep

from drone.battery import Battery
from drone import config
from drone.types import SchedulerCallback


class Simulation:

    def __init__(self, scheduler_callback: SchedulerCallback, time_factor=config.simulation_time_factor, charger_count: int = 1):
        self.time_factor = time_factor
        self.waiting_batteries: List[Battery] = []
        self.charging_batteries: List[Battery] = []
        self.finished_batteries: List[Battery] = []
        self.requests = {}
        self.charger_count = charger_count
        self.lock = Lock()
        self.scheduler_callback = scheduler_callback
        self.id_counter = 0

    def add_request(self, request):
        success, battery = self.take_battery()
        if success:
            with self.lock:
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

    def add_battery(self, battery: Battery):
        with self.lock:
            self.waiting_batteries.append(battery)
            self.scheduler_callback(
                self.waiting_batteries,
                self.charging_batteries,
                self.finished_batteries
            )

    def take_battery(self):
        with self.lock:
            if self.finished_batteries:
                battery = self.finished_batteries.pop(0)
                self.scheduler_callback(
                    self.waiting_batteries,
                    self.charging_batteries,
                    self.finished_batteries
                )
                return True, battery
            else:
                return False, None

    def create_battery(self, battery):
        with self.lock:
            new_battery = Battery(
                id=self.id_counter,
                soc=battery.state_of_charge,
                capacity=battery.capacity_kwh,
                max_power=battery.max_power_watt
            )
            self.id_counter += 1
            self.waiting_batteries.append(new_battery)
            return new_battery

    def exchange_battery(self, exchange_request):
        with self.lock:
            request = self.requests.pop(exchange_request.drone_id)
            new_battery = request['new_battery']
            self.waiting_batteries.append(new_battery)
            self.scheduler_callback(
                self.waiting_batteries,
                self.charging_batteries,
                self.finished_batteries
            )
            return request['charged_battery']

    def start(self):
        last = time()
        event_time = 0.0
        while True:
            current = time()
            delta = (current-last)*self.time_factor
            event_time += delta
            last = current
            while config.resolution < event_time:
                # fire event
                with self.lock:
                    # swap fully charged batteries to finished
                    swap_batteries = []
                    for charging_battery in self.charging_batteries:
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

                    self.scheduler_callback(
                        self.waiting_batteries,
                        self.charging_batteries,
                        self.finished_batteries
                    )
                event_time -= config.resolution
            sleep(0.8*(config.resolution-event_time)/self.time_factor)
