import os
import json
from slackbot import SlackBot
from roster import Roster

s = SlackBot()
rost = Roster("password.json", "EAST")

for engineer in s.inTraining:
    s.setStatus(engineer)

s.msgOutOfQueue()
s.msgAllStaff()