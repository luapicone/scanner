import os

import requests
from dotenv import load_dotenv

load_dotenv()


def _post_to_discord(message):
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False
    response = requests.post(webhook_url, json={"content": message}, timeout=10)
    response.raise_for_status()
    return True


def build_signal_message(signal):
    direction_emoji = "🟢" if signal["direction"] == "LONG" else "🔴"
    return (
        f"🚨 **SETUP DETECTADO** {direction_emoji}\n"
        f"**{signal['symbol']}** | {signal['direction']}\n"
        f"Score: `{signal['score']}` | Confidence: `{signal['confidence']}`\n"
        f"Entry: `{signal['entry']}`\n"
        f"Zone: `{signal.get('entry_zone_low', signal['entry'])}` -> `{signal.get('entry_zone_high', signal['entry'])}`\n"
        f"TP: `{signal['tp']}` | SL: `{signal['sl']}`\n"
        f"Invalidation: `{signal['invalidation']}`\n"
        f"Reason: {signal['reason']}"
    )


def build_result_message(row):
    result = row["result"]
    emoji = "✅" if result == "WIN" else "❌" if result == "LOSS" else "⏳"
    return (
        f"{emoji} **SEÑAL CERRADA**\n"
        f"**{row['symbol']}** | {row['direction']}\n"
        f"Result: `{row['result']}`\n"
        f"Entry: `{row['entry']}` | TP: `{row['tp']}` | SL: `{row['sl']}`\n"
        f"Evaluated at: `{row['evaluated_at']}`"
    )


def send_discord_alert(signal):
    return _post_to_discord(build_signal_message(signal))


def send_discord_result_alert(row):
    return _post_to_discord(build_result_message(row))
