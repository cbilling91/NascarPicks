import os
import requests

# Define the URL and file path
url = 'https://cockroachlabs.cloud/clusters/e906cef2-48d5-4dbf-877c-48c20348cdc3/cert'
file_path = os.path.expanduser('~/.postgresql/root.crt')

# Create the directories if they don't exist
os.makedirs(os.path.dirname(file_path), exist_ok=True)

# Download the file and save it
response = requests.get(url)
with open(file_path, 'wb') as file:
    file.write(response.content)

print(f"Certificate downloaded and saved to {file_path}")
