import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from app.dependencies.nascar import get_current_weekend_schedule, get_weekend_feed, get_drivers_list, get_drivers
from app.models.nascar import Driver
from tests import fixtures

test_file = "app.dependencies.nascar"

@pytest.fixture
def mock_requests_get(monkeypatch):
    with patch(test_file+'.requests.get') as mock_get:
        yield mock_get

def test_get_current_weekend_schedule(mock_requests_get):
    mock_response = mock_requests_get.return_value
    mock_response.json.return_value = [
        {"start_time": "2023-11-01T12:00:00", "event_name": "Race", "race_id": "race1"},
        {"start_time": "2023-11-08T12:00:00", "event_name": "Race", "race_id": "race2"},
        {"start_time": "2023-11-15T12:00:00", "event_name": "Race", "race_id": "race3"}
    ]
    
    # Set the current date to November 2, 2023, which falls between race2 and race3
    with patch(test_file+'.datetime') as mock_datetime:
        mock_datetime.now.side_effect = lambda: datetime(2023, 11, 15, 12, 0, 0)
        mock_datetime.strptime = datetime.strptime
        
        current_weekend_race = get_current_weekend_schedule()

    assert current_weekend_race == {"start_time": "2023-11-15T12:00:00", "event_name": "Race", "race_id": "race3"}

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
    assert result == [Driver(**fixtures.drivers['response'][1])]

@patch(test_file+".load_json")
def test_get_drivers_without_filters(mock_load_json):
    # Mock the load_json function to return sample data
    mock_load_json.return_value = fixtures.drivers

    # Call the get_drivers function without any filters
    result = get_drivers()

    # Assert that the function returns all Driver objects in the sample data
    expected_result = [Driver(**item) for item in fixtures.drivers['response']]
    assert result == expected_result
