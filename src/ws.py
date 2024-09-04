from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
import subprocess
import time

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template_string('''
        <h2>Progress Bar</h2>
        <div id="progress-bar-container" style="width: 100%; background-color: #e0e0e0;">
            <div id="progress-bar" style="width: 0%; height: 30px; background-color: #76c7c0;"></div>
        </div>
        <p id="progress-text">0%</p>

        <script src="//cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.0/socket.io.js"></script>
        <script>
            const socket = io();

            socket.on('progress', function(data) {
                const progressText = document.getElementById('progress-text');
                const progressBar = document.getElementById('progress-bar');

                progressText.textContent = data;
                const percentage = data.match(/(\d+)%/);
                if (percentage) {
                    progressBar.style.width = percentage[1] + '%';
                }
            });
        </script>
    ''')

@socketio.on('connect')
def handle_connect():
    def generate_progress():
        command = ["bash", "progress_script.sh"]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in process.stdout:
            socketio.emit('progress', line.decode('utf-8').strip())
            time.sleep(0.1)  # Adjust this for smoother updates

        process.wait()

    socketio.start_background_task(generate_progress)

if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=8888)
