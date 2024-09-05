from flask import Flask
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return "{'status': 'OK'}"

@app.route('/exec', methods=['GET'])
def exec():
    os.system('ls')
    return "executed!"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8888)
