import csv
import json
import os
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(BASE_DIR, "signal_history.csv")
REPORT_FILE = os.path.join(BASE_DIR, "scanner_report.json")

HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Scanner Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; background:#0f172a; color:#e2e8f0; margin:0; padding:24px; }
    h1,h2 { margin:0 0 12px; }
    .grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap:12px; margin-bottom:24px; }
    .card { background:#1e293b; border-radius:14px; padding:16px; box-shadow: 0 6px 20px rgba(0,0,0,.25); }
    .value { font-size:28px; font-weight:700; margin-top:8px; }
    table { width:100%; border-collapse: collapse; margin-top:12px; background:#1e293b; border-radius:14px; overflow:hidden; }
    th, td { padding:10px 12px; border-bottom:1px solid #334155; text-align:left; font-size:14px; }
    th { background:#172033; }
    .section { margin-bottom:28px; }
  </style>
</head>
<body>
  <h1>Scanner Dashboard</h1>
  <p>Auto refresh cada 10 segundos</p>

  <div class="section">
    <div class="grid" id="summary"></div>
  </div>

  <div class="section">
    <h2>Setups actuales</h2>
    <div id="setups"></div>
  </div>

  <div class="section">
    <h2>Último scan, setups aceptados</h2>
    <div id="latestSetups"></div>
  </div>

  <div class="section">
    <h2>Último scan, descartes</h2>
    <div id="latestRejected"></div>
  </div>

  <div class="section">
    <h2>Historial reciente</h2>
    <div id="history"></div>
  </div>

  <script>
    function renderTable(containerId, columns, rows) {
      const container = document.getElementById(containerId);
      if (!rows || !rows.length) {
        container.innerHTML = '<div class="card">Sin datos</div>';
        return;
      }
      const head = columns.map(c => `<th>${c.label}</th>`).join('');
      const body = rows.map(row => `<tr>${columns.map(c => `<td>${row[c.key] ?? ''}</td>`).join('')}</tr>`).join('');
      container.innerHTML = `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
    }

    async function loadData() {
      const response = await fetch('/api/dashboard');
      const data = await response.json();

      const summary = document.getElementById('summary');
      const cards = [
        ['WR', `${data.summary.win_rate_pct}%`],
        ['Wins', data.summary.wins],
        ['Losses', data.summary.losses],
        ['Expired', data.summary.expired],
        ['Pending', data.summary.pending],
        ['Total', data.summary.total],
      ];
      summary.innerHTML = cards.map(([label, value]) => `<div class="card"><div>${label}</div><div class="value">${value}</div></div>`).join('');

      renderTable('setups', [
        { key: 'symbol', label: 'Symbol' },
        { key: 'direction', label: 'Direction' },
        { key: 'score', label: 'Score' },
        { key: 'confidence', label: 'Confidence' },
        { key: 'entry', label: 'Entry' },
        { key: 'tp', label: 'TP' },
        { key: 'sl', label: 'SL' },
        { key: 'result', label: 'Status' },
      ], data.pending_signals);

      renderTable('latestSetups', [
        { key: 'symbol', label: 'Symbol' },
        { key: 'direction', label: 'Direction' },
        { key: 'score', label: 'Score' },
        { key: 'confidence', label: 'Confidence' },
        { key: 'entry', label: 'Entry' },
        { key: 'tp', label: 'TP' },
        { key: 'sl', label: 'SL' },
        { key: 'reason', label: 'Reason' },
      ], data.latest_accepted);

      renderTable('latestRejected', [
        { key: 'symbol', label: 'Symbol' },
        { key: 'reason', label: 'Reason' },
        { key: 'fast_rsi', label: 'Fast RSI' },
        { key: 'context_rsi', label: 'Context RSI' },
        { key: 'stretch', label: 'Stretch' },
        { key: 'zscore', label: 'ZScore' },
      ], data.latest_rejected);

      renderTable('history', [
        { key: 'timestamp', label: 'Timestamp' },
        { key: 'symbol', label: 'Symbol' },
        { key: 'direction', label: 'Direction' },
        { key: 'score', label: 'Score' },
        { key: 'result', label: 'Result' },
        { key: 'evaluated_at', label: 'Evaluated' },
      ], data.recent_history);
    }

    loadData();
    setInterval(loadData, 10000);
  </script>
</body>
</html>
"""


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def load_report():
    if not os.path.exists(REPORT_FILE):
        return {"history": None, "results": []}
    with open(REPORT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/dashboard")
def api_dashboard():
    rows = load_history()
    report = load_report()

    wins = sum(1 for row in rows if row.get("result") == "WIN")
    losses = sum(1 for row in rows if row.get("result") == "LOSS")
    expired = sum(1 for row in rows if row.get("result") == "EXPIRED")
    pending = sum(1 for row in rows if row.get("result") == "PENDING")
    settled = wins + losses
    win_rate_pct = round((wins / settled * 100), 2) if settled else 0.0

    recent_history = list(reversed(rows))[:20]
    pending_signals = [row for row in reversed(rows) if row.get("result") == "PENDING"][:20]
    latest_scan = report.get("results", [])
    latest_accepted = [item for item in latest_scan if item.get("accepted")]
    latest_rejected = [item for item in latest_scan if not item.get("accepted")]

    return jsonify(
        {
            "summary": {
                "total": len(rows),
                "wins": wins,
                "losses": losses,
                "expired": expired,
                "pending": pending,
                "win_rate_pct": win_rate_pct,
            },
            "pending_signals": pending_signals,
            "recent_history": recent_history,
            "latest_scan": latest_scan,
            "latest_accepted": latest_accepted,
            "latest_rejected": latest_rejected,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5050)
