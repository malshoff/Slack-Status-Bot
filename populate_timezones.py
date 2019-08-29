from pymongo import MongoClient
import os 
import json

#[{'id': 10, 'name': 'America/Boise'}, {'id': 12, 'name': 'America/Chicago'}, {'id': 11, 'name': 'America/Denver'},
#  {'id': 7, 'name': 'America/Los_Angeles'}, 
# {'id': 8, 'name': 'America/New_York'}, {'id': 9, 'name': 'America/Toronto'}, 
# {'id': 3, 'name': 'Asia/Calcutta'}, {'id': 13, 'name': 'Asia/Seoul'}, 
# {'id': 1, 'name': 'Asia/Shanghai'}, {'id': 2, 'name': 'Asia/Tokyo'}, 
# {'id': 4, 'name': 'Australia/Sydney'}, {'id': 5, 'name': 'Europe/Dublin'}, 
# {'id': 6, 'name': 'Europe/Madrid'}]

CONNECT_STRING = os.environ["CONNECT_STRING"]

client = MongoClient(f'{CONNECT_STRING}')
db = client.queue
timezones = db.timezones

EAST = [8,9]
APJ = [1,2,3,13]
WEST = [7]
EMEA = [4,5,6]

#east coast
timezones.insert_one({"EAST":EAST})
timezones.insert_one({'APJ':APJ})
timezones.insert_one({'WEST':WEST})
timezones.insert_one({'EMEA':EMEA})

ea = timezones.find_one({"EAST":{'$exists': True}})

print(set(ea['EAST']))
