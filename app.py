import os
import slack
import flask
from flask import Flask, request, redirect
from pymongo import MongoClient
from slackbot import SlackBot
import requests
from threading import Thread

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
    "list"
}
RESPONSE_JSON = {
    "text": "Received Command"
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
    #print(request.args['state'])
    names = request.args['state'].split(' ')
    #print(names)
    first_name = names[0]
    last_name = names[1]

    #print(auth_code)
  # An empty string is a valid token for this request
    client = slack.WebClient(token="")

  # Request the auth tokens from Slack
    response = client.oauth_access(
        client_id=client_id,
        client_secret=client_secret,
        code=auth_code
    )
    
    print(response)
    # Save the bot token to an environmental variable or to your data store
# for later use
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

    '''nextClient = slack.WebClient(token=response['access_token'])
    test = nextClient.chat_postMessage(
        channel='#test-queue',
        text="Hello world!")'''
    
    return "Auth complete! You will receive a notification on your Out of Queue day!" 

@app.errorhandler(404)
def page_not_found(e):
    return "command not found"

@app.route("/command", methods=["GET","POST"])
def execCommand():
    def choose_command(command,user_id):
        if command == "list":
            s.msgOutOfQueue()
        elif command == "run":
            cur = users.find_one({"user_id":user_id})
            return run(cur,user_id)
        elif command == "runall":
            if user_id == 'UF57DA49F':
                runAll()
            else:
                return "Only Malachi can run this command. MUAHAHAHAHA"
    user_id = request.form.get("user_id")
    command = request.form.get("text")
    if command not in COMMANDS:
            flask.redirect(404)
    #url = request.form.get("response_url")
    thread = Thread(target=choose_command,kwargs= {'command':command,'user_id':user_id})
    thread.start()
    return "Please visit #ooq-test to see the result! (this may take a few seconds)"

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