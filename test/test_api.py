import pytest
from httpx import AsyncClient
from drone.api import app
from time import sleep, time
from datetime import datetime
import drone.config as config

@pytest.mark.asyncio
async def test_batteries_scenario():
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:

        # Clear batteries
        response = await ac.delete("/batteries")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

        # Add demand estimation
        current_datetime = datetime.fromtimestamp(time())
        seconds_since_midnight = (current_datetime.hour * 3600) + (current_datetime.minute * 60) + current_datetime.second
        curr_slot = int(seconds_since_midnight/config.resolution)
        curr_seconds = int(seconds_since_midnight)
        demand_data = {
            "demand": [
                curr_seconds+6*60 for i in range(10)
            ]
        }
        print('sending demand estimation')
        response = await ac.put("/demand-estimation", json=demand_data)
        assert response.status_code == 200
        assert response.json()["success"] == True

        # Add 5 batteries
        for i in range(5):
            # should take 6 minutes for each
            battery_data = {
                "battery_id": f"battery{i}",
                "state_of_charge": 0.99,
                "capacity_kwh": 2,
                "max_power_watt": 2000
            }
            response = await ac.post("/battery", json=battery_data)
            assert response.status_code == 200
            assert response.json()["success"] == True

        # Check if 5 batteries are charged
        # Depending on your API structure, you might need to adjust this step.
        sleep(10)
        response = await ac.get("/batteries")
        assert response.status_code == 200
        data = response.json()
        batteries = data['batteries']
        assert len(batteries['finished_batteries']) == 5
        # Further checks based on your application logic
