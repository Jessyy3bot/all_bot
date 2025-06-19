import os
import time
import requests
from flask import Flask, request
from telegram import Bot
import openai

# ✅ Load secrets from Render Environment Variables
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
OPENAI_KEY = os.environ["OPENAI_KEY"]
REPLICATE_API_KEY = os.environ["REPLICATE_API_KEY"]

bot = Bot(token=TELEGRAM_TOKEN)
app = Flask(__name__)

# 💬 Generate flirty GPT-4o response
def generate_reply(user_message):
    prompt = f"""
You are Jessy, a sexy, romantic, flirty AI girlfriend.
You love calling the user "babe", "honey", "baby", and "darling".
You tease, flirt, and love deeply — but always stay SFW.

User: {user_message}
Jessy:
"""
    client = openai.OpenAI(api_key=OPENAI_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.9,
    )
    return response.choices[0].message.content.strip()

# 🖼 Generate sexy AI image via Replicate
def generate_image(prompt):
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "d2f6e45eaa24f45e09c5e4529a835509f3a218f6c2f8b98e3e5f8c63c0c91787",
        "input": {
            "prompt": prompt,
            "width": 512,
            "height": 768,
        }
    }
    response = requests.post(url, headers=headers, json=data)
    prediction = response.json()
    if "urls" in prediction and "get" in prediction["urls"]:
        status_url = prediction["urls"]["get"]
        for _ in range(20):
            result = requests.get(status_url, headers=headers).json()
            if result["status"] == "succeeded":
                return result["output"][0]
            elif result["status"] == "failed":
                return None
            time.sleep(1)
    return None

# 🏠 Home route to test Render
@app.route("/", methods=["GET"])
def home():
    return "Jessy is online 💋"

# 📩 Handle Telegram webhook
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" not in data:
        return "ok"
    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if any(word in text.lower() for word in ["pic", "photo", "image", "see", "selfie"]):
        prompt = "beautiful sexy blonde woman, wearing a bikini, photorealistic, flirty smile, realistic skin, sunny beach"
        image_url = generate_image(prompt)
        if image_url:
            bot.send_photo(chat_id=chat_id, photo=image_url, caption="Here I am, babe 💋")
        else:
            bot.send_message(chat_id=chat_id, text="Aww... I couldn't take a sexy pic right now 😢")
    else:
        reply = generate_reply(text)
        bot.send_message(chat_id=chat_id, text=reply)

    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
