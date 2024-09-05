from tasks import run
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    data = {
        "status": "OK",
    }
    return jsonify(data)

# タスク投入エンドポイント
@app.route('/enqueue', methods=['POST'])
def enqueue():
    json = request.get_json()
    cmd = json['cmd']

    result = run.delay(cmd)
    data = {
        "task_id": result.id,
    }
    return jsonify(data)

# 永続ログ取得エンドポイント
@app.route('/permlog', methods=['GET'])
def permlog():
    req = request.args
    task_id = req.get("task_id")

    # MEMO: ログファイル名の規則はfluentdで定義されている
    filename = os.path.join("/log", f"worker_tagged.{task_id}.log")
    f = open(filename, 'r')
    log = f.read()
    f.close()

    return log
