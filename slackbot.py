from slacker import Slacker
from roster import Roster
from pymongo import MongoClient
from datetime import datetime  
from datetime import timedelta  
from time import mktime
import requests
import urllib.parse
import os




class SlackBot(object):

    def __init__(self):
        self.CONNECT_STRING = os.environ["CONNECT_STRING"]
        self.roster = Roster("password.json")
        self.inTraining = self.roster.getOutOfQueue()  # list of training engineers
        self.BOT_TOKEN = os.environ['BOT_TOKEN']
        self.slackBotUser = Slacker(self.BOT_TOKEN)

    def isInDB(self,employee):
        client = MongoClient(f"{self.CONNECT_STRING}")
        db = client.queue #queue database
        users = db.users  # users collection
        cur = users.find_one({"first_name": employee['first_name'], "last_name": employee['last_name']})
        if not cur:
            return False
        else:
            return cur 
    
    #returns slack user ID and username of employee as a tuple
    def getUserByEmail(self,email):
        endpoint = 'https://slack.com/api/users.lookupByEmail'
        response = requests.post(endpoint,data= {'token':self.BOT_TOKEN, 'email':email})
        return (response.json()['user']['id'],response.json()['user']['real_name'],response.json()['user']['name'])

    def getUserById(self,user_id):
        endpoint = 'https://slack.com/api/users.info'
        response = requests.post(endpoint,data= {'token':self.BOT_TOKEN, 'user':user_id})
        return (response.json()['user']['id'],response.json()['user']['real_name'],response.json()['user']['name'])
    
    def buildURL(self,name):
        first_name = name[0]
        last_name = name[-1]
        url = f'https://queue.apps.pcfone.io/?name={first_name}+{last_name}'
        return url

    def setStatus(self,employee):
        cur = self.isInDB(employee)
        tomorrow = datetime.now() + timedelta(days=1) 
        unix_date = mktime(tomorrow.timetuple())

        if cur:
            slack = Slacker(cur['access_token'])
            slack.users.profile.set(user = cur['user_id'], name = 'status_text', 
                                    value = 'Training')
            slack.users.profile.set(user = cur['user_id'], name = 'status_emoji',
                                    value = ':thinkingman:')   
            slack.users.profile.set(user = cur['user_id'], name = 'status_expiration', 
                                    value = unix_date)
            slack.dnd.set_snooze(num_minutes=1440)             
            self.slackBotUser.chat.post_message( channel='#ooq-test', 
                                            text=f'{cur["first_name"]} is Out of Queue Today!',
                                            username='Out of Queue Bot'
                                          )
            print("SUCCESS!!!!!!!!")

        else:
            userInfo = self.getUserByEmail(employee['email'])
            url = f'https://queue.apps.pcfone.io/?name={employee["first_name"]}+{employee["last_name"]}'
            self.sendInitMsg(url,userInfo[0])

    def sendInitMsg(self,url,user_id):
        msg = f'Hi! It looks like you have not yet authorized me to set your status to "training" yet. Please follow this url to do so:{url}'
        self.slackBotUser.chat.post_message(channel=user_id, 
                                            text=msg,
                                            username='Out of Queue Bot',
                                            link_names=1,
                                            as_user=True
                                           )

    def msgOutOfQueue(self):
        
        endstr = "The following engineers are out of queue on {}: ".format(self.roster.TODAYS_DATE)
        for eng in self.inTraining:
            endstr += eng["first_name"] + " " + eng["last_name"] + ","
            
        self.slackBotUser.chat.post_message(channel='#ooq-test', 
                                            text=endstr,
                                            username='Out of Queue Bot',
                                            link_names=1
                                           )
        
#TODO: Create a different file to run the bot 
s = SlackBot()
#print(s.inTraining)
#me = s.isInDB({'first_name': 'Malachi', 'last_name': 'Shoffner'})
#s.setStatus(me)
#s.msgOutOfQueue()

'''for engineer in s.inTraining:
    s.setStatus(engineer)'''

