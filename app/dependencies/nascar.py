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
STATE_STORE = 'nascar-cockroach-statestore'

# Get the current year for NASCAR data
current_year = datetime.now().year

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


def load_json_with_ttl(url, ttl_seconds):
    @cache_with_ttl(ttl_seconds=ttl_seconds)
    def fetch_json():
        json_response = requests.get(url)
        if json_response.status_code != 200:
            return None
        return json_response.json()
    return fetch_json()


@cache_with_ttl(ttl_seconds=86400)
def get_full_schedule():
    schedule_url = f"https://cf.nascar.com/cacher/{current_year}/1/schedule-feed.json"
    return load_json_with_ttl(schedule_url, 86400)


def get_full_race_schedule_model(id=None, one_week_in_future_only=None, text_notifications_only=None):
    full_schedule = get_full_schedule()
    current_date = datetime.now()
    full_schedule_sorted = sorted(
        full_schedule, key=lambda x: x['start_time_utc'])
    # Find the first race event
    first_race = next((item for item in full_schedule_sorted if 'Race' in item['event_name'] and not 'Heat' in item['event_name']), None)
    
    filtered_schedule = {}
    if first_race and not text_notifications_only:
        filtered_schedule[first_race['race_id']] = ScheduleItem(**first_race)
    
    # Add other races within the time window
    for item in full_schedule_sorted:
        if item['race_id'] == id:
            return ScheduleItem(**item)
        if (item['race_id'] != first_race['race_id'] and  # Skip the first race since we already added it
            'Race' in item['event_name'] and not 'Heat' in item['event_name'] and
            (not one_week_in_future_only or 
             (datetime.strptime(item["start_time_utc"], "%Y-%m-%dT%H:%M:%S") < current_date + timedelta(days=5) and 
              (not text_notifications_only or datetime.strptime(item["start_time_utc"], "%Y-%m-%dT%H:%M:%S") >= current_date)))):
            filtered_schedule[item['race_id']] = ScheduleItem(**item)
    filtered_schedule = list(filtered_schedule.values())
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
    try:
        weekend_feed_response = load_json_with_ttl(
            f"https://cf.nascar.com/cacher/{current_year}/1/{race_id}/weekend-feed.json", 3600)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Access denied for race ID {race_id}. The race information may not be available yet.")
            return WeekendFeed(weekend_race=[], weekend_runs=[])
        raise  # Re-raise other HTTP errors

    try:
        weekend_feed_model = WeekendFeed(**weekend_feed_response)
        
        if weekend_feed_model.weekend_race:
            for position, result in enumerate(weekend_feed_model.weekend_race[0].results, start=1):
                result.position = position
        
        return weekend_feed_model
    except (ValueError, TypeError, KeyError):
        # Return empty model if the response is invalid
        return WeekendFeed(weekend_race=[], weekend_runs=[])


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
        positions = load_json_with_ttl(
            f"https://cf.nascar.com/cacher/{current_year}/1/{race_id}/lap-times.json", 10)
        positions_model = LapTimes(**positions)
        return positions_model
    except:
        return LapTimes(laps=[], flags=[])


def race_started(race_id):
    laps_and_flags = get_driver_position(race_id=race_id)
    for flag in laps_and_flags.flags:
        if flag.FlagState == 1:
            return True
    return False


