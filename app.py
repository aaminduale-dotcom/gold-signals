import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    alert = data.get("alert", "")
    price = data.get("price", "")
    sl = data.get("sl", "")
    tp = data.get("tp", "")
    if alert == "BUY":
        send(f"🟢 BUY GOLD\nEntry: {price}\nStop Loss: {sl}\nTake Profit: {tp}")
    elif alert == "SELL":
        send(f"🔴 SELL GOLD\nEntry: {price}\nStop Loss: {sl}\nTake Profit: {tp}")
    return "ok"

@app.route("/")
def home():
    return "Gold Signals Bot Running"
