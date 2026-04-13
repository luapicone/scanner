from config import TOP_SETUPS


def build_report(results):
    accepted = [r for r in results if r.get("accepted")]
    rejected = [r for r in results if not r.get("accepted")]
    accepted = sorted(accepted, key=lambda x: x["score"], reverse=True)[:TOP_SETUPS]

    lines = []
    lines.append("===== SCANNER REPORT =====")
    lines.append("")
    lines.append("TOP SETUPS")
    if not accepted:
        lines.append("- no setups accepted")
    for item in accepted:
        lines.append(
            f"- {item['symbol']} {item['direction']} | score={item['score']} | price={item['last_price']} | "
            f"rsi={item['fast_rsi']} | context={item['context_rsi']} | stretch={item['stretch']} | zscore={item['zscore']}"
        )

    lines.append("")
    lines.append("REJECTED")
    if not rejected:
        lines.append("- no rejected symbols")
    for item in rejected:
        lines.append(f"- {item['symbol']} | reason={item.get('reason')}")
    return "\n".join(lines)
