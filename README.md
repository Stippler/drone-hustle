# Battery Charging Service

   - Batteries can only be exchanged when they are full

# ToDos

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
 - Who wants to write a paper?


## Endpoints

### Charging Station 

This endpoint is used by a drone to request a charging station. It returns a JSON response indicating whether the request was accepted or not.


**Request:**
```
{
    "drone_id": "string",
}
```

**Response:**

```
{
    "success": true/false,
    "message": "string"
}
```
 
### Emergency Battery Endpoint

This endpoint is used by a drone to request an emergency battery. It returns a JSON response indicating whether the request was accepted or not.

**Request**

```
{
    "drone_id": "string"
}
```

**Response**

```
{
    "success": true/false,
    "message": "string"
}
```

### Exchange Happened Endpoint

This endpoint is used to indicate that a battery exchange has occurred. It takes in the ID of the battery that is gone and the ID and battery current of the new battery that was received.

**Request**

```
{
    "old_battery_id": "string",
    "new_battery_id": "string",
    "new_battery_current": "float"
}
```

**Response**

```
{
    "success": true,
    "message": "Exchange recorded successfully"
}
```

# Drone Optimization Problem

This is a simple simulation of drones flying towards a cursor using Pygame.
The simulation includes a `Drone` class with 2D coordinates, velocity, and acceleration vectors, and methods for updating and drawing the drones on the screen.

## Requirements

 - Python 3.x
 - Pygame
 - Numpy

TODO: requirements.txt will follow...

## Usage

Start with:

```
python -m drone.main
```

## MIP Formulation

The optimization of the charging schedule of the drone is done by solving the underlying MIP.
Decision Variables, Objective Function and the Constraints are given below.

### Decision Variables

Let `n` be the number of drones, `m` be the number of packages, and `T` be the total number of time steps in the planning horizon.

1. `c[i][t]`: a binary variable that equals 1 if drone i is charging at time step t, and 0 otherwise.
2. `p[k][t]`: a binary variable that equals 1 if package k is on a drone at time step t, and 0 otherwise.
3. `d[i][j][t]`: a binary variable that equals 1 if drone i is delivering a package to location j at time step t, and 0 otherwise.

### Objective Function

```
minimize sum(i=1 to n, t=1 to T) (1 - c[i][t])
```

### Constraints

 - Each drone can only carry one package at a time.

```
sum(k=1 to m, t=1 to T) p[k][t] <= 1, for all i
```

 - Each package must be picked up at its source location.

```
sum(i=1 to n, t=1 to T) p[k][t] = 1, for all k
```

 - Each package must be delivered to its destination location.

```
sum(i=1 to n, t=1 to T) d[i][j][t] = 1, for all j
```

 - Each drone can only pick up a package if it is at the source location of that package.
```
p[k][t] <= 1 - sum(i!=j, t=1 to T) d[i][source[k]][t], for all k, t
```

 - Each drone can only deliver a package if it is carrying that package.

```
d[i][j][t] <= p[k][t], for all i, j, k, t
```

