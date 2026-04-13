import os

import requests
from dotenv import load_dotenv

load_dotenv()


def build_signal_message(signal):
    return (
        "🚨 **SETUP DETECTADO**\n"
        f"- Symbol: {signal['symbol']}\n"
        f"- Direction: {signal['direction']}\n"
        f"- Score: {signal['score']}\n"
        f"- Confidence: {signal['confidence']}\n"
        f"- Entry: {signal['entry']}\n"
        f"- TP: {signal['tp']}\n"
        f"- SL: {signal['sl']}\n"
        f"- Invalidation: {signal['invalidation']}\n"
        f"- Reason: {signal['reason']}"
    )


def send_discord_alert(signal):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False

    response = requests.post(webhook_url, json={"content": build_signal_message(signal)}, timeout=10)
    response.raise_for_status()
    return True
