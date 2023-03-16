# Drone Scheduling

## Story Board

 - Could be simulated
 - Missions
   - Change the Batteries
   - Deliver Food from ... to ...
   - Battery needs 40 minutes
 - Communication
   - Too many orders
   - Too many drones
   - Too little battery
   - Maybe cancel order?
   - Charging Request
      - Acknowledgement
         - Accept
         - Reject
 - Charging Stations are not interconnected
   - Only consider one charging station
 - 15 Minute planning
 - Drone has to come back to a landing platform

## Reference Architecture

 - IBM Platform
 - Drones have "Missions"
   - what route a drone should take
   - what it should pickup
   - ...
 - Missions are assigned on L2
 - Data is coming from L1
    - Historical Data for future planning
 - Planes cannot fly over Tibet
 - Latency of 4G is maximum of 200 milliseconds (Sydney-Portugal)
 - Drone batteries are exchanged
    - multiple batteries are charged at the same time
    - for "charging" a battery can be switched
    - can be only one charging station but more could be possible
    - right now manually
    - proposal is automatic
 - Beyond Vision APIs
    - [Beyond Vision Website](https://beyond-vision.pt/)
    - [Beyond Vision API](https://docs.beyond-vision.pt/bexstream/APIs.html)
    - [Fullscreen Swagger API](https://bexstream-preprod.beyond-vision.pt/swagger/)
 - Time of Arrival is estimated
    - off by something (really small)
    - acceleration is ignored
 - Never tried more than 3/4 drones at the same time

## Integration Plan of Grand Demo

 - Build Webapplication
    - Use Docker
    - [BDM Cloud stuff](https://www.ibm.com/docs/en/dmeu/2.0?topic=model-developing-business-data)

## Related Work

### The Drone Scheduling Problem: A Systematic State-of-the-Art Review

#### Abbrevations

 - unmanned aerial vehicle (UAV)
 - unmanned aircraft system (UAS)
 - remotely piloted aircraft (RPA)
 - remotely piloted vehicle (RPV)
 - Math Definitions
    - $C={1,...,N_C}$ set of launch points
    - $K={1,...,N_k}$ set of available drones
    - $I={1,...,N_I}$ set of customer nodes
    - $p_k,k\in K$ operating cost of a drone associated with
        - maintenance
        - personel
        - operation of control center
        - deprecation cost
        - etc. 26
    - $t_{ik,i} \in I \cup$

#### Drone Sizes

![drone size overview](images/drone-sizes.png)

#### Papers
 - last-mile delivery 10, 11
    - Prime Air (Amazon) 12, 13
    - Wing (Google) 11, 14
 - literature surveys about drone operations, drone routing, etc. 2, 3, 19-23

#### Drone Scheduling Problem

 - launch points
 - flight time depens on battery capacity
    - usually one hour
