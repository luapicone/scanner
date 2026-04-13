import argparse
import time
from datetime import datetime

from config import CANDLE_LIMIT, LOOP_INTERVAL_SECONDS, SYMBOLS, TIMEFRAME_CONTEXT, TIMEFRAME_FAST
from data_fetcher import DataFetcher
from history import append_signals, evaluate_pending_signals, summarize_history
from report import build_report, export_report
from signal_engine import evaluate_symbol


def run_cycle(fetcher):
    evaluate_pending_signals(fetcher, timeframe=TIMEFRAME_FAST)
    results = []

    for symbol in SYMBOLS:
        fast_rows = fetcher.fetch_ohlcv(symbol, TIMEFRAME_FAST, CANDLE_LIMIT)
        context_rows = fetcher.fetch_ohlcv(symbol, TIMEFRAME_CONTEXT, CANDLE_LIMIT)
        result = evaluate_symbol(symbol, fast_rows, context_rows)
        results.append(result)

    append_signals(results)
    history_summary = summarize_history()
    export_report(results, history_summary=history_summary)
    print(f"\n[{datetime.now().isoformat(timespec='seconds')}]")
    print(build_report(results, history_summary=history_summary))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", help="run scanner continuously")
    parser.add_argument("--interval", type=int, default=LOOP_INTERVAL_SECONDS, help="seconds between scans in loop mode")
    args = parser.parse_args()

    fetcher = DataFetcher()

    if not args.loop:
        run_cycle(fetcher)
        return

    while True:
        run_cycle(fetcher)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
