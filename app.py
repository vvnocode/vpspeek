import datetime
import yaml
import json
import os
import random
import subprocess
import threading

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# File and key to store speed test results and the next run time
data_file = 'data.json'

# Load configurations from conf.yaml
with open('conf.yaml', 'r') as file:
    conf = yaml.safe_load(file)


def load_data():
    if not os.path.exists(data_file):
        # If the file does not exist, create an initial structure
        data = {"results": [], "next_run": None}
        save_data(data)
    else:
        try:
            with open(data_file, 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = {"results": [], "next_run": None}
            save_data(data)
    return data


def save_data(data):
    with open(data_file, 'w') as fileIO:
        json.dump(data, fileIO, indent=4)


def speed_test(triggered_by="auto"):
    result = subprocess.run(
        ["curl", "-o", "/dev/null", "-s", "-w", "%{size_download} %{time_total} %{speed_download}\n",
         conf['speedtest_url']],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("Speed test failed.")
        return

    size_download, time_total, speed_download = result.stdout.strip().split()
    size_download = float(size_download) / (1024 * 1024)  # 转换为 MB
    time_total = float(time_total)  # 下载总用时
    speed_download = (float(speed_download) * 8) / (1024 * 1024)  # 转换为 Mbps

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_result = {
        "timestamp": timestamp,
        "file_size_MB": round(size_download, 2),
        "time_seconds": round(time_total, 2),
        "speed_Mbps": round(speed_download, 2),
        "triggered_by": triggered_by
    }

    data = load_data()
    data["results"].append(new_result)
    set_next_run(data)
    save_data(data)


def set_next_run(data):
    next_run_interval = random.randint(conf['min_interval'], conf['max_interval']) * 60
    next_run = datetime.datetime.now() + datetime.timedelta(seconds=next_run_interval)
    data["next_run"] = next_run.strftime('%Y-%m-%d %H:%M:%S')


def check_run():
    data = load_data()
    if data["next_run"]:
        next_run = datetime.datetime.strptime(data["next_run"], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() >= next_run:
            speed_test()
    else:
        # If next_run is None, trigger the speed test immediately
        speed_test()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/config', methods=['GET'])
def get_config():
    return jsonify(conf)


@app.route('/speeds', methods=['GET'])
def get_speeds():
    sort_key = request.args.get('sort_by', 'timestamp')
    sort_order = request.args.get('sort_order', 'desc')
    data = load_data()
    results = sorted(data['results'], key=lambda x: x.get(sort_key, 'timestamp'), reverse=sort_order == 'desc')
    return jsonify(results)


@app.route('/trigger_speed_test', methods=['GET'])
def trigger_speed_test():
    speed_test(triggered_by="manual")
    return jsonify({"message": "Speed test initiated"}), 202


def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_run, 'interval', seconds=10)  # Check every 10 seconds if it's time to run the speed test
    scheduler.start()


if __name__ == '__main__':
    threading.Thread(target=run_scheduler).start()
    app.run(host='0.0.0.0', debug=False, port=conf['port'])
