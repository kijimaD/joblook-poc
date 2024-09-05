from tasks import run
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    data = {
        "status": "OK",
    }
    return jsonify(data)

@app.route('/enqueue', methods=['POST'])
def enqueue():
    json = request.get_json()
    cmd = json['cmd']
    result = run.delay(cmd)
    data = {
        "task_id": result.id,
    }
    return jsonify(data)
