from helper import stream_entries

orders = []
for e in stream_entries():
    if e["method"] == "POST" and e["path"] == "/api/v3/order" and e["json"]:
        orders.append({
            "time": e["dt"].isoformat() if e["dt"] else None,
            "acct": e["acct"],
            "ip": e["ip"],
            "orderId": e["json"].get("orderId"),
            "clientOrderId": e["json"].get("clientOrderId"),
            "status": e["json"].get("status"),
            "origQty": e["json"].get("origQty"),
            "executedQty": e["json"].get("executedQty"),
            "fills": e["json"].get("fills")
        })

for o in orders[:5]:
    print(o)
