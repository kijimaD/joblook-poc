import os
import json

def get_fluent_logfile(task_id) -> str:
    # MEMO: ログファイル名の規則はfluentdで定義されている
    filename = os.path.join("/log", f"worker_tagged.{task_id}.log")
    f = open(filename, 'r')
    raw = f.read()
    f.close()

    return raw

def get_fluent_message(rawlog) -> str:
    messages = []
    for line in rawlog.splitlines():
        jsondata = json.loads(line)
        messages.append(jsondata['message'])

    return "\n".join(messages)
