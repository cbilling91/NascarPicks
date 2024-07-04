import requests
from datetime import datetime, timedelta
from typing import Generator, ClassVar, Type
import json
from functools import wraps
import hashlib
import base64

from pydantic import BaseModel, Field
from fastapi import Cookie, Response, HTTPException, Depends
from dapr.clients import DaprClient
from fastui.forms import SelectSearchResponse
from cachetools import TTLCache

from app.models.nascar import ScheduleItem, Driver, DriverPoints, WeekendFeed, Player, LapTimes, StagePoints, PlayerPicks, PicksItem, PickPoints

dapr_client = DaprClient()
STATE_STORE = 'nascar-db'


def cache_with_ttl(ttl_seconds):
    cache = TTLCache(maxsize=100, ttl=ttl_seconds)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key using the function name and arguments
            key = (func.__name__, args, frozenset(kwargs.items()))
            # Check if the result is already in the cache
            if key in cache:
                return cache[key]
            # If not, compute the result
            result = func(*args, **kwargs)
            # Cache the result with the specified expiration time
            cache[key] = result
            return result
        return wrapper
    return decorator


def generate_pydantic_class(fields: Generator[tuple, None, None]) -> Type[BaseModel]:
    class_dict = {}
    for name, type_hint, search_url_variable in fields:
        if type_hint is ClassVar:
            class_dict[name] = ClassVar
        else:
            json_schema_extra = {
                'search_url': f'/api/drivers/{search_url_variable}'}
            field = Field(
                title=name, description=f'{name} desc', json_schema_extra=json_schema_extra)
            class_dict[name] = (type_hint, field)
    return type("GeneratedPydanticClass", (BaseModel,), class_dict)


@cache_with_ttl(ttl_seconds=3600)
def load_json(url):
    json_response = requests.get(url)
    return json_response.json()


@cache_with_ttl(ttl_seconds=10)
def load_json_10sec(url):
    json_response = requests.get(url)
    return json_response.json()


@cache_with_ttl(ttl_seconds=86400)
def get_full_schedule():
    # Get the NASCAR schedule feed
    schedule_url = "https://cf.nascar.com/cacher/2024/1/schedule-feed.json"
    schedule_response = requests.get(schedule_url)
    schedule_data = schedule_response.json()
    return schedule_data


def get_full_race_schedule_model(id=None, one_week_in_future_only=None):
    full_schedule = get_full_schedule()
    current_date = datetime.now()
    full_schedule_sorted = sorted(
        full_schedule, key=lambda x: x['start_time_utc'])
    filtered_schedule = {
        item['race_id']: ScheduleItem(**item) for item in full_schedule_sorted if (
            'Race' in item['event_name']
            and
            (id == None or item['race_id'] == id)
            and
            (not one_week_in_future_only or datetime.strptime(
                item["start_time_utc"], "%Y-%m-%dT%H:%M:%S") < current_date + timedelta(days=7))
        )
    }
    filtered_schedule = list(filtered_schedule.values())
    if id:
        return filtered_schedule[0]
    return filtered_schedule


def get_current_weekend_schedule():
    # Get the NASCAR schedule feed
    schedule_data = get_full_schedule()

    # Find the race for this weekend
    current_date = datetime.now()
    # current_date = datetime.strptime("2024-11-03T15:05:00", "%Y-%m-%dT%H:%M:%S")
    current_weekend_race = None

    for race in schedule_data:
        if race['event_name'] == 'Race':
            race_date = datetime.strptime(
                race["start_time_utc"], "%Y-%m-%dT%H:%M:%S")
            if current_date <= race_date <= current_date + timedelta(days=6):
                current_weekend_race = race
                break

    return current_weekend_race


def get_weekend_feed(race_id):
    # Get the weekend feed for the specified race
    weekend_feed_response = load_json(
        f"https://cf.nascar.com/cacher/2024/1/{race_id}/weekend-feed.json")
    weekend_feed_model = WeekendFeed(**weekend_feed_response)
    adding_position = []
    position = 1
    for result in weekend_feed_model.weekend_race[0].results:
        result.position = position
        adding_position.append(result)
        position += 1
    weekend_feed_model.weekend_race[0].results = adding_position
    return weekend_feed_model


def get_qualified_drivers(race_id):
    weekend_feed = get_weekend_feed(race_id)
    for run in weekend_feed.weekend_runs:
        if run.run_type == 2:
            return run.results


def get_results(race_id):
    weekend_feed = get_weekend_feed(race_id)
    return weekend_feed.weekend_race[0].results
    for result in weekend_feed.weekend_race.results:
        if run['run_type'] == 2:
            drivers_models = [Driver(**item) for item in run['results']]
    return drivers_models


