from statistics import mean, pstdev


def sma(values):
    return mean(values) if values else None


def rsi(closes, period=14):
    if len(closes) < period + 1:
        return None
    gains = []
    losses = []
    for i in range(-period, 0):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def zscore(values, period=20):
    if len(values) < period:
        return None
    sample = values[-period:]
    mu = mean(sample)
    sigma = pstdev(sample)
    if sigma == 0:
        return 0.0
    return (sample[-1] - mu) / sigma


def rolling_vwap(closes, volumes, window=20):
    if len(closes) < window or len(volumes) < window:
        return None
    c = closes[-window:]
    v = volumes[-window:]
    total_vol = sum(v)
    if total_vol == 0:
        return None
    return sum(price * vol for price, vol in zip(c, v)) / total_vol
