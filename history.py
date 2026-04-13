import csv
import os
from datetime import datetime, timedelta, timezone

from config import SIGNAL_DEDUP_MINUTES

HISTORY_FILE = "signal_history.csv"


FIELDNAMES = [
    "timestamp",
    "symbol",
    "direction",
    "score",
    "confidence",
    "entry",
    "tp",
    "sl",
    "invalidation",
    "result",
    "evaluated_at",
    "expiry_at",
]


def load_rows(path=HISTORY_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save_rows(rows, path=HISTORY_FILE):
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def append_signals(results, path=HISTORY_FILE):
    accepted = [r for r in results if r.get("accepted")]
    rows = load_rows(path)
    now = datetime.now(timezone.utc)

    for item in accepted:
        duplicate_found = False
        for row in reversed(rows):
            if row.get("symbol") != item["symbol"] or row.get("direction") != item["direction"]:
                continue
            row_time = datetime.fromisoformat(row["timestamp"])
            if now - row_time <= timedelta(minutes=SIGNAL_DEDUP_MINUTES):
                duplicate_found = True
            break

        if duplicate_found:
            continue

        rows.append(
            {
                "timestamp": now.isoformat(),
                "symbol": item["symbol"],
                "direction": item["direction"],
                "score": item["score"],
                "confidence": item["confidence"],
                "entry": item["entry"],
                "tp": item["tp"],
                "sl": item["sl"],
                "invalidation": item["invalidation"],
                "result": "PENDING",
                "evaluated_at": "",
                "expiry_at": (now + timedelta(minutes=60)).isoformat(),
            }
        )

    save_rows(rows, path)


def evaluate_pending_signals(fetcher, timeframe="5m", lookahead_bars=12, path=HISTORY_FILE):
    rows = load_rows(path)
    updated = False

    now = datetime.now(timezone.utc)

    for row in rows:
        if row.get("result") != "PENDING":
            continue

        expiry_at = row.get("expiry_at")
        expiry_dt = datetime.fromisoformat(expiry_at) if expiry_at else now
        symbol = row["symbol"]
        direction = row["direction"]
        tp = float(row["tp"])
        sl = float(row["sl"])
        candles = fetcher.fetch_ohlcv(symbol, timeframe=timeframe, limit=lookahead_bars)

        if not candles:
            continue

        for candle in candles:
            high = float(candle[2])
            low = float(candle[3])
            if direction == "LONG":
                if low <= sl:
                    row["result"] = "LOSS"
                    row["evaluated_at"] = now.isoformat()
                    updated = True
                    break
                if high >= tp:
                    row["result"] = "WIN"
                    row["evaluated_at"] = now.isoformat()
                    updated = True
                    break
            else:
                if high >= sl:
                    row["result"] = "LOSS"
                    row["evaluated_at"] = now.isoformat()
                    updated = True
                    break
                if low <= tp:
                    row["result"] = "WIN"
                    row["evaluated_at"] = now.isoformat()
                    updated = True
                    break

        if row.get("result") == "PENDING" and now >= expiry_dt:
            row["result"] = "EXPIRED"
            row["evaluated_at"] = now.isoformat()
            updated = True

    if updated:
        save_rows(rows, path)


def summarize_history(path=HISTORY_FILE):
    if not os.path.exists(path):
        return {"total": 0, "wins": 0, "losses": 0, "expired": 0, "win_rate_pct": 0.0}

    total = wins = losses = expired = 0
    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            result = row.get("result", "").upper()
            if result not in {"WIN", "LOSS", "EXPIRED"}:
                continue
            total += 1
            if result == "WIN":
                wins += 1
            elif result == "LOSS":
                losses += 1
            else:
                expired += 1

    settled = wins + losses
    win_rate = (wins / settled * 100) if settled else 0.0
    return {"total": total, "wins": wins, "losses": losses, "expired": expired, "win_rate_pct": round(win_rate, 2)}
