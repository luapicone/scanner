from config import CANDLE_LIMIT, SYMBOLS, TIMEFRAME_CONTEXT, TIMEFRAME_FAST
from data_fetcher import DataFetcher
from history import append_signals, summarize_history
from report import build_report, export_report
from signal_engine import evaluate_symbol


def main():
    fetcher = DataFetcher()
    results = []

    for symbol in SYMBOLS:
        fast_rows = fetcher.fetch_ohlcv(symbol, TIMEFRAME_FAST, CANDLE_LIMIT)
        context_rows = fetcher.fetch_ohlcv(symbol, TIMEFRAME_CONTEXT, CANDLE_LIMIT)
        result = evaluate_symbol(symbol, fast_rows, context_rows)
        results.append(result)

    append_signals(results)
    history_summary = summarize_history()
    export_report(results, history_summary=history_summary)
    print(build_report(results, history_summary=history_summary))


if __name__ == "__main__":
    main()