def get_driver_position(race_id) -> LapTimes:
    try:
        positions = load_json_10sec(
            f"https://cf.nascar.com/cacher/2024/1/{race_id}/lap-times.json")
        positions_model = LapTimes(**positions)
        return positions_model
    except:
        return LapTimes(laps=[], flags=[])


def get_driver_stage_points(race_id) -> StagePoints:
    try:
        stage_points = load_json_10sec(
            f"https://cf.nascar.com/cacher/2024/1/{race_id}/live-stage-points.json")
        stage_points_model = StagePoints(stage_points)
        return stage_points_model
    except:
        return StagePoints(root=[])


def get_race_drivers_search_model(race_id) -> SelectSearchResponse:
    drivers = get_qualified_drivers(race_id)
    all_drivers = [{'label': driver.driver_name, 'value': str(
        driver.driver_id)} for driver in drivers]
    all_drivers_options = [
        {
            'label': 'Drivers',
            'options': all_drivers
        }
    ]
    return SelectSearchResponse(options=all_drivers_options)


def get_drivers(series=None, id=None, query=None) -> list[Driver]:
    drivers = load_json("https://cf.nascar.com/cacher/drivers.json")
    drivers_models = [Driver(**item) for item in drivers['response'] if (series == None or item['Driver_Series'] == series) and (
        id == None or item['Nascar_Driver_ID'] == int(id)) and item['Crew_Chief'] and (not query or query.lower() in item['Full_Name'].lower())]
    drivers_models = sorted(drivers_models, key=lambda x: x.Full_Name)
    return drivers_models


def get_all_cup_drivers_pick_options(query: str = None) -> SelectSearchResponse:
    drivers = get_drivers(series='nascar-cup-series', query=query)
    all_drivers = [{'label': driver.Full_Name, 'value': str(
        driver.Nascar_Driver_ID)} for driver in drivers]
    all_drivers_options = [
        {
            'label': 'Drivers',
            'options': all_drivers
        }
    ]
    return SelectSearchResponse(options=all_drivers_options)


def get_drivers_list(race_weekend_feed):
    # Create a list of drivers with their car number and image URL
    drivers_list = []

    for driver in race_weekend_feed["weekend_race"][0]["results"]:
        car_number = driver["car_number"]
        driver_url = f"https://cf.nascar.com/data/images/carbadges/1/{car_number}.png"
        drivers_list.append(
            {"driver_name": driver["driver_fullname"], "car_number": car_number, "image_url": driver_url})

    return drivers_list


def publish_driver_picks(player_id, race_id, picks):

    if picks.player_select:
        key = f'picks-{picks.player_select}-{race_id}'
        picking_player = picks.player_select
    else:
        key = f'picks-{player_id}-{race_id}'
        picking_player = player_id
    payload = {
        'player': picking_player,
        'race': race_id,
        'picks': picks.search_select_multiple,
        'type': 'picks'
    }
    dapr_client.save_state(STATE_STORE, key, value=json.dumps(payload), state_metadata={
        'contentType': 'application/json'
    })
    return


def get_driver_picks(race_id, player_id=None) -> PlayerPicks:

    query = {
        "filter": {
            "AND": [
                {
                    "EQ": {"race": str(race_id)},
                },
                {
                    "EQ": {"type": "picks"}
                }
            ]
        }
    }
    if player_id:
        query['filter']['AND'].append(
            {
                "EQ": {"player": f'{player_id}'}
            }
        )
    race_picks = dapr_client.query_state(
        store_name=STATE_STORE, query=json.dumps(query)
    )
    race_picks_list = [{key: [get_drivers(id=pick)[0] for pick in value] if key ==
                        'picks' else value for key, value in item.json().items()} for item in race_picks.results]
    race_picks_model = PlayerPicks(race_picks_list)
    return race_picks_model

##
## TODO: Looping through full lists too much
##
def get_driver_points(race_id, active_standings=True):

    race_picks = get_driver_picks(race_id)
    full_schedule = get_full_race_schedule_model()
    current_race = get_full_race_schedule_model(id=race_id)
    points_race_begin = False
    previous_race_picks = PlayerPicks(root=[])
    if current_race.event_name == 'Race':
        for race_index in range(len(full_schedule)):
            if full_schedule[race_index].race_name == "DAYTONA 500":
                points_race_begin = True
                continue
            if full_schedule[race_index].race_id == race_id and race_index > 0 and points_race_begin:
                race_type = ""
                index_lookback = 0
                while race_type != 'Race':
                    index_lookback += 1
                    previous_points_race = full_schedule[race_index-index_lookback]
                    race_type = previous_points_race.event_name
                previous_race_picks = get_driver_picks(
                    previous_points_race.race_id)

    results = get_driver_position(race_id)
    all_driver_stage_points = get_driver_stage_points(race_id)
    players_points = []
    for player_picks in race_picks:
        # player_picks_dict = player_picks.json()
        player_points = calculate_points(
            results, player_picks, all_driver_stage_points, previous_race_picks)
        players_points.append(player_points)
    players_points = sorted(
        players_points, key=lambda x: getattr(x, 'total_points'), reverse=True)
    return players_points

