import ccxt


class DataFetcher:
    def __init__(self):
        self.exchange = ccxt.binanceusdm({"enableRateLimit": True})

    def fetch_ohlcv(self, symbol, timeframe, limit):
        return self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
