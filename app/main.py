from fastapi import FastAPI
from app.nascar import NascarApiClient

nascar = NascarApiClient()

app = FastAPI()

@app.get("/events")
async def get_events():
    """Get NASCAR events"""
    return nascar.get_schedule()

@app.get("/events/current")
async def get_current():
    """Get details of specific NASCAR event"""
    return nascar.get_schedule(current=True)

@app.get("/events/{event}")
async def get_event(event: str):
    """Get details of specific NASCAR event"""
    return nascar.get_schedule(id=event)

# @app.get("/events/{event}/races/{race}")
# async def get_race(event: str, race: str):
#     """Get NASCAR race details"""
#     return get_race_api(id=event, race, api_key)

@app.get("/events/current/races")
async def get_current_races():
    """Get details of specific NASCAR event"""
    return nascar.get_schedule(current=True, races=True)

@app.get("/events/current/races/{race_id}")
async def get_current_race(race_id: str):
    """Get details of specific NASCAR event"""
    return nascar.get_schedule(current=True, races=True, race_id=race_id)

# @app.get("/drivers")
# async def get_drivers():
#     """Get NASCAR drivers"""
#     return get_drivers_api(api_key)

@app.get("/points/{race_id}")
async def get_points(race_id: str):
    """Get NASCAR driver points"""
    return nascar.get_driver_points(race_id)

@app.post("/points/{race_id}")
async def get_points(race_id: str, user_picks: dict):
    """Get NASCAR driver points"""
    if not user_picks:
        return {"error": "Invalid payload"}, 400

    user_points = nascar.calculate_user_points(race_id, user_picks)
    if user_points is None:
        return {"error": "Failed to calculate points"}, 500

    return user_points
    #return nascar.get_points(race_id)