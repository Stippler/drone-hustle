from drone.simulation import convert_price_profile
import logging
from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import drone.config as config
from threading import Thread
from drone.simulation import Simulation

logging.basicConfig(level=logging.INFO)

app = FastAPI()
simulation = Simulation()
thread = Thread(target=simulation.start)
thread.start()

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.delete("/batteries",
            summary="Remove all batteries",
            description="""
    This endpoint is used to remove all batteries.
    """)
def remove_batteries():
    simulation.clear_batteries()
    return {
        "success": True,
        "message": f"all batteries removed successfully"
    }


class Battery(BaseModel):
    battery_id: str = Field(example="battery1")
    state_of_charge: float = Field(example=0.9)
    capacity_kwh: float = Field(example=2)
    max_power_watt: float = Field(example=2000)


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
    drone_id: str = Field(example="drone123")
    state_of_charge: float = Field(
        example=0.75, description="Anticipated state of charge.")
    capacity_kwh: float = Field(example=1.5)
    max_power_watt: float = Field(example=1500)
    delta_eta_seconds: int = Field(
        example=60*10, description="Time in seconds until estimated time of arrival.")


@app.post("/charge-request",
          summary="Request for charging",
          description="""
    This endpoint is used by a drone to request a battery at a charging station shortly before arrival.
    Only currently available batteries are taken into consideration.
    """)
def charge_request(charge_request: ChargeRequest):
    success = simulation.check_request(charge_request)
    if success:
        success = simulation.add_request(charge_request)
    return {
        "success": success,
        "message": f"charging request {'accepted' if success else 'declined'}"
    }


class ExchangeRequest(BaseModel):
    drone_id: str = Field(example="drone123")
    state_of_charge: float = Field(
        example=0.5, description="Actual state of charge of the battery.")


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
    demand: List[int] = Field(example=[i*60*60 for i in range(24)],
                              description="List representing battery demand events in seconds after midnight.")


@app.put("/demand-estimation",
         summary="Demand estimation",
         description="""
    This endpoint is used to send a prognosis of the estimated demand of charged batteries of a day. 
    The demand should be a list of events in seconds when batteries will be exchanged relative to midnight.
    Event time can only be within 24 hours.
    """)
def demand_estimation(demand_estimation: DemandEstimation):
    simulation.set_demand(demand_estimation)
    return {
        "success": True
    }


class PriceProfile(BaseModel):
    price: List[float] = Field(example=[
        25.02, 18.29, 16.04, 14.6, 14.95, 14.5, 10.76, 12.01, 
        12.39, 14.04, 14.68, 16.08, 16.08, 16.05, 16.04, 16.1,
        23.93, 26.9, 26.36, 23.98, 16.09, 14.08, 12.44, 0.04
    ], description="List of prices at various intervals, must be at most 24 hours long.")
    resolution_s: int = Field(
        example=3600, description="Resolution of price profile in seconds.")

@app.put("/price-profile",
         summary="Price profile",
         description="""
    This endpoint is used to send a prognosis of the price profile of the electricity.
    """)
def update_price_profile(price_profile: PriceProfile):
    # TODO: fix, make seconds instead of milliseconds, tell diogo
    simulation.set_price_profile(price_profile)
    return {
        "success": True
    }


@app.get("/price-profile",
         summary="Price profile",
         description="""
    This endpoint is used to get a prognosis of the price profile of the electricity.
    """)
def get_price_profile():
    price_profile = [float(price) for price in simulation.get_price_profile()]
    return {
        "success": True,
        "price_profile": price_profile
    }


@app.get("/batteries",
         summary="status of batteries",
         description="""
    This endpoint returns a list of batteries with their status.
    """)
def batteries():
    batteries = simulation.get_batteries()
    return {
        "success": True,
        "batteries": batteries
    }


@app.get("/schedules",
         summary="current charging schedule",
         description="""
    This endpoint returns the current charging schedules.
    """)
def schedule():
    schedule = {
        "resolution_seconds": config.resolution,
        "schedules": list([[int(e) for e in schedule] for schedule in simulation.get_schedules()])
    }
    return {
        "success": True,
        "schedules": schedule
    }
