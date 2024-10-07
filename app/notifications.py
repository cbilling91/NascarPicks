import os
import sys
import psycopg2

from dotenv import load_dotenv

load_dotenv()

# Get the directory of the current script
current_dir = os.path.dirname(os.path.realpath(__file__))
# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(parent_dir)

from twilio.rest import Client

from app.dependencies.nascar import (
    get_full_race_schedule_model
)
from app.models.nascar import Player

connection_string = os.getenv("CONNECTION_STRING")

twilio_client = Client()

next_race = get_full_race_schedule_model(one_week_in_future_only=True)[-1]

conn = psycopg2.connect(connection_string)

with conn.cursor() as cur:
    cur.execute("SELECT value FROM public.state WHERE key LIKE 'nascarpicks||player-%';")
    players = cur.fetchall()
    conn.commit()

    for player in players:
        player = player[0]
        if player['text_notifications']:
            print(player['phone_number'])
            message = f"NASCAR Picks League! Make your picks for the {next_race.race_name} at {next_race.track_name}: https://nascar-frontend-demo.lemonbush-6bcc1f8d.eastus.azurecontainerapps.io/picks/{next_race.race_id}/?player_id={player['hash']}\n\nWhen the race starts, watch the live points here: https://nascar-frontend-demo.lemonbush-6bcc1f8d.eastus.azurecontainerapps.io/races/{next_race.race_id}/?player_id={player['hash']}"
            print(message)
            if player['name'] == "Chase Billing":
                message = twilio_client.messages.create(
                    from_='+18335431795',
                    body=message,
                    to=f"+1{player['phone_number']}"
                )
                print(message.sid)





