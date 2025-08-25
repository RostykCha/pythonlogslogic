from helper import orders_per_second, warnings_count, errors_summary

ops = orders_per_second()
print("avg orders/sec:", sum(ops.values())/len(ops))
print("peak orders/sec:", max(ops.values()))
print("warnings:", warnings_count())
print("errors by logger:", errors_summary())
