from helper import stream_entries
from collections import defaultdict, Counter

by_minute = defaultdict(lambda: {"ERROR":0,"WARN":0})
timeout_lines = []
ddos_lines = []
ip_counter = Counter()
acct_counter = Counter()

for e in stream_entries():
    if e["dt"]:
        minute = e["dt"].replace(second=0, microsecond=0)
        if e["level"] in ("ERROR","WARN"):
            by_minute[minute][e["level"]] += 1
        msg = e["msg"]
        if msg and "Timeout waiting for response from backend" in msg:
            timeout_lines.append((e["dt"], e["logger"].strip(), e["msg"]))
        if msg and "Possible DDoS" in msg or ("BANNED until" in msg):
            ddos_lines.append((e["dt"], e["msg"]))
    if e["ip"]:
        ip_counter[e["ip"]] += 1
    if e["acct"]:
        acct_counter[e["acct"]] += 1

print("errors/warns per minute:")
for k in sorted(by_minute):
    print(k, by_minute[k])

print("\ntimeout samples (first 5):")
for row in timeout_lines[:5]:
    print(row)

print("\nddos samples (first 5):")
for row in ddos_lines[:5]:
    print(row)

print("\ntop ips:")
for ip, cnt in ip_counter.most_common(5):
    print(ip, cnt)

print("\ntop accounts:")
for acct, cnt in acct_counter.most_common(5):
    print(acct, cnt)
