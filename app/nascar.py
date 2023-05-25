import requests
from datetime import date

class NascarApiClient:
    def __init__(self):
        self.base_url = "https://api.sportradar.us/nascar-ot3/mc/"
        self.api_key = self.get_api_key()
        current_date = date.today()
        self.today = current_date.strftime("%Y-%m-%d")
        self.today = "2023-05-28"
        self.year = "2023"

    def get_api_key(self):
        with open("/mnt/api_key") as f:
            return f.read().strip()

    def make_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}?api_key={self.api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Request failed with status code {response.status_code}")
            return None

    def get_schedule(self, id=None, current=None, races=None, race_id=None):
        endpoint = self.year+"/races/schedule.json"
        schedule = self.make_request(endpoint)

        if id or current:
            for event in schedule['events']:
                if event['id'] == id or (current and event['start_date'] == self.today):
                    if races:
                        if race_id:
                            for race in event['races']:
                                if race['id'] == race_id:
                                    return race
                        else:
                            return event['races']
                    else:
                        return event
        else:
            return schedule

    def get_points(self, race_id=None):

        endpoint = f"races/{race_id}/results.json"
        points = self.make_request(endpoint)

        if points.status_code == 200:
            return points.json()
        else:
            print(f"Request failed with status code {points.status_code}")
            return None

    def get_driver_points(self, race_id):
        endpoint = f"races/{race_id}/results.json"
        points = self.make_request(endpoint)

        formatted_points = {}

        for driver in points["results"]:

            formatted_points[driver['driver']['full_name']] = driver

        return formatted_points

    def calculate_user_points(self, race_id, user_picks):
        driver_points = self.get_driver_points(race_id)
        #print (driver_points)
        #return driver_points

        if driver_points is None:
            return None

        user_points = {}
        for user, drivers in user_picks.items():
            total_points = 0
            for driver in drivers:
                if driver in driver_points:
                    total_points += driver_points[driver]["points"] + driver_points[driver]["bonus_points"]
            user_points[user] = total_points

        return user_points


    # def current_event(self, endpoint):
    #     url = f"{self.base_url}/{endpoint}?api_key={self.api_key}"
    #     response = requests.get(url)
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         print(f"Request failed with status code {response.status_code}")
    #         return None

    # def get_race_results(self):
    #     endpoint = "race_results"
    #     return self.make_request(endpoint)

    # def get_driver_standings(self):
    #     endpoint = "driver_standings"
    #     return self.make_request(endpoint)