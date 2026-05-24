import os
import requests
import threading
import time
from flask import Flask

app = Flask(__name__)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

def get_candles():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F?interval=1h&range=5d"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    d = r.json()["chart"]["result"][0]
    closes = d["indicators"]["quote"][0]["close"]
    highs = d["indicators"]["quote"][0]["high"]
    lows = d["indicators"]["quote"][0]["low"]
    return closes, highs, lows

def ema(data, period):
    k = 2 / (period + 1)
    e = data[0]
    for p in data[1:]:
        if p is not None:
            e = p * k + e * (1 - k)
    return e

def rsi(data, period=14):
    gains, losses = [], []
    for i in range(1, len(data)):
        if data[i] and data[i-1]:
            diff = data[i] - data[i-1]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
    if not gains:
        return 50
    ag = sum(gains[-period:]) / period
    al = sum(losses[-period:]) / period
    if al == 0:
        return 100
    return 100 - (100 / (1 + (ag / al)))

def atr(highs, lows, closes, period=14):
    trs = []
    for i in range(1, len(closes)):
        if closes[i] and closes[i-1] and highs[i] and lows[i]:
            tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
            trs.append(tr)
    return sum(trs[-period:]) / period if trs else 1

last_signal = None

def analyze():
    global last_signal
    while True:
        try:
            closes, highs, lows = get_candles()
            closes = [c for c in closes if c]
            price = closes[-1]
            ema200 = ema(closes, min(200, len(closes)))
            rsi_val = rsi(closes)
            atr_val = atr(highs, lows, closes)
            sl_dist = atr_val * 1.5
            tp_dist = atr_val * 3
            signal = None
            if price > ema200 and rsi_val < 35:
                signal = "BUY"
                sl = round(price - sl_dist, 2)
                tp = round(price + tp_dist, 2)
            elif price < ema200 and rsi_val > 65:
                signal = "SELL"
                sl = round(price + sl_dist, 2)
                tp = round(price - tp_dist, 2)
            if signal and signal != last_signal:
                last_signal = signal
                emoji = "🟢" if signal == "BUY" else "🔴"
                msg = f"{emoji} <b>{signal} GOLD</b>\nEntry: {round(price,2)}\nStop Loss: {sl}\nTake Profit: {tp}\nRSI: {round(rsi_val,1)}"
                send(msg)
        except:
            pass
        time.sleep(300)

t = threading.Thread(target=analyze)
t.daemon = True
t.start()

@app.route("/")
def home():
    return "Gold Signal Bot Running"
