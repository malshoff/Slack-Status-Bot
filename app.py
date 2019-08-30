import os
import slack
import slacker
import flask
import json
from flask import Flask, request, redirect
from pymongo import MongoClient
from slackbot import SlackBot
import requests
from threading import Thread
from tasks import testtask,choose_command, processEvent

client_id = os.environ["SLACK_CLIENT_ID"]
client_secret = os.environ["SLACK_CLIENT_SECRET"]
oauth_scope = os.environ["SLACK_SCOPE"]
CONNECT_STRING = os.environ["CONNECT_STRING"]



app = Flask(__name__)

client = MongoClient(f'{CONNECT_STRING}')
db = client.queue
users = db.users


s = SlackBot()

COMMANDS = {
    "list",
    "listall",
    "run",
    "runall", 
    "refresh",
    "test"
}



@app.route("/", methods=["GET"])
def pre_install():
    name = request.args['name'].split(' ')
    first_name = name[0]
    if len(name) == 3:
        last_name = name[2]
    else:
        last_name = name[1]
    
    return f'<a href="https://slack.com/oauth/authorize?scope={ oauth_scope }&client_id={ client_id }&state={first_name}+{last_name}">Authorize App (you will be redirected to Slack)</a>'

@app.route("/finish_auth", methods=["GET", "POST"])
def post_install():
  # Retrieve the auth code from the request params
    auth_code = request.args['code']
    names = request.args['state'].split(' ')
    first_name = names[0]
    last_name = names[1]


    client = slack.WebClient(token="")

  # Request the auth tokens from Slack
    response = client.oauth_access(
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )
    
  
    # Save the token to an to data store for later use
    person = {
        'access_token': response['access_token'],
        'user_id': response['user_id'],
        'first_name': first_name,
        'last_name': last_name,
    }

    users.update(
        {'user_id': response['user_id']},
        {'$set': person},
        upsert = True 
    )

    run(person,response['user_id'])
    
    return "Auth complete! You will receive a notification on your Out of Queue day, and your status will be updated! \n\n Please check out #sup-ooq for discussion" 

@app.errorhandler(404)
def page_not_found(e):
    return "Not found"


@app.route("/command", methods=["GET","POST"])
def execCommand():
    user_id = request.form.get("user_id")
    command = request.form.get("text")
    if command not in COMMANDS:
            return flask.redirect(404)
    
    #enqueue the command
    choose_command.apply_async(args=(command,user_id), queue="commands")
    return "Executing command. This may take a few seconds."

@app.route("/events", methods=["POST"])
def events():
    r = request.get_json()
    processEvent.apply_async(args=(r,), queue="events")
    return "received event"

def run(eng,user_id):

    if eng:
        s.setStatus(eng)
        return "Ran set status!"
    else:
        info = s.getUserById(user_id)
        url = s.buildURL(info[1])
        s.sendInitMsg(url,user_id)