##
## TODO: This function is way too big. It should be broken up
##
def calculate_points(results: LapTimes, player_picks: PicksItem, all_driver_stage_points: StagePoints, previous_race_picks: PlayerPicks) -> DriverPoints:
    repeated_picks = []
    penalty = False
    for previous_pick in previous_race_picks:
        if previous_pick.player == player_picks.player:
            repeated_picks = [
                previous
                for previous in previous_pick.picks
                for current in player_picks.picks
                if previous.model_dump() == current.model_dump()
            ]
    points = 0
    stage_points = 0
    picks_data = [PickPoints(), PickPoints(), PickPoints()]
    if results.laps or results.flags:
        for index, pick in enumerate(player_picks.picks):
            if pick in repeated_picks:
                picks_data[index].repeated_pick = True
            picks_data[index].name = pick.Full_Name
            position_points = 40
            reduction = 5
            for result in results.laps:
                if pick.Nascar_Driver_ID == result.NASCARDriverID:
                    points += position_points
                    picks_data[index].position_points = position_points
                    break
                position_points -= reduction
                if position_points < 0:
                    position_points = 0
                reduction = 1
            picks_data[index].stage_points = 0
            if all_driver_stage_points.root:
                for stage in all_driver_stage_points:
                    for driver_position in stage.results:
                        if pick.Nascar_Driver_ID == driver_position.driver_id:
                            points += driver_position.stage_points
                            if driver_position.stage_points == 10:
                                picks_data[index].stage_wins += 1
                            stage_points += driver_position.stage_points
                            picks_data[index].stage_points += driver_position.stage_points
                            break
    return DriverPoints(name=get_player(player_id=player_picks.player).name, picks=picks_data)

def publish_user(form):
    key = f'player-{form.name.replace(" ", "-").lower()}-{form.phone_number}'

    # Use a secure hash function like SHA-256
    hash_object = hashlib.sha256(key.encode())
    # Get the hash value as bytes
    hash_bytes = hash_object.digest()
    # Encode the bytes using base64
    encoded_hash = base64.urlsafe_b64encode(hash_bytes).decode('utf-8')

    payload = {
        'id': key,
        'name': form.name,
        'phone_number': form.phone_number,
        'hash': encoded_hash,
        'type': 'player',
        'text_notifications': form.text_notifications,
        'admin': form.admin
    }
    print(payload)
    dapr_client.save_state(STATE_STORE, key, value=json.dumps(payload), state_metadata={
        'contentType': 'application/json'
    })
    return


def get_player_interface(response: Response, player_id: str = None, player_id_cookie=Cookie(None)):
    if player_id:
        response.set_cookie(key="player_id_cookie",
                            value=player_id, max_age=259200, httponly=True)
    elif player_id_cookie:
        player_id = player_id_cookie
    else:
        raise HTTPException(status_code=401, detail="Cannot identify you.")
    return get_player(player_hash=player_id)


def check_admin_user(admin: Player = Depends(get_player_interface)):
    if admin.admin:
        return admin
    else:
        raise HTTPException(status_code=401, detail="Only admins can do this.")


@cache_with_ttl(ttl_seconds=60)
def get_player(player_hash=None, player_id=None):
    if player_hash:
        player_query = {
            "filter": {
                "EQ": {"hash": player_hash}
            }
        }
        player = dapr_client.query_state(
            store_name=STATE_STORE, query=json.dumps(player_query))
        if len(player.results) == 0:
            raise HTTPException(
                status_code=401, detail="Your user is not found in the database.")
        player = player.results[0]
    else:
        player = dapr_client.get_state(store_name=STATE_STORE, key=player_id)
        # test=player.json()
    if hasattr(player, "json"):
        return Player(**player.json())
    else:
        return Player(name='Unknown', phone_number='9999999999', id="1234567890", hash="1234567890", type="player")


# @cache_with_ttl(ttl_seconds=60)
def get_players(id: str = None):
    if id:
        player = dapr_client.get_state(
            store_name=STATE_STORE, key=id
        )
        return Player(**player.json())
    player_query = {
        "filter": {
            "EQ": {"type": "player"}
        }
    }
    players = dapr_client.query_state(
        store_name=STATE_STORE, query=json.dumps(player_query)
    )
    return [Player(**item.json()) for item in players.results]


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
            print(
                f"Driver: {driver['driver_name']}, Car Number: {driver['car_number']}, Image URL: {driver['image_url']}")
    else:
        print("No race scheduled for this weekend.")
