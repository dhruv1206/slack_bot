from flask import Flask, request, jsonify, redirect, url_for, session
from flask_oauthlib.client import OAuth
import requests
import os
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.oauth import OAuthStateStore, AuthorizeUrlGenerator
from slackeventsapi import SlackEventAdapter


env_path = ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
app.secret_key = os.environ["FLASK_SECRET_KEY"]

# Add OAuth configuration
oauth = OAuth(app)
slack = oauth.remote_app(
    'slack',
    consumer_key=os.environ['SLACK_CLIENT_ID'],
    consumer_secret=os.environ['SLACK_CLIENT_SECRET'],
    request_xtoken_params={'scope': 'app_mentions:read,chat:write,im:history'},
    base_url='https://slack.com/api/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://slack.com/api/oauth.access',
    authorize_url='https://slack.com/oauth/v2/authorize',
)

slack_event_adapter = SlackEventAdapter(
    os.environ["SIGNING_SECRET"], "/slack/events", app)
client = WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# OAuth routes


@app.route('/login')
def login():
    return slack.authorize(callback=url_for('authorized', _external=True, _scheme='https'))


@app.route('/logout')
def logout():
    session.pop('slack_token', None)
    return redirect(url_for('index'))


@app.route('/authorized')
@slack.authorized_handler
def authorized(resp):
    if resp is None or 'access_token' not in resp:
        return 'Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        )
    session['slack_token'] = (resp['access_token'], '')
    return redirect(url_for('index'))


@slack.tokengetter
def get_slack_oauth_token():
    return session.get('slack_token')

# Add your existing code below this line


@slack_event_adapter.on("app_mention")
def mention(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    message = event.get("text").split("<@U06CV5K9LPR>")[1].strip()
    if user_id != client.token:  # Check if the user is the bot itself
        client.chat_postMessage(
            channel=channel_id, text=getTopNews(user_id, message))


@slack_event_adapter.on("message")
def handle_message(payload):
    print(payload)
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    message = event.get("text")
    print(user_id, client.token)
    if user_id != client.token:  # Check if the user is the bot itself
        client.chat_postMessage(
            channel=channel_id, text=getTopNews(user_id, message))


def getTopNews(user_id, message):
    url = f"https://newsapi.org/v2/everything?q={message}&sortBy=publishedAt&apiKey=" + \
        os.environ['NEWS_API_KEY']
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if 'articles' in data:
            articles = data['articles'][:5]

            news_message = f"Here are the top 5 news articles on {message}:\n"

            for index, article in enumerate(articles, 1):
                news_message += f"{index}. {article['title']}\n"

            return news_message

    return f"Sorry, I couldn't fetch news on {message} at the moment."


@app.route('/check', methods=['GET'])
def check():
    return jsonify({'message': 'Hello World'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
