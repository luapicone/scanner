import csv
import os
from datetime import datetime, timezone

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
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        for item in accepted:
            writer.writerow(
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
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
                }
            )


def evaluate_pending_signals(fetcher, timeframe="5m", lookahead_bars=12, path=HISTORY_FILE):
    rows = load_rows(path)
    updated = False

    for row in rows:
        if row.get("result") != "PENDING":
            continue

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
                    row["evaluated_at"] = datetime.now(timezone.utc).isoformat()
                    updated = True
                    break
                if high >= tp:
                    row["result"] = "WIN"
                    row["evaluated_at"] = datetime.now(timezone.utc).isoformat()
                    updated = True
                    break
            else:
                if high >= sl:
                    row["result"] = "LOSS"
                    row["evaluated_at"] = datetime.now(timezone.utc).isoformat()
                    updated = True
                    break
                if low <= tp:
                    row["result"] = "WIN"
                    row["evaluated_at"] = datetime.now(timezone.utc).isoformat()
                    updated = True
                    break

    if updated:
        save_rows(rows, path)


def summarize_history(path=HISTORY_FILE):
    if not os.path.exists(path):
        return {"total": 0, "wins": 0, "losses": 0, "win_rate_pct": 0.0}

    total = wins = losses = 0
    with open(path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            result = row.get("result", "").upper()
            if result not in {"WIN", "LOSS"}:
                continue
            total += 1
            if result == "WIN":
                wins += 1
            else:
                losses += 1

    win_rate = (wins / total * 100) if total else 0.0
    return {"total": total, "wins": wins, "losses": losses, "win_rate_pct": round(win_rate, 2)}
