import os
import json
from slackbot import SlackBot
from roster import Roster

s = SlackBot()
rost = Roster("password.json", "EAST")

rost.setOutOfQueue()

for engineer in s.inTraining:
    s.setStatus(engineer)

s.msgOutOfQueue()
s.msgAllStaff()