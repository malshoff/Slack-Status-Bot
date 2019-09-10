from celery import Celery
import os
import json
from slackbot import SlackBot
from pymongo import MongoClient
from roster import Roster

vcap_services = os.getenv('VCAP_SERVICES', None)
vcap_services = json.loads(vcap_services)

rediscloud = vcap_services.get("p-redis")[0]
redis_url = 'redis://:{0}@{1}:{2}/0'.format(
    rediscloud["credentials"]["password"],
    rediscloud["credentials"]["host"],
    rediscloud["credentials"]["port"]
)

BROKER_URL = redis_url

app = Celery('tasks', broker=BROKER_URL)


CONNECT_STRING = os.environ["CONNECT_STRING"]
client = MongoClient(f'{CONNECT_STRING}')
db = client.queue
employees = db.employees
s = SlackBot()

@app.task
def testtask(command, user_id):
    
    s.slackBotUser.chat.post_message(channel='#ooq-test',
                                     text="testing with the Redis queue worked!",
                                     username='Out of Queue Bot',
                                     link_names=1
                                     )
    return "Done"


@app.task
def choose_command(command, user_id):
    if command == "list":
        listTestChannel()

    elif command == "listall":
        if user_id == 'UF57DA49F':
            listAll()

    elif command == "run":
        cur = employees.find_one({"user_id": user_id})
        return run(cur, user_id)
        
    elif command == "runall":
        if user_id == 'UF57DA49F':  # Malachi's id
            runAll()
        else:
            return "Only Malachi can run this command. MUAHAHAHAHA"

    elif command == "refresh":
        refresh()


@app.task
def processEvent(e):
    
    print(f"Training Engineers: {s.inTraining}")
    print(f"Training IDS: {s.TRAINING_IDS}")

    if not s.TRAINING_IDS:
        print("Message from processEvent task: There are no engineers in training today")
        return

    if e["event"].get("bot_id"):
        return "This is a bot!"

    flag = False
    try:
        msg = e["event"]["text"]
    except:
        print(f'Error: {e}')
        return

    for eng in s.TRAINING_IDS:
        if eng in msg:
            flag = eng
    #print(f"Flag after for loop: {flag}")
    if flag != False:
        thread = e["event"]["ts"]
        s.slackBotUser.chat.post_message(channel=e["event"]["channel"],
                                         text=f"Hi! <@{flag}> is out of queue today, and may not be able to respond to this message immediately.",
                                         username='Out of Queue Bot',
                                         link_names=1,
                                         thread_ts=thread
                                         )
    else:
        print("This message does not apply!")

def refresh():
    rost = Roster("password.json", "EAST")
    rost.setEmployees()
    rost.setOutOfQueue()
    s.refreshOOQ()
    print(f"Refresh Complete! Value of inTraining: {s.inTraining}")


def run(eng, user_id):
   

    if eng:
        s.setStatus(eng)
        return "From run(): Ran set status!"
    else:
        info = s.getUserById(user_id)
        url = s.buildURL(info[1])
        s.sendInitMsg(url, user_id)


def runAll():
  

    if not s.inTraining:
        return False
    for engineer in s.inTraining:
        s.setStatus(engineer)
    return "ran runAll()"


def listTestChannel():
    
    s.msgOutOfQueue()
    return "listTestChannel: ran"

def listAll():
   
    s.msgAllStaff()
    return "listAll: ran"
