from helper import stream_entries
import re
patterns = {
    "http_api": re.compile(r"\b(POST|GET|PUT|DELETE)\s+/api/"),
    "amqp_rabbitmq": re.compile(r"\bRmq(Send|Recv)NetworkConnector\b"),
    "gzip": re.compile(r"\bgzip\b"),
    "json_body": re.compile(r"\{.*\}"),
}
counts = {k: 0 for k in patterns}
examples = {k: [] for k in patterns}
for e in stream_entries():
    line = f"{e['ts']}|{e['level']}|{e['thread']}|{e['logger']} - {e['msg']}"
    for k, rx in patterns.items():
        if rx.search(line):
            counts[k] += 1
            if len(examples[k]) < 3:
                examples[k].append(line[:240])
summary = {
    "protocols_detected": {
        "http_https_rest": counts["http_api"] > 0,
        "amqp_rabbitmq": counts["amqp_rabbitmq"] > 0,
        "json_over_http": counts["json_body"] > 0 and counts["http_api"] > 0,
        "gzip_response": counts["gzip"] > 0
    },
    "counts": counts,
    "examples": examples
}
print(str(summary))
