from flask import Flask
from tasks import run

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return "{'status': 'OK'}"

@app.route('/enqueue', methods=['GET'])
def enqueue():
    run.delay("ls")

    return "enqueued!"
