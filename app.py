from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import slack
import os
from slackeventsapi import SlackEventAdapter

env_path = ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ["SIGNING_SECRET"], "/slack/events", app)
client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])
BOT_ID = client.api_call("auth.test")['user_id']


@slack_event_adapter.on("app_mention")
def mention(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    message = event.get("text").split("<@U06CV5K9LPR>")[1].strip()
    if user_id != BOT_ID:
        client.chat_postMessage(
            channel=channel_id, text=getTopNews(user_id, message))


@slack_event_adapter.on("message")
def handle_message(payload):
    print(payload)
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    message = event.get("text")
    print(user_id, BOT_ID)
    if user_id != BOT_ID:
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


if __name__ == '__main__':
    app.run(debug=True)
