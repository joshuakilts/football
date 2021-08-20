import requests
import json
import pymongo
import sys
from time import sleep
sys.path.append("..")
from creds.get_key import get_ffpros_key


# api documentation here: https://api.fantasypros.com/public/v2/docs/#introduction
api_key = get_ffpros_key()


# players
positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']
url = 'https://api.fantasypros.com/public/v2/json/nfl/players'
headers = {'x-api-key': api_key}
response = requests.get(url, headers = headers)
sleep(1)
players = response.json()

with open('../data/fantasypros/players/players.json', 'w') as f:
    f.write(json.dumps(players))


# consensus rankings
for position in positions:
    url = 'https://api.fantasypros.com/public/v2/json/nfl/2021/consensus-rankings?experts=true&position={}'.format(position)
    headers = {'x-api-key': api_key}
    response = requests.get(url, headers = headers)
    sleep(1)
    consensus = response.json()
    
    with open('../data/fantasypros/consensus/{}.json'.format(position), 'w') as f:
        f.write(json.dumps(consensus))


# projections
for position in positions:
    url = 'https://api.fantasypros.com/public/v2/json/nfl/2021/projections?position={}'.format(position)
    headers = {'x-api-key': api_key}
    response = requests.get(url, headers = headers)
    sleep(1)
    projections = response.json()
    
    with open('../data/fantasypros/projections/{}.json'.format(position), 'w') as f:
        f.write(json.dumps(projections))