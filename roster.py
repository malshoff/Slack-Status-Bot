import json
import requests
import datetime
from requests.auth import HTTPBasicAuth
from slacker import Slacker 
from pymongo import MongoClient
import os


class Roster(object):
    def __init__(self,passwordFile):
        self.EAST_COAST_ENGINEER_IDS = set()
        self.EMPLOYEES= {}
        self.UNAVAILABLE = {9,10,12,13,14,15,16}
        self.EAST_COAST_TIMEZONES = {8,9}
        self.TODAYS_DATE = datetime.date.today()
        self.TRAINING_CODES = {11}

        with open(str(passwordFile), 'r') as creds:
            self.credentials = json.loads(creds.read())
        self.updateEmployees()

    def updateEmployees(self):
        r = requests.get('https://pivotal-roster-api.cfapps.io/api/employees/employee/', auth=(
            self.credentials['user'], 
            self.credentials['pass'])
            )
        for person in r.json():
            if person['timezone'] in self.EAST_COAST_TIMEZONES:
                self.EAST_COAST_ENGINEER_IDS.add(person['id'])
                self.EMPLOYEES[person['id']] = {
                                                'first_name': person['first_name'],
                                                'last_name': person['last_name'],
                                                'email': person['email']
                                                }
    def getOutOfQueue(self):
        r = requests.get('https://pivotal-roster-api.cfapps.io/api/schedule/employee_schedule?audit_date='+str(self.TODAYS_DATE), auth=(self.credentials['user'], self.credentials['pass']))
        engs = r.json()
        res = []
        for eng in engs:
            if eng['engineer'] in self.EAST_COAST_ENGINEER_IDS and eng['availability'] in self.TRAINING_CODES: #engineer is out of queue
                res.append(self.EMPLOYEES[eng['engineer']])
        return res









'''print(slack.usergroups.users.list('SCY2D900P'))''' #ID of usergroup
