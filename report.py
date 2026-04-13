import json
from config import TOP_SETUPS


def build_report(results, history_summary=None):
    accepted = [r for r in results if r.get("accepted")]
    rejected = [r for r in results if not r.get("accepted")]
    accepted = sorted(accepted, key=lambda x: x["score"], reverse=True)[:TOP_SETUPS]

    lines = []
    lines.append("===== SCANNER REPORT =====")
    if history_summary:
        lines.append(
            f"history: total={history_summary['total']} | wins={history_summary['wins']} | losses={history_summary['losses']} | win_rate={history_summary['win_rate_pct']}%"
        )
    lines.append("")
    lines.append("TOP SETUPS")
    if not accepted:
        lines.append("- no setups accepted")
    for item in accepted:
        lines.append(f"- {item['symbol']} {item['direction']} | score={item['score']} | confidence={item['confidence']}")
        lines.append(f"  price={item['last_price']} | entry={item['entry']} | zone={item['entry_zone_low']} -> {item['entry_zone_high']} | tp={item['tp']} | sl={item['sl']} | invalidation={item['invalidation']}")
        lines.append(f"  rsi={item['fast_rsi']} | context={item['context_rsi']} | stretch={item['stretch']} | zscore={item['zscore']}")
        lines.append(f"  reason={item['reason']}")

    lines.append("")
    lines.append("REJECTED")
    if not rejected:
        lines.append("- no rejected symbols")
    for item in rejected:
        lines.append(f"- {item['symbol']} | reason={item.get('reason')}")
    return "\n".join(lines)


def export_report(results, history_summary=None, text_path="scanner_report.txt", json_path="scanner_report.json"):
    with open(text_path, "w", encoding="utf-8") as text_file:
        text_file.write(build_report(results, history_summary=history_summary))
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump({"history": history_summary, "results": results}, json_file, indent=2)
