from tasks import run
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit
import os
import json

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/', methods=['GET'])
def root():
    data = {
        "status": "OK",
    }
    return jsonify(data)

@app.route('/front')
def index():
    return render_template_string('''
        <h2>Log</h2><span>task_id: </span><span id="task-id"></span>
        <pre id="progress-text" style="background-color: black; color: white; height: 60%; width: 100%;"></pre>

        <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
        <script>
            const url = new URL(window.location.href);
            task_id = url.searchParams.get('task_id');
            const taskID = document.getElementById('task-id');
            taskID.textContent = task_id;

            const progressText = document.getElementById('progress-text');

            fetch('http://localhost:8888/permlog?task_id='+task_id)
              .then(response => {
                // 行ごとのJSONなので、全体としては普通の文字列
                return response.text()
              })
              .then(data => {
                progressText.innerHTML = data + "<br>";
              })
              .catch(error => {
                console.error(error);
              });

            const socket = io();
            socket.on(task_id, function(data) {
                progressText.innerHTML += data + "<br>";
            });
        </script>
    ''')

# タスク投入エンドポイント
@app.route('/enqueue', methods=['POST'])
def enqueue():
    json = request.get_json()
    cmd = json['cmd']

    result = run.delay(cmd)
    return jsonify({'task_id': result.id})

# 永続ログ取得エンドポイント
@app.route('/permlog', methods=['GET'])
def permlog():
    req = request.args
    task_id = req.get("task_id")

    # MEMO: ログファイル名の規則はfluentdで定義されている
    filename = os.path.join("/log", f"worker_tagged.{task_id}.log")
    f = open(filename, 'r')
    raw = f.read()
    f.close()

    messages = []
    for line in raw.splitlines():
        try:
            jsondata = json.loads(line)
            messages.append(jsondata['message'])
        except json.JSONDecodeError:
            print(f"Invalid JSON format: {line.strip()}")

    return "\n".join(messages)

@app.route('/sync', methods=['POST'])
def sync():
    json = request.get_json()
    log = json['log']
    task_id = json['task_id']

    socketio.emit(task_id, log)

    return jsonify({'status': 'OK'})

@socketio.on('connect')
def handle_connect():
    print("connect...")

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=8888, allow_unsafe_werkzeug=True)
