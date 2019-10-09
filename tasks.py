from celery import Celery
from celery.schedules import crontab
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
app.conf.timezone = 'US/Eastern'

CONNECT_STRING = os.environ["CONNECT_STRING"]
client = MongoClient(f'{CONNECT_STRING}')
db = client.queue
employees = db.employees
threads = db.threads
s = SlackBot()

ZOOM_MONGO = os.environ["ZOOM_MONGO"]
zoomDBClient = MongoClient(ZOOM_MONGO)
zdb = zoomDBClient.zoom
zoomUsers = zdb.users

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls refresh every minute.
    sender.add_periodic_task(60.0, refresh.s(), name='Refresh every minute')

    # Executes every Monday morning at 7:30 a.m.
    sender.add_periodic_task(
        crontab(hour=8, minute=30),
        daily.s(),
    )

@app.task
def daily():
    rost = Roster("password.json", "EAST")
    rost.setEmployees()
    rost.setOutOfQueue()

    s = SlackBot()
    print("From cron.py")
    print(s.inTraining)

    if s.inTraining:
        for engineer in s.inTraining:
            s.setStatus(engineer)

    s.msgOutOfQueue()
    s.msgAllStaff()

@app.task
def listInMeeting():
    allmatches = []
    inMeeting = zoomUsers.find({
    "num_meetings": {
        "$gt": 0
    }
    })
    for n in inMeeting:
        allmatches.append(f"{n['first_name']} {n['last_name']}")

    s.slackBotUser.chat.post_message(channel='#sup-zoom-test',
                                     text=f"The following CEs are on a Zoom Currently:{', '.join(allmatches)}",
                                     username='Availability Bot',
                                     link_names=1
                                     )
    return "Done"

@app.task
def choose_command(command, user_id):
    s.refreshOOQ()
    print(f"Training Engineers: {s.inTraining}")
    print(f"Training IDS: {s.TRAINING_IDS}")
    
    if command == "list":
        listTestChannel(user_id)

    elif command == "zoom":
        listInMeeting()

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
    print(e)
    if e["event"].get("thread_ts"):
        seen = threads.find_one({"thread_id": e["event"]["thread_ts"]})
        if not seen:
            print(f"This thread was not in the db:")
        else:
            print(f"Seen is {seen}")
            return "I don't respond within threads!"
    if e["event"].get("bot_id"):
        return "This is a bot!"

    s.refreshOOQ()
    if not s.TRAINING_IDS:
        return "Message from processEvent task: There are no engineers in training today"

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
        thread = e["event"].get("ts")
        threads.insert_one({'thread_id':thread})
        
        
        s.slackBotUser.chat.post_message(channel=e["event"]["channel"],
                                        text=f"Hi! <@{flag}> is out of queue today, and may not be able to respond to this message immediately.",
                                        username='Out of Queue Bot',
                                        link_names=1,
                                        thread_ts=e["event"]["ts"]
                                        )
        
    else:
        print("This message does not apply!")

@app.task
def refresh():
    rost = Roster("password.json", "EAST")
    rost.setEmployees()
    rost.setOutOfQueue()
    s = SlackBot()
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


def listTestChannel(user):
    s.msgOutOfQueue(user)
    return "listTestChannel: ran"


def listAll():
    s.msgAllStaff()
    return "listAll: ran"
