from helper import orders_per_second, stream_entries

ops = orders_per_second()
print("peak second:", max(ops, key=ops.get), "->", max(ops.values()))

# manual verify: print all order lines from that second
peak_time = max(ops, key=ops.get)
for e in stream_entries():
    if e["dt"] and e["dt"].replace(microsecond=0) == peak_time and e["path"] == "/api/v3/order":
        print(e["dt"], e["acct"], e["json"].get("orderId"))
