import json
import requests
import datetime
from requests.auth import HTTPBasicAuth
from slacker import Slacker
from pymongo import MongoClient
from pymongo import UpdateOne
import os
from collections import defaultdict
from pytz import timezone

CONNECT_STRING = os.environ["CONNECT_STRING"]
client = MongoClient(f'{CONNECT_STRING}')
db = client.queue
out = db.ooq
timezones = db.timezones
employees = db.employees
TODAYS_DATE = datetime.datetime.now().replace(
            tzinfo=timezone('US/Eastern')).strftime("%m/%d/%Y")

class Roster():
    
    def __init__(self, passwordFile, tz):
        self.ENGINEER_IDS = set()  # ID's of engineers in given timezone
        self.EMPLOYEES = {}
        self.UNAVAILABLE = {9, 10,11, 12, 13, 14, 15, 16}
        self.TRAINING_CODES = {11}
        self.tz = tz
        with open(str(passwordFile), 'r') as creds:
            self.credentials = json.loads(creds.read())


    def getCategories(self):
        r = requests.get('http://pivotal-roster-api.cfapps.io/api/employees/tag/', auth=(
            self.credentials['user'],
            self.credentials['pass'])
        )
        with open("tags.txt", "w+") as f:
            json.dump(r.json(), f, indent=2)

    def getTimezones(self):

        print("Finding tz" + str(self.tz))
        ea = timezones.find_one({self.tz: {'$exists': True}})
        return set(ea[self.tz])

    def setEmployees(self):
        r = requests.get('https://pivotal-roster-api.cfapps.io/api/employees/employee/', auth=(
            self.credentials['user'],
            self.credentials['pass'])
        )
        tzPeople = []
        tzs = self.getTimezones()

        for person in r.json():
            if person['timezone'] in tzs:
                self.ENGINEER_IDS.add(person['id'])

            tzPeople.append({
                'tags': person['tags'],
                'employee_id': person['id'],
                'first_name': person['first_name'],
                'last_name': person['last_name'],
                'email': person['email'],
                'timezone': person['timezone'],
                'date': TODAYS_DATE
            })

        employees.bulk_write([
            UpdateOne(
                {'employee_id': p['employee_id']},
                {'$set': p},
                upsert=True
            )
            for p in tzPeople
        ])

    def setOutOfQueue(self):

        r = requests.get('https://pivotal-roster-api.cfapps.io/api/schedule/employee_schedule?active=true&audit_date=' +
                         str(TODAYS_DATE), auth=(self.credentials['user'], self.credentials['pass']))
        engs = r.json()
        #print(engs)
        res = []

        for eng in engs:
            # engineer is out of queue
            if eng['engineer'] in self.ENGINEER_IDS and eng['availability'] in self.TRAINING_CODES:
                res.append(employees.find_one(
                    {'employee_id': eng['engineer']}
                ))

        out.update(
            {'date': str(TODAYS_DATE)},
            {'$set': {'eng': res}},
            upsert=True
        )

    def getOutOfQueue():
        outToday = out.find_one({"date":str(TODAYS_DATE)})
        if outToday:
            return outToday['eng']
        return outToday


'''print(slack.usergroups.users.list('SCY2D900P'))'''  # ID of usergroup east-pcf-ce-team
