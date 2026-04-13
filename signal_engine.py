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
    base_move = max(last_price * max(stretch_abs, 0.0015), last_price * 0.002)

    if direction == "LONG":
        entry = last_price
        tp = last_price + base_move
        sl = last_price - (base_move * 0.75)
        invalidation = sl
    else:
        entry = last_price
        tp = last_price - base_move
        sl = last_price + (base_move * 0.75)
        invalidation = sl

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
        "tp": round(tp, 6),
        "sl": round(sl, 6),
        "invalidation": round(invalidation, 6),
        "reason": f"reversion setup accepted with stretch {round(stretch, 6)} and zscore {round(price_zscore, 4)}",
    }
