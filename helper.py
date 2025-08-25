import re, json
from datetime import datetime
from collections import defaultdict

LOG_PATH = "data/QA-Pre-Interview-Assignment.log"

HEADER_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\[(?P<epoch>\d+)\]\s*\|\s*(?P<level>[A-Z]+)\s*\|\s*(?P<thread>[^|]+)\|\s*(?P<logger>[^-]+)-\s*(?P<msg>.*)$"
)

IP_RE = re.compile(r"\[FROM\]: \[(?P<ip>[\d\.]+)\]")
ACCT_RE = re.compile(r"\[ACCT\]:\s*(?P<acct>\d+\|\d+)")
HTTP_RE = re.compile(r"httpStatus:(?P<status>\d+)")
RESP_RE = re.compile(r"\[RESP\]:\s*(?P<resp>\d+/\d+)")
API_RE = re.compile(r"\b(POST|GET|DELETE|PUT)\s+(?P<path>/\S+)")

def iter_lines(path=LOG_PATH):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            yield line.rstrip("\n")

def parse_line(line: str):
    m = HEADER_RE.match(line)
    if not m:
        return None
    d = m.groupdict()
    try:
        d["dt"] = datetime.strptime(d["ts"], "%Y-%m-%d %H:%M:%S.%f")
    except:
        d["dt"] = None

    # light-weight extractions
    d["ip"] = (IP_RE.search(line).group("ip") if IP_RE.search(line) else None)
    d["acct"] = (ACCT_RE.search(line).group("acct") if ACCT_RE.search(line) else None)
    d["httpStatus"] = int(HTTP_RE.search(line).group("status")) if HTTP_RE.search(line) else None
    d["resp"] = (RESP_RE.search(line).group("resp") if RESP_RE.search(line) else None
    )
    api = API_RE.search(line)
    d["method"] = api.group(1) if api else None
    d["path"] = api.group("path") if api else None

    # try to capture trailing JSON (order responses etc.)
    jstart = line.find("{")
    jend = line.rfind("}")
    payload = None
    if jstart != -1 and jend != -1 and jend > jstart:
        raw = line[jstart : jend + 1]
        try:
            payload = json.loads(raw)
        except:
            payload = None
    d["json"] = payload
    return d

def stream_entries():
    for line in iter_lines():
        e = parse_line(line)
        if e:
            yield e

# Common helpers
def count_by_level(level: str):
    level = level.upper()
    c = 0
    for e in stream_entries():
        if e["level"] == level:
            c += 1
    return c

def warnings_count():
    return count_by_level("WARN")

def unique_error_loggers():
    s = set()
    for e in stream_entries():
        if e["level"] == "ERROR":
            s.add(e["logger"].strip())
    return sorted(s)

def orders_per_second():
    bucket = defaultdict(int)
    for e in stream_entries():
        if e["method"] == "POST" and e["path"] == "/api/v3/order" and e["dt"]:
            key = e["dt"].replace(microsecond=0)
            bucket[key] += 1
    return dict(sorted(bucket.items()))

def trades_for_account(acct: str):
    trades = []
    for e in stream_entries():
        if e["acct"] == acct and e["json"] and "fills" in e["json"] and e["json"]["fills"]:
            trades.append({
                "time": e["dt"].isoformat() if e["dt"] else None,
                "orderId": e["json"].get("orderId"),
                "clientOrderId": e["json"].get("clientOrderId"),
                "status": e["json"].get("status"),
                "fills": e["json"]["fills"]
            })
    return trades

def errors_summary():
    bucket = defaultdict(int)
    for e in stream_entries():
        if e["level"] == "ERROR":
            bucket[e["logger"].strip()] += 1
    return dict(sorted(bucket.items(), key=lambda x: x[1], reverse=True))
