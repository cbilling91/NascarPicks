import os
import json

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.dependencies.nascar import get_current_weekend_schedule, get_weekend_feed, get_drivers_list, get_drivers, calculate_points, get_driver_points
from app.models.nascar import Driver, Result, Position, LapTimes, PicksItem, StagePoints, PlayerPicks, PickPoints, DriverPoints
from tests import fixtures, utils

test_file = "app.dependencies.nascar"

# Example: Load a JSON file into a variable
def load_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

@pytest.fixture
def mock_requests_get(monkeypatch):
    with patch(test_file+'.requests.get') as mock_get:
        yield mock_get

@patch(test_file+".load_json")
def test_get_weekend_feed(mock_load_json):
    mock_load_json.return_value = fixtures.results
    race_weekend_feed = get_weekend_feed("race1")
    assert race_weekend_feed == fixtures.results_model

def test_get_drivers_list():
    race_weekend_feed = {
        "weekend_race": [
        {
            "results": [
                {
                    "car_number": "1",
                    "driver_fullname": "Driver 1",
                    "driver_id": 4001,
                    "official_car_number": "1",
                }
            ]
        }
        ]
    }
    drivers_list = get_drivers_list(race_weekend_feed)
    assert drivers_list == [{"driver_name": "Driver 1", "car_number": "1", "image_url": "https://cf.nascar.com/data/images/carbadges/1/1.png"}]

@patch(test_file+".load_json")
def test_get_drivers_with_series(mock_load_json):
    # Mock the load_json function to return sample data
    mock_load_json.return_value = fixtures.drivers

    # Call the get_drivers function with series='Cup'
    result = get_drivers(series='Cup')

    # Assert that the function returns the expected list of Driver objects
    assert result == [Driver(**fixtures.drivers['response'][0])]

@patch(test_file+".load_json")
def test_get_drivers_with_id(mock_load_json):
    # Mock the load_json function to return sample data
    mock_load_json.return_value = fixtures.drivers

    # Call the get_drivers function with id=2
    result = get_drivers(id=2)

    # Assert that the function returns the expected list of Driver objects
    assert result == [Driver(**fixtures.drivers['response'][2])]

@patch(test_file+".load_json")
def test_get_drivers_without_filters(mock_load_json):
    # Mock the load_json function to return sample data
    mock_load_json.return_value = fixtures.drivers

    # Call the get_drivers function without any filters
    result = get_drivers()

    # Assert that the function returns all Driver objects in the sample data
    expected_result = [Driver(**item) for item in fixtures.drivers['response']]
    assert result == expected_result

def test_picks_models():
    pick_points_1 = PickPoints(
        name='pick 1',
        stage_points=5,
        position_points=10,
        total_points=15
    )
    pick_points_2 = PickPoints(
        name='pick 2',
        stage_points=10,
        stage_wins=1,
        position_points=4,
        total_points=14
    )
    pick_points_3 = PickPoints(
        name='pick 3',
        stage_points=0,
        position_points=35,
        total_points=35
    )
    pick_points_list = [pick_points_1, pick_points_2, pick_points_3]
    player_points = DriverPoints(
        name="player", picks=pick_points_list)
    
    player_model = DriverPoints(
        name="player",
        stage_points= 15,
        position_points= 49,
        total_points = 64,
        total_playoff_points=10,
        pick_1 = "pick 3",
        pick_1_repeated_pick = False,
        pick_1_stage_points = 0,
        pick_1_stage_wins = 0,
        pick_1_position_points = 35,
        pick_1_total_points = 35,
        pick_1_playoff_points = 9,
        pick_2 = "pick 1",
        pick_2_repeated_pick = False,
        pick_2_stage_points = 5,
        pick_2_stage_wins = 0,
        pick_2_position_points = 10,
        pick_2_total_points = 15,
        pick_2_playoff_points = 0,
        pick_3 = "pick 2",
        pick_3_repeated_pick = False,
        pick_3_stage_points = 10,
        pick_3_stage_wins = 1,
        pick_3_position_points = 4,
        pick_3_total_points = 14,
        pick_3_playoff_points = 1,
        penalty = False
    )
    assert player_model.model_dump() == player_points.model_dump()


def test_get_driver_points():

    results = LapTimes(**load_json_file("./variables/positions.json"))
    player_picks = PicksItem(**load_json_file("./variables/player_picks.json"))
    all_divers_stage_points = StagePoints(load_json_file("./variables/all_drivers_stage_points.json"))
    previous_race_picks = PlayerPicks(load_json_file("./variables/previous_race_picks.json"))

    calculated_points = calculate_points(results, player_picks, all_divers_stage_points, previous_race_picks)
    assert calculated_points.model_dump() == DriverPoints(
        name="Chase Billing",
        stage_points= 24,
        position_points= 49,
        total_points = 73,
        total_playoff_points=8,
        pick_1 = 'Christopher Bell',
        pick_1_repeated_pick = False,
        pick_1_stage_points = 0,
        pick_1_stage_wins = 0,
        pick_1_position_points = 33,
        pick_1_total_points = 33,
        pick_1_playoff_points = 7,
        pick_2 = 'Kyle Larson',
        pick_2_repeated_pick = True,
        pick_2_stage_points = 19,
        pick_2_stage_wins = 1,
        pick_2_position_points = 3,
        pick_2_total_points = 22,
        pick_2_playoff_points = 1,
        pick_3 = 'Denny Hamlin',
        pick_3_repeated_pick = False,
        pick_3_stage_points = 5,
        pick_3_stage_wins = 0,
        pick_3_position_points = 13,
        pick_3_total_points = 18,
        pick_3_playoff_points = 0,
        penalty = False
    ).model_dump()
