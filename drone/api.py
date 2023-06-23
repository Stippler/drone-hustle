import logging
from datetime import datetime
from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from threading import Thread
from drone.simulation import Simulation
from drone.scheduler import Scheduler

logging.basicConfig(level=logging.INFO)

app = FastAPI()
scheduler = Scheduler()
simulation = Simulation(scheduler_callback=scheduler.update_schedule)
thread = Thread(target=simulation.start)
thread.start()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Battery(BaseModel):
    battery_id: str
    state_of_charge: float
    capacity_kwh: float
    max_power_watt: float

@app.post("/battery", 
    summary="Add a battery",
    description="""
    This endpoint is used by the simulation to add a battery to the optimization process.
    All batteries should be added at startup.
    """)
def add_battery(battery: Battery):
    battery = simulation.create_battery(battery)
    return {
        "success": True,
        "message": f"battery {battery.id} added"
    }

class ChargeRequest(BaseModel):
    drone_id: str
    state_of_charge: float # TODO: update documentation that this is anticipated soc
    capacity_kwh: float
    max_power_watt: float
    delta_eta_seconds: int
    force: bool


@app.post("/charge-request", 
    summary="Request for charging",
    description="""
    This endpoint is used by a drone to request a charging station.
    Use `force` for a drone to request an emergency battery.
    """)
def charge_request(charge_request: ChargeRequest):
    # TODO: fix dirty hack that only currently available can be requested
    success = scheduler.check_request(charge_request)
    if success:
        success = simulation.add_request(charge_request)
    return {
        "success": success,
        "message": f"charging request {'accepted' if success else 'declined'}"
    }

class ExchangeRequest(BaseModel):
    drone_id: str
    state_of_charge: float # TODO: update documentation that this is actual soc

@app.put("/exchange", 
    summary="Battery exchange",
    description="""
    This endpoint is used to indicate that a battery exchange has occurred.
    It takes in the ID of the battery that is gone and the ID of the new battery that was received.
    """)
def exchange_battery(exchange_request: ExchangeRequest):
    battery = simulation.exchange_battery(exchange_request)
    return {
        "success": True,
        "id": battery.id,
        "soc": battery.soc,
        "capacity": battery.capacity,
        "max_power": battery.max_power,
        "message": "battery exchange completed"
    }

class DemandEstimation(BaseModel):
    start: datetime
    demand: List[float]
    resolution_ms: int

@app.put("/demand-estimation",
    summary="Demand estimation",
    description="""
    This endpoint is used to send a prognosis of the estimated demand of charged batteries in a certain interval.
    """)
def demand_estimation(demand_estimation: DemandEstimation):
    return

class PriceProfile(BaseModel):
    start: datetime
    price: List[float]
    resolution_ms: int

@app.put("/price-profile",
    summary="Price profile",
    description="""
    This endpoint is used to send a prognosis of the price profile of the electricity.
    """)
def price_profile(price_profile: PriceProfile):
    return
