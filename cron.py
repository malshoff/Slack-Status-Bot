import os
import json
from slackbot import SlackBot
from roster import Roster

# 45 12 ? * *
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

