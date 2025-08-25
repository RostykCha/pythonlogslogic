from helper import stream_entries

levels = {e["level"] for e in stream_entries()}
print(levels)