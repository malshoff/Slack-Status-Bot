from celery import Celery 
import os 
import json 
from slackbot import SlackBot
from pymongo import MongoClient

vcap_services =  os.getenv('VCAP_SERVICES', None)
vcap_services = json.loads(vcap_services)

rediscloud = vcap_services.get("p-redis")[0]
redis_url = 'redis://:{0}@{1}:{2}/0'.format(
    rediscloud["credentials"]["password"],
    rediscloud["credentials"]["host"],
    rediscloud["credentials"]["port"]
)

BROKER_URL = redis_url

app = Celery('tasks', broker=BROKER_URL)

s = SlackBot()

CONNECT_STRING = os.environ["CONNECT_STRING"]
client = MongoClient(f'{CONNECT_STRING}')
db = client.queue
users = db.users

@app.task
def testtask(command,user_id):
    s.slackBotUser.chat.post_message(channel='#ooq-test', 
                                                 text="testing with the Redis queue worked!",
                                                 username='Out of Queue Bot',
                                                 link_names=1
                                                )
    return "Done"                                           

@app.task
def choose_command(command,user_id):
        if command == "list":    
            s.msgOutOfQueue()
        elif command == "listall":
            if user_id == 'UF57DA49F':
                s.msgAllStaff()
        elif command == "run":
            cur = users.find_one({"user_id":user_id})
            return run(cur,user_id)
        elif command == "runall":
            if user_id == 'UF57DA49F': #Malachi's id
                runAll()
            else:
                return "Only Malachi can run this command. MUAHAHAHAHA"

        elif command == "refresh":
            refresh()

def refresh():
    s = SlackBot()

def run(eng,user_id):

    if eng:
        s.setStatus(eng)
        return "Ran set status!"
    else:
        info = s.getUserById(user_id)
        url = s.buildURL(info[1])
        s.sendInitMsg(url,user_id)
   

def runAll():
    for engineer in s.inTraining:
        s.setStatus(engineer)