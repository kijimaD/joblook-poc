from tasks import run
from utils import get_fluent_logfile, get_fluent_message
from flask import Flask, request, jsonify, render_template_string, Response
from flask_socketio import SocketIO, emit
import os
import json
import requests

app = Flask(__name__)
socketio = SocketIO(app)

# @app.before_request
# def log_request_info():
#     app.logger.debug('Headers: %s', request.headers)
#     app.logger.debug('Body: %s', request.get_data())

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "OK",
    })

@app.route('/tasks', methods=['GET'])
def tasks():
    return render_template_string('''
        <h2>Tasks</h2>
        <ul id="task-list"></ul>

        <script>
            const taskList = document.getElementById('task-list');
            fetch('/flower/api/tasks') // リバースプロキシURL
              .then((response) => {
                return response.json()
              })
              .then((data) => {
                Object.keys(data).forEach((key) => {
                  uuid = data[key]['uuid'];
                  state = data[key]['state'];
                  args = data[key]['args'];
                  timestamp = data[key]['timestamp'];
                  dateTime = new Date(timestamp * 1000);
                  dateString = dateTime.toLocaleDateString('ja-JP')
                  timeString = dateTime.toLocaleTimeString('ja-JP')
                  taskList.innerHTML += "<table><tbody>"
                  taskList.innerHTML += `
                  <tr>
                    <td><code>${state}<code></td>
                    <td><code>${dateString} ${timeString}<code></td>
                    <td><code><a href="/task?task_id=${uuid}">${uuid}</a><code></td>
                    <td><code>${args}<code></td>
                  </tr>
                  `;
                  taskList.innerHTML += "</tbody></table>"
                })
              })
              .catch(error => {
                console.error(error);
              });
        </script>
    ''')

@app.route('/task', methods=['GET'])
def task():
    req = request.args
    task_id = req.get("task_id")
    if task_id is None:
            return jsonify({'message': 'parameter `task_id` is required!'}, 400)
    rawlog = get_fluent_logfile(task_id)
    initial_msg = get_fluent_message(rawlog)

    return render_template_string('''
        <a id="flower-url">{{ task_id }}</a>
        <pre id="progress-text" style="background-color: black; color: white; height: 90%; width: 90%;overflow: scroll;padding: 1em;">{{ initial_msg }}<br></pre>

        <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
        <script>
            const flowerURL = document.getElementById('flower-url');
            flowerURL.href = `http://${location.hostname}:5555/task/{{ task_id }}`;

            const progressText = document.getElementById('progress-text');
            const socket = io();
            socket.on("{{ task_id }}", function(data) {
                progressText.innerHTML += data + "<br>";
                progressText.scrollTop = progressText.scrollHeight;
            });
        </script>
    ''', task_id=task_id, initial_msg=initial_msg)

# タスク投入エンドポイント
@app.route('/enqueue', methods=['POST'])
def enqueue():
    cmd = ""

    try:
      json = request.get_json()
      cmd = json['cmd']
    except Exception as e:
      return jsonify({'message': f"parameter invalid {e}"}), 400

    result = run.delay(cmd)
    return jsonify({'task_id': result.id})

# 永続ログ取得エンドポイント
# 返り値はJSONではない
@app.route('/permlog', methods=['GET'])
def permlog():
    req = request.args
    task_id = req.get("task_id")
    rawlog = get_fluent_logfile(task_id)

    return get_fluent_message(rawlog)

# ログ受信およびブロードキャストエンドポイント
# syncエンドポイントには、すべてのタスクIDが送られてくる。IDごとのチャンネルに送信する
@app.route('/sync', methods=['POST'])
def sync():
    raw = request.data.decode('utf-8')
    # 1行1行送るので非効率だが、こうしないと複数のタスクを実行したときに混じって送信してしまう
    for line in raw.splitlines():
        try:
            jsondata = json.loads(line)
            task_id = jsondata['task_id']
            socketio.emit(task_id, jsondata['message'])
        except json.JSONDecodeError:
            print(f"Invalid JSON format: {line.strip()}")

    return jsonify({'status': 'OK'})

@app.route('/flower/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
def flower_proxy(path):
    BACKEND_URL = 'http://flower:5555'
    # フロントエンドサーバーから受け取ったリクエストをそのままflowerに転送
    url = f"{BACKEND_URL}/{path}"

    # クライアントのリクエストに基づいてバックエンドにリクエストを送る
    if request.method == "GET":
        resp = requests.get(url, headers=request.headers, params=request.args)
    elif request.method == "POST":
        resp = requests.post(url, headers=request.headers, json=request.get_json())
    elif request.method == "PUT":
        resp = requests.put(url, headers=request.headers, json=request.get_json())
    elif request.method == "DELETE":
        resp = requests.delete(url, headers=request.headers)
    else:
        return Response("Method not supported", status=405)

    # バックエンドのレスポンスをそのままクライアントに返す
    return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))

@socketio.on('connect')
def handle_connect():
    print("connect...")

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=8888, allow_unsafe_werkzeug=True)
