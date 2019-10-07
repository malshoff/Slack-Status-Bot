from slacker import Slacker
from roster import Roster
from pymongo import MongoClient
from datetime import datetime
from datetime import timedelta
from time import mktime
import requests
import urllib.parse
import os
import roster 


class SlackBot(object):

    def __init__(self, tz="EAST"):
        self.roster = Roster("password.json", tz)
        self.inTraining = Roster.getOutOfQueue()  # list of training engineers
        self.BOT_TOKEN = os.environ['BOT_TOKEN']
        self.slackBotUser = Slacker(self.BOT_TOKEN)
        self.TRAINING_IDS = self.trainingIds()


    def refreshOOQ(self):
        self.inTraining = Roster.getOutOfQueue()
        self.TRAINING_IDS = self.trainingIds()
        
    # Return a set of Slack user IDs of CEs that are Out of Queue today
    def trainingIds(self):
        idset = set()

        if not self.inTraining:
            return idset

        for t in self.inTraining:

            if 'user_id' in t and t['user_id']:
                idset.add(t['user_id'])

        return idset

    # returns slack user ID and username of employee as a tuple
    def getUserByEmail(self, email):
        endpoint = 'https://slack.com/api/users.lookupByEmail'
        response = requests.post(
            endpoint, data={'token': self.BOT_TOKEN, 'email': email})
        return (response.json()['user']['id'], response.json()['user']['real_name'], response.json()['user']['name'])

    def getUserById(self, user_id):
        endpoint = 'https://slack.com/api/users.info'
        response = requests.post(
            endpoint, data={'token': self.BOT_TOKEN, 'user': user_id})
        return (response.json()['user']['id'], response.json()['user']['real_name'], response.json()['user']['name'])

    def buildURL(self, name):
        name = name.split()
        first_name = name[0]
        last_name = name[-1]
        if len(name) == 3:
            first_name += '+' + name[1]
       
        
        url = f'https://queue.apps.pcfone.io/?name={first_name}+{last_name}'
        return url

    def isInTraining(self, employee):
        if not self.inTraining:
            return False

        for eng in self.inTraining:
            if employee["first_name"] == eng["first_name"] and employee["last_name"] == eng["last_name"]:
                return True
        return False

    def setStatus(self, employee):
        if not employee:
            return "setStatus: employee was empty!"

        tomorrow = datetime.now() + timedelta(days=1)
        unix_date = mktime(tomorrow.timetuple())

        if 'user_id' in employee and employee['user_id']:
            if self.isInTraining(employee):
                self.slackBotUser.chat.post_message(channel=employee['user_id'],
                                                    text="Your status has been set for your OOQ day. Type `/status` clear your status.",
                                                    username='Out of Queue Bot',
                                                    link_names=1,
                                                    as_user=True
                                                    )
                slack = Slacker(employee['access_token'])
                slack.users.profile.set(user=employee['user_id'], name='status_text',
                                        value='Training')
                slack.users.profile.set(user=employee['user_id'], name='status_emoji',
                                        value=':thinkingman:')
                slack.users.profile.set(user=employee['user_id'], name='status_expiration',
                                        value=unix_date)
                slack.dnd.set_snooze(num_minutes=1440)
                self.slackBotUser.chat.post_message(channel='#ooq-test',
                                                    text=f'{employee["first_name"]} is Out of Queue Today!',
                                                    username='Out of Queue Bot'
                                                    )
                print("SUCCESS!!!!!!!!")

            else:
                self.slackBotUser.chat.post_message(channel=employee['user_id'],
                                                    text="You will be notified and have your status changed on your OOQ day!",
                                                    username='Out of Queue Bot',
                                                    link_names=1,
                                                    as_user=True
                                                    )

        else:
            userInfo = self.getUserByEmail(employee['email'])
            url = f'https://queue.apps.pcfone.io/?name={employee["first_name"]}+{employee["last_name"]}'
            self.sendInitMsg(url, userInfo[0])

    def sendInitMsg(self, url, user_id):
        msg = f'Hi! It looks like you have not yet authorized me to set your status to "training" yet. Please follow this url to do so:{url}'
        self.slackBotUser.chat.post_message(channel=user_id,
                                            text=msg,
                                            username='Out of Queue Bot',
                                            link_names=1,
                                            as_user=True
                                            )
        self.slackBotUser.chat.post_message(channel='UF57DA49F',
                                            text=f"Sent OOQ PM with url {url}",
                                            username='Out of Queue Bot',
                                            link_names=1,
                                            as_user=True
                                            )

    def msgOutOfQueue(self,user="ooq-test"):
        endstr = "The following CEs are out of queue on {}: ".format(
            roster.TODAYS_DATE)

        if not self.inTraining or len(self.inTraining) == 0:
            endstr += "No one today!"
        else:
            for eng in self.inTraining:
                endstr += eng["first_name"] + " " + eng["last_name"] + ","

        self.slackBotUser.chat.post_message(channel=user,
                                            text=endstr,
                                            username='Out of Queue Bot',
                                            link_names=1
                                            )

    def msgAllStaff(self):
        self.msgPAAS()
        self.msgData()

    def msgPAAS(self):
        PAAS_TAGS = {39,40,41}  # Tags for data engineers
        addStr = []
        endstr = "Hello team! The following PaaS CEs are out of queue on {}: ".format(
            roster.TODAYS_DATE)

        if not self.inTraining or len(self.inTraining) == 0:
            endstr = "Hello team! No PaaS CEs are out of queue today. "

        else:
            
            for eng in self.inTraining:
                flag = False
                for tag in eng['tags']:
                    if tag in PAAS_TAGS:
                        flag = True
                        break
                if flag:
                    addStr.append(eng["first_name"] + " " + eng["last_name"])

        endstr += ', '.join(addStr)

        self.slackBotUser.chat.post_message(channel='#sup-pcf-staff',
                                            text=endstr,
                                            username='Out of Queue Bot',
                                            link_names=1
                                            )

    def msgData(self):
        DATA_TAGS = {36, 37, 38}  # Tags for data engineers

        endstr = "Hello team! The following data CEs are out of queue on {}: ".format(
            roster.TODAYS_DATE)
        addStr = []
        if not self.inTraining or len(self.inTraining) == 0:
            endstr = "Hello team! No data CEs are out of queue today."

        else:
            for eng in self.inTraining:
                flag = False
                for tag in eng['tags']:
                    if tag in DATA_TAGS:
                        flag = True
                        break
                if flag:
                    addStr.append(eng["first_name"] + " " + eng["last_name"])

        
        endstr += ', '.join(addStr)
            
        self.slackBotUser.chat.post_message(channel='#support-data-amer',
                                            text=endstr,
                                            username='Out of Queue Bot',
                                            link_names=1
                                            )