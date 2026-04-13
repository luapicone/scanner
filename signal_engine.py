from config import (
    CONTEXT_LONG_MAX,
    CONTEXT_SHORT_MIN,
    RSI_LONG_MAX,
    RSI_SHORT_MIN,
    SCORE_MIN,
    VWAP_STRETCH_MIN,
    ZSCORE_MIN,
)
from indicators import rolling_vwap, rsi, zscore


def _confidence_label(score):
    if score >= 0.85:
        return "high"
    if score >= 0.7:
        return "medium"
    return "moderate"


def evaluate_symbol(symbol, fast_rows, context_rows):
    fast_closes = [row[4] for row in fast_rows]
    fast_volumes = [row[5] for row in fast_rows]
    context_closes = [row[4] for row in context_rows]

    fast_rsi = rsi(fast_closes)
    context_rsi = rsi(context_closes)
    price_zscore = zscore(fast_closes)
    vwap = rolling_vwap(fast_closes, fast_volumes)

    if None in (fast_rsi, context_rsi, price_zscore, vwap):
        return {"symbol": symbol, "accepted": False, "reason": "insufficient_data"}

    last_price = fast_closes[-1]
    stretch = (last_price - vwap) / vwap if vwap else 0.0

    long_ok = fast_rsi <= RSI_LONG_MAX and context_rsi <= CONTEXT_LONG_MAX and stretch <= -VWAP_STRETCH_MIN and abs(price_zscore) >= ZSCORE_MIN
    short_ok = fast_rsi >= RSI_SHORT_MIN and context_rsi >= CONTEXT_SHORT_MIN and stretch >= VWAP_STRETCH_MIN and abs(price_zscore) >= ZSCORE_MIN

    if not long_ok and not short_ok:
        return {
            "symbol": symbol,
            "accepted": False,
            "reason": "no_reversion_setup",
            "fast_rsi": round(fast_rsi, 4),
            "context_rsi": round(context_rsi, 4),
            "stretch": round(stretch, 6),
            "zscore": round(price_zscore, 4),
        }

    direction = "LONG" if long_ok else "SHORT"
    score = 0.0
    score += min(abs(stretch) / (VWAP_STRETCH_MIN * 2), 1.0) * 0.4
    score += min(abs(price_zscore) / (ZSCORE_MIN * 3), 1.0) * 0.35
    score += 0.25 if direction == "LONG" and context_rsi < CONTEXT_LONG_MAX else 0.25 if direction == "SHORT" and context_rsi > CONTEXT_SHORT_MIN else 0.0

    if score < SCORE_MIN:
        return {
            "symbol": symbol,
            "accepted": False,
            "reason": "score_below_threshold",
            "score": round(score, 4),
            "direction": direction,
        }

    stretch_abs = abs(stretch)
    zscore_abs = abs(price_zscore)
    score_boost = max(score, SCORE_MIN)

    entry_buffer = max(last_price * 0.0005, last_price * stretch_abs * 0.15)
    target_move = max(last_price * 0.0022, last_price * stretch_abs * (1.05 + score_boost))
    stop_move = max(last_price * 0.0012, target_move * (0.5 + max(0.0, 0.9 - zscore_abs) * 0.2))

    if direction == "LONG":
        entry = last_price
        entry_zone_low = last_price - (entry_buffer * 1.25)
        entry_zone_high = last_price + (entry_buffer * 0.20)
        tp = last_price + target_move
        sl = last_price - stop_move
        invalidation = sl
        freshness_distance = max(tp - entry, 1e-9)
        move_progress = max(0.0, (last_price - entry_zone_low) / freshness_distance)
    else:
        entry = last_price
        entry_zone_low = last_price - (entry_buffer * 0.20)
        entry_zone_high = last_price + (entry_buffer * 1.25)
        tp = last_price - target_move
        sl = last_price + stop_move
        invalidation = sl
        freshness_distance = max(entry_zone_high - tp, 1e-9)
        move_progress = max(0.0, (entry_zone_high - last_price) / freshness_distance)

    if move_progress <= 0.33:
        entry_status = "ENTRY_READY"
    elif move_progress <= 0.66:
        entry_status = "ENTRY_CAUTION"
    else:
        entry_status = "ENTRY_LATE"

    return {
        "symbol": symbol,
        "accepted": True,
        "direction": direction,
        "score": round(score, 4),
        "confidence": _confidence_label(score),
        "fast_rsi": round(fast_rsi, 4),
        "context_rsi": round(context_rsi, 4),
        "stretch": round(stretch, 6),
        "zscore": round(price_zscore, 4),
        "last_price": round(last_price, 6),
        "entry": round(entry, 6),
        "entry_zone_low": round(entry_zone_low, 6),
        "entry_zone_high": round(entry_zone_high, 6),
        "entry_status": entry_status,
        "move_progress_pct": round(min(move_progress, 1.0) * 100, 2),
        "tp": round(tp, 6),
        "sl": round(sl, 6),
        "invalidation": round(invalidation, 6),
        "reason": f"reversion setup accepted with stretch {round(stretch, 6)}, zscore {round(price_zscore, 4)} and score {round(score, 4)}",
    }
