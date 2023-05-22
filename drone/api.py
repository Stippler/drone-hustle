from datetime import datetime
from typing import List
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

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

    def __str__(self):
        return f"Battery(battery_id={self.battery_id}, state_of_charge={self.state_of_charge}, capacity={self.capacity_kwh}, max_power={self.max_power_watt})"

@app.post("/battery")
def add_battery(battery: Battery):
    print(f'POST /battery {battery}')
    return {
        "success": True,
        "message": "battery added"
    }

class ChargeRequest(BaseModel):
    drone_id: str
    state_of_charge: float
    capacity_kwh: float
    max_power_watt: float
    delta_eta_seconds: int
    force: bool

    def __str__(self):
        return f"ChargeRequest(drone_id={self.drone_id}, state_of_charge={self.state_of_charge}, capacity={self.capacity_kwh}, max_power={self.max_power_watt}, delta_eta={self.delta_eta_seconds})"

@app.post("/charge-request")
def charge_request(charge_request: ChargeRequest):
    print(f'POST /charge_request {charge_request}')
    return {
        "success": True,
        "message": "charging request accepted"
    }

class ExchangeRequest(BaseModel):
    old_battery_id: str
    new_battery_id: str

    def __str__(self):
        return f"ExchangeRequest(old_battery_id={self.old_battery_id}, new_battery_id={self.new_battery_id})"

@app.put("/exchange")
def exchange_battery(exchange_request: ExchangeRequest):
    print(f'PUT /exchange {exchange_request}')
    return {
        "success": True,
        "message": "battery exchange completed"
    }


class DemandEstimation(BaseModel):
    start: datetime
    demand: List[float]
    resolution_ms: int

    def __str__(self):
        return f"DemandEstimation(start={self.start}, demand={self.demand}, resolution_ms={self.resolution_ms})"

@app.put("/demand-estimation")
def demand_estimation(demand_estimation: DemandEstimation):
    print(f'PUT /demand-estimation {demand_estimation}')
    return

class PriceProfile(BaseModel):
    start: datetime
    price: List[float]
    resolution_ms: int

    def __str__(self):
        return f"PriceProfile(start={self.start}, price={self.price}, resolution_ms={self.resolution_ms})"

@app.put("/price-profile")
def price_profile(price_profile: PriceProfile):
    print(f'PUT /price-profile {price_profile}')
    return