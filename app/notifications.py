import os
import sys

from azure.cosmos import CosmosClient
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

key = os.getenv("PRIMARY_KEY")
connection_string = f"AccountEndpoint=https://nascar-picks-cosmosdb-account.documents.azure.com:443/;AccountKey={key}"

twilio_client = Client()

# Initialize the Cosmos client
cosmos_client = CosmosClient.from_connection_string(connection_string)

# Specify the database and container you want to work with
database_name = 'nascar-database'
container_name = 'nascar-collection'

# Access the database and container
database = cosmos_client.get_database_client(database_name)
container = database.get_container_client(container_name)

query = "SELECT * FROM c WHERE c['value'].type = @value"
parameters = [
    {"name": "@value", "value": "player"}
]

# Execute the query
players_raw = list(container.query_items(
    query=query,
    parameters=parameters,
    enable_cross_partition_query=True
))
players = [Player(**item['value']) for item in players_raw]

next_race = get_full_race_schedule_model(one_week_in_future_only=True)[-1]

for player in players:
    if player.text_notifications:
        print(player.phone_number)
        message = f"NASCAR Picks League! Make your picks for the {next_race.race_name} at {next_race.track_name}: https://nascar-frontend-demo.lemonbush-6bcc1f8d.eastus.azurecontainerapps.io/picks/{next_race.race_id}/?player_id={player.hash}"
        print(message)
        message = twilio_client.messages.create(
          from_='+18335431795',
          body=message,
          to=f'+1{player.phone_number}'
        )
        print(message.sid)





