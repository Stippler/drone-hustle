from typing import Callable, List

from pydantic import BaseModel
from drone.battery import Battery


WaitingBatteries = List[Battery]
ChargingBatteries = List[Battery]
FinishedBatteries = List[Battery]
SchedulerCallback = Callable[
    [WaitingBatteries, ChargingBatteries, FinishedBatteries],
    WaitingBatteries
]