def get_driver_stage_points(race_id) -> StagePoints:
    stage_points = load_json_with_ttl(
        f"https://cf.nascar.com/cacher/{current_year}/1/{race_id}/live-stage-points.json", 10)
    if stage_points is None:
        return StagePoints(root=[])
    return StagePoints(root=stage_points)


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
    drivers = load_json_with_ttl("https://cf.nascar.com/cacher/drivers.json", 3600)
    #  or item['Driver_Series'] == series
    drivers_models = [Driver(**item) for item in drivers['response'] if (series == None or True) and (
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

    pick_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    payload = {
        'player': picking_player,
        'race': race_id,
        'picks': picks.search_select_multiple,
        'type': 'picks',
        'pick_time': pick_time
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
## TODO: Looping through full lists repeatedly is bad!
##
def is_playoff_race(weekend_feed):
    if weekend_feed.weekend_race and len(weekend_feed.weekend_race) > 0:
        return weekend_feed.weekend_race[0].playoff_round
    return False


def has_race_started(results):
    for flag in results.flags:
        if flag.FlagState == 1:
            return True
    return False


def assign_playoff_points(players_points, points_dict):
    last_pick_1 = last_pick_2 = last_pick_3 = 0
    first = True
    points_position = position_scores = 0

    for player_points in players_points:
        if position_scores < 3 or points_position < 3:
            position_scores += 1
            if (last_pick_1 != player_points.pick_1 or last_pick_2 != player_points.pick_2 or last_pick_3 != player_points.pick_3) and not first:
                points_position += 1
            first = False

            player_points.total_playoff_points += points_dict[points_position]

            last_pick_1 = player_points.pick_1
            last_pick_2 = player_points.pick_2
            last_pick_3 = player_points.pick_3


def calculate_position_points(results, pick):
    position_points = 40
    reduction = 5
    for result in results.laps:
        if pick.Nascar_Driver_ID == result.NASCARDriverID:
            return position_points
        position_points -= reduction
        if position_points < 1:
            position_points = 1
        reduction = 1
    return position_points


def calculate_stage_points(all_driver_stage_points, pick):
    stage_points = 0
    if all_driver_stage_points.root:
        for stage in all_driver_stage_points:
            for driver_position in stage.results:
                if pick.Nascar_Driver_ID == driver_position.driver_id:
                    if driver_position.position == 1:
                        pick.stage_wins += 1
                    if driver_position.position <= 10:
                        stage_points += (11 - driver_position.position)
                        pick.stage_points += (11 - driver_position.position)
                    break
    return stage_points


def calculate_points(results: LapTimes, player_name: str, player_picks: PicksItem, all_driver_stage_points: StagePoints, previous_race_picks: PlayerPicks, playoff_race: bool) -> DriverPoints:
    repeated_picks = [
        previous
        for previous_pick in previous_race_picks
        if previous_pick.player == player_picks.player
        for previous in previous_pick.picks
        for current in player_picks.picks
        if previous.model_dump() == current.model_dump()
    ]

    points = 0
    picks_data = [PickPoints(), PickPoints(), PickPoints()]

    if results.laps or results.flags:
        for index, pick in enumerate(player_picks.picks):
            if pick in repeated_picks:
                picks_data[index].repeated_pick = True
            picks_data[index].name = pick.Full_Name
            picks_data[index].position_points = calculate_position_points(results, pick)
            points += picks_data[index].position_points
            picks_data[index].stage_points = calculate_stage_points(all_driver_stage_points, picks_data[index])
            points += picks_data[index].stage_points

    return DriverPoints(name=player_name, pick_time=player_picks.pick_time, playoff_race=playoff_race, picks=picks_data)


def get_driver_points(race_id):
    race_picks = get_driver_picks(race_id)
    full_schedule = get_full_race_schedule_model()
    current_race = get_full_race_schedule_model(id=race_id)
    weekend_feed = get_weekend_feed(race_id)
    playoff_race = is_playoff_race(weekend_feed)

    previous_race_picks = PlayerPicks(root=[])
    if current_race.event_name == 'Race':
        points_race_begin = False
        for race_index in range(len(full_schedule)):
            if full_schedule[race_index].race_name == "DAYTONA 500":
                points_race_begin = True
                continue
            if full_schedule[race_index].race_id == race_id and race_index > 0 and points_race_begin:
                previous_race_picks = get_driver_picks(full_schedule[race_index-1].race_id)

    results = get_driver_position(race_id)
    race_started = has_race_started(results)
    all_driver_stage_points = get_driver_stage_points(race_id)

    players_points = [
        calculate_points(results, get_player(player_id=player_picks.player).name, player_picks, all_driver_stage_points, previous_race_picks, playoff_race)
        for player_picks in race_picks
    ]

    players_points.sort(key=lambda x: getattr(x, 'total_points'), reverse=True)

    if race_started:
        assign_playoff_points(players_points, [10, 5, 3, 0, 0, 0])

    return players_points


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


def delete_player(player_id: str):
    """Delete a player from the state store."""
    try:
        # Delete the player from the state store
        delete_response = dapr_client.delete_state(
            store_name=STATE_STORE,
            key=player_id
        )
        return True
    except Exception as e:
        print(f"Error deleting player: {e}")
        return False


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
