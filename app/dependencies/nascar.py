import requests
from datetime import datetime, timedelta
from typing import Generator, Any, ClassVar, Type

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

from app.models.nascar import ScheduleItem, Driver, RaceDriver

def generate_pydantic_class(fields: Generator[tuple, None, None]) -> Type[BaseModel]:
    class_dict = {}
    for name, type_hint, search_url_variable in fields:
        if type_hint is ClassVar:
            class_dict[name] = ClassVar
        else:
            json_schema_extra = {'search_url': f'/api/drivers/{search_url_variable}'}
            field = Field(title=name, description=f'{name} desc', json_schema_extra=json_schema_extra)
            class_dict[name] = (type_hint, field)
    return type("GeneratedPydanticClass", (BaseModel,), class_dict)

class DriverSelectForm(BaseModel):
    search_select_multiple: list[str] = Field(title="Select 3 Drivers", description="drivers desc", json_schema_extra={'search_url': '/api/drivers/1'})
    #thing: str = Field(title="drivers", description="drivers desc", json_schema_extra={'search_url': '/api/drivers/1'})

    @field_validator("search_select_multiple")
    def validate_value(cls, search_select_multiple):
        # Custom validation logic goes here
        if len(search_select_multiple) != 3:
            raise PydanticCustomError("lower", "Must pick 3 drivers exactly")
        return search_select_multiple
    
    # @field_validator("thing")
    # def validate_value(cls, thing):
    #     # Custom validation logic goes here
    #     if thing != "right":
    #         raise PydanticCustomError("lower", "Must pick 3 drivers exactly")
    #     return thing

def load_json(url):
    json_response = requests.get(url)
    return json_response.json()

def get_full_schedule():
    # Get the NASCAR schedule feed
    schedule_url = "https://cf.nascar.com/cacher/2023/1/schedule-feed.json"
    schedule_response = requests.get(schedule_url)
    schedule_data = schedule_response.json()
    return schedule_data

def get_full_race_schedule_model(id=None):
    full_schedule = get_full_schedule()
    full_schedule_sorted = sorted(full_schedule, key=lambda x: x['start_time_utc'])
    filtered_schedule = [ScheduleItem(**item) for item in full_schedule_sorted if (item['event_name'] == 'Race' and (id==None or item['race_id'] == id ))]
    if id:
        return filtered_schedule[0]
    return filtered_schedule

def get_current_weekend_schedule():
    # Get the NASCAR schedule feed
    schedule_data = get_full_schedule()

    # Find the race for this weekend
    current_date = datetime.now()
    #current_date = datetime.strptime("2023-11-03T15:05:00", "%Y-%m-%dT%H:%M:%S")
    current_weekend_race = None

    for race in schedule_data:
        if race['event_name'] == 'Race':
            race_date = datetime.strptime(race["start_time"], "%Y-%m-%dT%H:%M:%S")
            if current_date <= race_date <= current_date + timedelta(days=6):
                current_weekend_race = race
                break

    return current_weekend_race

def get_weekend_feed(race_id):
    # Get the weekend feed for the specified race
    weekend_feed_url = f"https://cf.nascar.com/cacher/2023/1/{race_id}/weekend-feed.json"
    weekend_feed_response = requests.get(weekend_feed_url)
    weekend_feed_data = weekend_feed_response.json()
    return weekend_feed_data

def get_race_drivers(race_id):
    weekend_feed = get_weekend_feed(race_id)
    drivers_models = []
    for run in weekend_feed['weekend_runs']:
        if run['run_type'] == 2:
            drivers_models = [RaceDriver(**item) for item in run['results']]
    return drivers_models

def get_drivers(series=None, id=None):
    drivers = load_json("https://cf.nascar.com/cacher/drivers.json")
    drivers_models = [Driver(**item) for item in drivers['response'] if (series==None or item['Driver_Series'] == series) and (id==None or item['Driver_ID'] == id)]
    return drivers_models

def get_drivers_list(race_weekend_feed):
    # Create a list of drivers with their car number and image URL
    drivers_list = []

    for driver in race_weekend_feed["weekend_race"][0]["results"]:
        car_number = driver["car_number"]
        driver_url = f"https://cf.nascar.com/data/images/carbadges/1/{car_number}.png"
        drivers_list.append({"driver_name": driver["driver_fullname"], "car_number": car_number, "image_url": driver_url})

    return drivers_list

if __name__ == "__main__":
    # Get the current weekend's race
    current_weekend_race = get_current_weekend_schedule()

    if current_weekend_race:
        race_id = current_weekend_race["race_id"]
        print(race_id)
        
        # Get the weekend feed for the current race
        race_weekend_feed = get_weekend_feed(race_id)

        # Get the list of drivers and their image URLs
        drivers_list = get_drivers_list(race_weekend_feed)

        # Print the list of drivers
        for driver in drivers_list:
            print(f"Driver: {driver['driver_name']}, Car Number: {driver['car_number']}, Image URL: {driver['image_url']}")
    else:
        print("No race scheduled for this weekend.")
