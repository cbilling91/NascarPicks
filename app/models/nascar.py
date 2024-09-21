from __future__ import annotations
import pytz

from typing import List, Optional
from datetime import date, datetime

from pydantic import BaseModel, RootModel, EmailStr, Field, field_validator, root_validator
from pydantic_core import PydanticCustomError


class DriverSelectForm(BaseModel):
    player_select: str = None
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
    text_notifications: Optional[bool] = False # = Field(default=True)
    admin: bool = Field(default=False)

    @field_validator("phone_number")
    def validate_value(cls, phone_number):
        # Custom phone number validation logic
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise ValueError('Phone number must be a 10-digit number with no dashes')
        return phone_number


class Player(BaseModel):
    hash: str
    edit: str = "Edit"
    id: str
    name: str
    phone_number: str
    text_notifications: Optional[bool] = None
    type: str
    admin: bool


class Players(RootModel):
    root: List[Player]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class PlayerList(RootModel):
    root: List[Player]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


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
    start_time_utc: datetime
    start_time: str
    end_time_utc: date
    picks: str = "Make Picks"
    race: str = "Race"

    @root_validator(pre=True)
    def convert_to_edt(cls, values):
        start_time_utc = values.get('start_time_utc')
        
        start_time_utc = datetime.strptime(values.get('start_time_utc'), "%Y-%m-%dT%H:%M:%S")
        
        # Ensure the timestamp is in UTC
        if start_time_utc.tzinfo is None:
            utc_zone = pytz.utc
            start_time_utc = utc_zone.localize(start_time_utc)
        else:
            start_time_utc = start_time_utc.astimezone(pytz.utc)
        
        # Convert to Eastern Daylight Time (EDT)
        edt_zone = pytz.timezone('America/New_York')
        edt_timestamp = start_time_utc.astimezone(edt_zone)
        
        # Set both UTC and EDT timestamps in the values dictionary
        values['start_time_utc'] = start_time_utc
        values['start_time'] = edt_timestamp.strftime("%Y-%m-%d %I:%M:00 %p")
        
        return values


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
    Rank: int
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
    qualifying_speed: float
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
    pole_winner_speed: float
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
    picks: List[PickPoints] = []
    name: str = ""
    stage_points: int = 0
    position_points: int = 0
    total_points: int = 0
    total_playoff_points: int = 0
    pick_1: str = ""
    pick_1_repeated_pick: bool = False
    pick_1_stage_points: int = 0
    pick_1_stage_wins: int = 0
    pick_1_position_points: int = 0
    pick_1_total_points: int = 0
    pick_1_playoff_points: int = 0
    pick_2: str = ""
    pick_2_repeated_pick: bool = False
    pick_2_stage_points: int = 0
    pick_2_stage_wins: int = 0
    pick_2_position_points: int = 0
    pick_2_total_points: int = 0
    pick_2_playoff_points: int = 0
    pick_3: str = ""
    pick_3_repeated_pick: bool = False
    pick_3_stage_points: int = 0
    pick_3_stage_wins: int = 0
    pick_3_position_points: int = 0
    pick_3_total_points: int = 0
    pick_3_playoff_points: int = 0
    penalty: bool = False
    pick_time: Optional[datetime] = ""
    playoff_race: Optional[int] = 0

    @root_validator(pre=True)
    def flatten_items(cls, values):
        picks = values.get('picks', [])
        if picks:
            sorted_picks = sorted(picks, key=lambda x: x.stage_points + x.position_points)
            stage_points = 0
            position_points = 0
            repeated_picks = 0
            total_playoff_points = 0
            for index, item in enumerate(sorted_picks):
                reverse_index = len(sorted_picks) - index
                values[f'pick_{reverse_index}'] = item.name
                values[f'pick_{reverse_index}_repeated_pick'] = item.repeated_pick
                if item.repeated_pick:
                    repeated_picks += 1
                if repeated_picks < 2:
                    values[f'pick_{reverse_index}_stage_points'] = item.stage_points
                    values[f'pick_{reverse_index}_stage_wins'] = item.stage_wins
                    values[f'pick_{reverse_index}_position_points'] = item.position_points
                    playoff_points = 0
                    if item.position_points == 40:
                        playoff_points = 5
                    playoff_points += item.stage_wins
                    values[f'pick_{reverse_index}_playoff_points'] = playoff_points
                    values[f'pick_{reverse_index}_total_points'] = item.stage_points + item.position_points
                    stage_points += item.stage_points
                    position_points += item.position_points
                    total_playoff_points += playoff_points

            values['stage_points'] = stage_points
            values['position_points'] = position_points
            values['total_points'] = position_points + stage_points
            if not values['playoff_race']:
                values['total_playoff_points'] = total_playoff_points
            if repeated_picks > 1:
                values['penalty'] = True
            else:
                values['penalty'] = False
            values['picks'] = []
            if 'pick_time' in values:
                if not values['pick_time']:
                    del values['pick_time']
                else:
                    pick_time_utc = values['pick_time']
                    # Ensure the timestamp is in UTC
                    if pick_time_utc.tzinfo is None:
                        utc_zone = pytz.utc
                        pick_time_utc = utc_zone.localize(pick_time_utc)
                    else:
                        pick_time_utc = pick_time_utc.astimezone(pytz.utc)
                    
                        # Convert to Eastern Daylight Time (EDT)
                        edt_zone = pytz.timezone('America/New_York')
                        edt_timestamp = pick_time_utc.astimezone(edt_zone)
                        
                        # Set both UTC and EDT timestamps in the values dictionary
                        values['pick_time_utc'] = pick_time_utc
                        values['pick_time'] = edt_timestamp.strftime("%Y-%m-%d %I:%M:00 %p")
                    
        return values


class PickPoints(BaseModel):
    name: str = ""
    repeated_pick: bool = False
    stage_wins: int = 0
    stage_points: int = 0
    position_points: int = 0


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


class Result(BaseModel):
    position: int
    vehicle_number: str
    driver_id: int
    full_name: str
    stage_points: int


class StagePointsItem(BaseModel):
    race_id: int
    run_id: int
    stage_number: int
    results: List[Result]


class StagePoints(RootModel):
    root: List[StagePointsItem]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class PicksItem(BaseModel):
    type: str
    picks: List[Driver]
    player: str
    race: str
    pick_time: Optional[datetime] = ""


class PlayerPicks(RootModel):
    root: List[PicksItem]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]