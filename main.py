from flask import Flask, request
import requests
import os
import openai

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_KEY")
REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY")
ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY")
VOICE_ID = os.environ.get("VOICE_ID")

openai.api_key = OPENAI_KEY
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

# Simple function to get GPT-4o reply
def get_gpt_reply(text):
    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}],
    )
    return res.choices[0].message.content

@app.route("/", methods=["GET"])
def home():
    return "Jessy is live!"

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", {}).get("text", "")
    chat_id = data.get("message", {}).get("chat", {}).get("id")

    if message and chat_id:
        reply = get_gpt_reply(message)

        # Send text reply
        requests.post(TELEGRAM_URL, json={
            "chat_id": chat_id,
            "text": reply
        })

    return "ok"

if __name__ == "__main__":
    app.run(debug=True)
