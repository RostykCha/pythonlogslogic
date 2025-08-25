from helper import stream_entries
from collections import defaultdict, Counter
from datetime import timedelta

timeouts = []
nullptr = []
ddos = []
minqty = []
warn_err_by_minute = defaultdict(lambda: {"ERROR":0,"WARN":0})
by_ip = Counter()
by_acct = Counter()

for e in stream_entries():
    if e["dt"] and e["level"] in ("ERROR","WARN"):
        key = e["dt"].replace(second=0, microsecond=0)
        warn_err_by_minute[key][e["level"]] += 1
    if e["ip"]:
        by_ip[e["ip"]] += 1
    if e["acct"]:
        by_acct[e["acct"]] += 1
    m = e["msg"] or ""
    if e["level"] == "ERROR" and "Timeout waiting for response from backend" in m:
        timeouts.append((e["dt"], e["logger"].strip(), m[:200]))
    if e["level"] == "ERROR" and "getBannedData(null)" in m:
        nullptr.append((e["dt"], e["logger"].strip(), m[:200]))
    if ("Possible DDoS" in m) or ("BANNED until" in m):
        ddos.append((e["dt"], m[:200]))
    if e["json"] and e["json"].get("code") == -1013:
        minqty.append((e["dt"], e["json"]))

def summarize_window(events, delta=timedelta(minutes=1)):
    if not events:
        return None
    t0 = min(t for t, *_ in events)
    t1 = max(t for t, *_ in events)
    return {"start": t0, "end": t1, "span_seconds": (t1 - t0).total_seconds(), "count": len(events)}

tickets = {
    "timeouts": {
        "summary": summarize_window(timeouts),
        "samples": timeouts[:5]
    },
    "rate_limiter_nullptr": {
        "summary": summarize_window(nullptr),
        "samples": nullptr[:3]
    },
    "ddos_ban": {
        "summary": summarize_window(ddos),
        "samples": ddos[:5],
        "top_ips": by_ip.most_common(5)
    },
    "min_qty_rejects": {
        "count": len(minqty),
        "samples": minqty[:3]
    },
    "warn_err_by_minute": dict(sorted(warn_err_by_minute.items()))
}

print(tickets)
