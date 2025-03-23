from flask import Flask, render_template, request, jsonify
import datetime

app = Flask(__name__)

alarm_status = False
logs = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle-alarm', methods=['POST'])
def toggle_alarm():
    global alarm_status
    alarm_status = not alarm_status
    status = "activated" if alarm_status else "deactivated"
    logs.append(f"{datetime.datetime.now()}: Alarm {status}")
    return jsonify({"message": f"Alarm {status}!"})

@app.route('/logs')
def get_logs():
    return jsonify({"logs": logs[-10:]})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)