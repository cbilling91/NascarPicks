from __future__ import annotations

from typing import List, Optional
from datetime import date

from pydantic import BaseModel, RootModel, EmailStr, Field, field_validator, constr
from pydantic_core import PydanticCustomError


class DriverSelectForm(BaseModel):
    search_select_multiple: list[str] = Field(title="Select 3 Drivers", description="drivers desc", json_schema_extra={'search_url': '/api/drivers/1'})
    #thing: str = Field(title="drivers", description="drivers desc", json_schema_extra={'search_url': '/api/drivers/1'})

    @field_validator("search_select_multiple")
    def validate_value(cls, search_select_multiple):
        # Custom validation logic goes here
        if len(search_select_multiple) != 3:
            raise PydanticCustomError("lower", "Must pick 3 drivers exactly")
        return search_select_multiple


class UserForm(BaseModel):
    # id: str
    # hash: str
    name: str
    phone_number: str

    @field_validator("phone_number")
    def validate_value(cls, phone_number):
        # Custom phone number validation logic
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise ValueError('Phone number must be a 10-digit number with no dashes')
        return phone_number


class Player(BaseModel):
    hash: str
    id: str
    name: str
    phone_number: str
    type: str


class PlayerList(RootModel):
    root: List[Player]


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
    picks: str = "Make Picks"
    race: str = "Race"


class DriverResult(BaseModel):
    result_id: int
    finishing_position: int
    starting_position: int
    car_number: str
    driver_fullname: str
    driver_id: int
    driver_hometown: str
    hometown_city: str
    hometown_state: str
    hometown_country: str
    team_id: int
    team_name: str
    qualifying_order: int
    qualifying_position: int
    qualifying_speed: int
    laps_led: int
    times_led: int
    car_make: str
    car_model: str
    sponsor: str
    points_earned: int
    playoff_points_earned: int
    laps_completed: int
    finishing_status: str
    winnings: int
    series_id: int
    race_season: int
    race_id: int
    owner_fullname: str
    crew_chief_id: int
    crew_chief_fullname: str
    points_position: int
    points_delta: int
    owner_id: int
    official_car_number: str
    disqualified: bool
    diff_laps: int
    diff_time: int


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


class RaceResult(BaseModel):
    result_id: int
    finishing_position: int
    starting_position: int
    car_number: str
    driver_fullname: str
    driver_id: int
    driver_hometown: str
    hometown_city: str
    hometown_state: str
    hometown_country: str
    team_id: int
    team_name: str
    qualifying_order: int
    qualifying_position: int
    qualifying_speed: int
    laps_led: int
    times_led: int
    car_make: str
    car_model: str
    sponsor: str
    points_earned: int
    playoff_points_earned: int
    laps_completed: int
    finishing_status: str
    winnings: int
    series_id: int
    race_season: int
    race_id: int
    owner_fullname: str
    crew_chief_id: int
    crew_chief_fullname: str
    points_position: int
    points_delta: int
    owner_id: int
    official_car_number: str
    disqualified: bool
    diff_laps: int
    diff_time: int
    position: int = -1
    

class CautionSegment(BaseModel):
    race_id: int
    start_lap: int
    end_lap: int
    reason: str
    comment: str
    beneficiary_car_number: Optional[str]
    flag_state: int


class RaceLeader(BaseModel):
    start_lap: int
    end_lap: int
    car_number: str
    race_id: int


class RaceScheduleItem(BaseModel):
    event_name: str
    notes: str
    start_time_utc: str
    run_type: int


class WeekendRaceItem(BaseModel):
    race_id: int
    series_id: int
    race_season: int
    race_name: str
    race_type_id: int
    restrictor_plate: bool
    track_id: int
    track_name: str
    date_scheduled: str
    race_date: str
    qualifying_date: str
    tunein_date: str
    scheduled_distance: float
    actual_distance: float
    scheduled_laps: int
    actual_laps: int
    stage_1_laps: int
    stage_2_laps: int
    stage_3_laps: int
    stage_4_laps: int
    number_of_cars_in_field: int
    pole_winner_driver_id: int
    pole_winner_speed: int
    number_of_lead_changes: int
    number_of_leaders: int
    number_of_cautions: int
    number_of_caution_laps: int
    average_speed: float
    total_race_time: str
    margin_of_victory: str
    race_purse: int
    race_comments: str
    attendance: int
    results: List[RaceResult]
    caution_segments: List[CautionSegment]
    race_leaders: List[RaceLeader]
    infractions: List
    schedule: List[RaceScheduleItem]
    stage_results: List
    pit_reports: List
    radio_broadcaster: str
    television_broadcaster: str
    satellite_radio_broadcaster: str
    master_race_id: int
    inspection_complete: bool
    playoff_round: int


class RunResult(BaseModel):
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


class WeekendRun(BaseModel):
    weekend_run_id: int
    race_id: int
    timing_run_id: int
    run_type: int
    run_name: str
    run_date: str
    run_date_utc: str
    results: List[RunResult]


class WeekendFeed(BaseModel):
    weekend_race: List[WeekendRaceItem]
    weekend_runs: List[WeekendRun]


class DriverPoints(BaseModel):
    name: str
    pick_1: str
    pick_2: str
    pick_3: str
    points: int


class Lap(BaseModel):
    Lap: int
    LapTime: Optional[float]
    LapSpeed: Optional[str]
    RunningPos: int


class Position(BaseModel):
    Number: str
    FullName: str
    Manufacturer: str
    RunningPos: int
    NASCARDriverID: int
    Laps: List[Lap]


class Flag(BaseModel):
    LapsCompleted: int
    FlagState: int


class LapTimes(BaseModel):
    laps: List[Position]
    flags: List[Flag]
