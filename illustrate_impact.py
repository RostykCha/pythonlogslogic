from helper import stream_entries
from collections import Counter

categories = Counter()
for e in stream_entries():
    if e["level"] == "ERROR" and "Timeout waiting for response" in e["msg"]:
        categories["timeouts"] += 1
    elif e["level"] == "WARN" and "Possible DDoS" in e["msg"]:
        categories["ddos_warn"] += 1
    elif e["level"] == "ERROR" and "getBannedData" in e["msg"]:
        categories["rate_limiter_bug"] += 1
    elif e["json"] and e["json"].get("code") == -1013:
        categories["min_qty_reject"] += 1

print(categories)
