from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
import slack
import os
from slackeventsapi import SlackEventAdapter

import scrape_gn
from scrape_gn import scrape_google_news

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
    print(user_id, BOT_ID)
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
    # Use the scrape_google_news function to get top news articles
    news_results = scrape_google_news(message)

    if news_results:
        news_message = f"Here are the top 5 news articles on {message}:\n"

        for index, result in enumerate(news_results, 1):
            news_message += f"{index}. {result['title']}\n{result['url']}\n\n"

        return news_message

    return f"Sorry, I couldn't fetch news on {message} at the moment."


@app.route('/check', methods=['GET'])
def check():
    return jsonify({'message': 'Hello World'})


if __name__ == '__main__':
    print(getTopNews("test", "India vs Afghnaistan"))
    app.run(debug=True, host='0.0.0.0', port=5000)
