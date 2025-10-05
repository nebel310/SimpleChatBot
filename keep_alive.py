from flask import Flask
from threading import Thread
import logging

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    try:
        app.run(host='0.0.0.0', port=8080)
    except Exception as e:
        logging.error(f"Web server error: {e}")

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()