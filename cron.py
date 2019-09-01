import os
import json
from slackbot import SlackBot

s = SlackBot()

for engineer in s.inTraining:
    s.setStatus(engineer)

s.msgOutOfQueue()
s.msgAllStaff()