from flask import Flask
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return "{'status': 'OK'}"

@app.route('/enqueue', methods=['GET'])
def enqueue():
    os.system('ls')
    return "executed!"

# docker compose exec worker /bin/sh -c 'python -c "from tasks import longjob; longjob.delay()"'
