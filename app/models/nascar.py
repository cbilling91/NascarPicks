from __future__ import annotations

from typing import List
from datetime import date

from pydantic import BaseModel


class ScheduleItem(BaseModel):
    start_time: str
    end_time: str
    event_name: str
    race_id: int
    track_id: int
    track_name: str
    race_name: str
    series_id: int
    run_type: int
    start_time_utc: str
    end_time_utc: date


class RaceDriver(BaseModel):
    run_id: int
    car_number: str
    vehicle_number: str
    manufacturer: str
    driver_id: int
    driver_name: str
    finishing_position: int
    best_lap_time: float
    best_lap_speed: float
    best_lap_number: int
    laps_completed: int
    comment: str
    delta_leader: float
    disqualified: bool


class Driver(BaseModel):
    Nascar_Driver_ID: int
    Driver_ID: int
    Driver_Series: str
    First_Name: str
    Last_Name: str
    Full_Name: str
    Series_Logo: str
    Short_Name: str
    Description: str
    DOB: str
    DOD: str
    Hometown_City: str
    Crew_Chief: str
    Hometown_State: str
    Hometown_Country: str
    Rookie_Year_Series_1: int
    Rookie_Year_Series_2: int
    Rookie_Year_Series_3: int
    Hobbies: str
    Children: str
    Twitter_Handle: str
    Residing_City: str
    Residing_State: str
    Residing_Country: str
    Badge: str
    Badge_Image: str
    Manufacturer: str
    Manufacturer_Small: str
    Team: str
    Image: str
    Image_Small: str
    Image_Transparent: str
    SecondaryImage: str
    Firesuit_Image: str
    Firesuit_Image_Small: str
    Career_Stats: str
    Driver_Page: str
    Age: int
    Rank: str
    Points: str
    Points_Behind: int
    No_Wins: str
    Poles: str
    Top5: str
    Top10: str
    Laps_Led: str
    Stage_Wins: str
    Playoff_Points: str
    Playoff_Rank: str
    Integrated_Sponsor_Name: str
    Integrated_Sponsor: str
    Integrated_Sponsor_URL: str
    Silly_Season_Change: str
    Silly_Season_Change_Description: str