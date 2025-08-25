from helper import stream_entries

issues = []
for e in stream_entries():
    if e["level"] in ("ERROR","WARN"):
        issues.append(e["msg"])
for i in issues[:10]:
    print(i)