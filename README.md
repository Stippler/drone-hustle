# Battery Charging Service

# Roadmap

 - [ ] REST API
 - [ ] Implement Scheduler
   - [ ] Charge most capacity first
   - [ ] Constraint, currently charging battery cannot be changed (but charging process can be paused)
   - [ ] Constraint: Availability of Energy
     - A minute per percent state of charge to duration
     - Amount of batteries that need to be ready per timeslot
   - [ ] Usage of Battery/Per Minute must be available
     - [ ] We always want a certain number on Batteries on Stock
       - if too low send out warning message (not important)
   - [ ] Battery Simulator
 - [ ] Confidence Estimator
   - [ ] Electricity Prices

# Questions

 - Simulate Battery Charging
   - We implement battery charging simulation.
   - How long does a battery load?
   - Is the charging curve important? How does the charging curve look like? Can we make it linear?
 - Charging station specifics
   - How many batteries should each station hold?
   - How many chargers do we have per station? Can we assume one?
 - Drone demand prediction
   - How often does a drone come per hour?
   - Is the probability evenly distributed?
   - Is there an estimated variance too?
   - Are the demand predictions fixed size or floating?
 - Who wants to write a paper?

## Endpoints

### POST /battery

This endpoint is used by the simulation to add a battery to the optimization process.
All batteries should be added at startup.

**Request:**
```
{
    "battery_id": "string",
    "state_of_charge": float,
    "capacity_kwh": float,
    "max_power_watt": float
}
```


### POST /charge-request

This endpoint is used by a drone to request a charging station. It returns a JSON response indicating whether the request was accepted or not.
Use `force` for a drone to request an emergency battery.


**Request:**
```
{
    "drone_id": "string",
    "battery_id": "string",
    "state_of_charge": float,
    "capacity_kwh": float,
    "max_power_watt": float,
    "eta: timestamp,
    "force": boolean
}
```

**Response:**

```
{
    "success": true/false,
    "message": "string"
}
```

### PUT /exchange

This endpoint is used to indicate that a battery exchange has occurred.
It takes in the ID of the battery that is gone and the ID and battery current of the new battery that was received.

**Request**

```
{
    "old_battery_id": "string",
    "new_battery_id": "string"
}
```

**Response**

```
{
    "success": true,
    "message": "Exchange recorded successfully"
}
```

### PUT /demand-estimation

This endpoint is used to send a prognosis of the estimated demand of charged batteries in a certain interval.

**Request**
```
{
    start: timestamp,
    demand: List[float],
    resolution_ms: int
}
```

### PUT /price-profile

This endpoint is used to send a prognosis of the price profile of the electricity.

**Request**
```
{
    start: timestamp,
    price: List[float],
    resolution_ms: int
}
```


# Drone Simulator

This is a simple simulation of drones flying towards a cursor using Pygame.
The simulation includes a `Drone` class with 2D coordinates, velocity, and acceleration vectors, and methods for updating and drawing the drones on the screen.

## Requirements

 - Python 3.x
 - Pygame
 - Numpy

## Usage

Start with:

```
python -m drone.main
```

