import os
import shutil
import sys
import subprocess
import random
import datetime
import json
import threading

from ruamel.yaml import YAML
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# 初始化 YAML 解析器
yaml = YAML()
yaml.preserve_quotes = True  # 保留引号


# 配置文件路径处理
def resource_path(relative_path, external=False):
    """ 获取资源文件路径，兼容开发和打包后的情况 """
    if external:
        # 外部资源文件的路径（与可执行文件同目录）
        return os.path.join(os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath('.'),
                            relative_path)
    else:
        # 内部资源文件路径（如 conf.yaml.default）
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base_path, relative_path)


# 检查并加载/更新配置文件
def load_or_create_config():
    # 外部配置文件路径
    config_file = resource_path('conf.yaml', external=True)
    # 默认配置文件路径 (打包后存在于 MEIPASS 临时目录中)
    default_config_file = resource_path('conf.yaml.default')

    # 如果默认配置文件不存在，抛出异常
    if not os.path.exists(default_config_file):
        raise FileNotFoundError(f"默认配置文件 '{default_config_file}' 不存在！")

    # 如果 conf.yaml 不存在，复制 conf.yaml.default
    if not os.path.exists(config_file):
        print(f"'{config_file}' 不存在，复制默认配置文件...")
        shutil.copy(default_config_file, config_file)

    # 读取默认配置
    with open(default_config_file, 'r') as default_file:
        default_conf = yaml.load(default_file)

    # 读取用户配置（如果存在）
    with open(config_file, 'r') as user_file:
        user_conf = yaml.load(user_file)

    merged_conf = merge_dicts(default_conf, user_conf)

    # 保存合并后的配置到 conf.yaml
    with open(config_file, 'w') as config_file_out:
        yaml.dump(merged_conf, config_file_out)

    return merged_conf


# 加载数据
def load_data():
    data_file = resource_path('data.json', external=True)  # 确保 data.json 位于外部目录
    if not os.path.exists(data_file):
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


# 保存数据
def save_data(data):
    data_file = resource_path('data.json', external=True)  # 确保保存到外部路径
    with open(data_file, 'w') as fileIO:
        json.dump(data, fileIO, indent=4)


# 以默认配置为基础，用用户配置更新字段
def merge_dicts(defaults, overrides):
    for key, value in overrides.items():
        if isinstance(value, dict) and key in defaults:
            merge_dicts(defaults[key], value)
        else:
            defaults[key] = value
    return defaults


# 测速函数
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


# 设置下一次运行时间
def set_next_run(data):
    next_run_interval = random.randint(conf['min_interval'], conf['max_interval']) * 60
    next_run = datetime.datetime.now() + datetime.timedelta(seconds=next_run_interval)
    data["next_run"] = next_run.strftime('%Y-%m-%d %H:%M:%S')


# 检查是否应该运行测速
def check_run():
    data = load_data()
    if data["next_run"]:
        next_run = datetime.datetime.strptime(data["next_run"], '%Y-%m-%d %H:%M:%S')
        if datetime.datetime.now() >= next_run:
            speed_test()
    else:
        speed_test()


# Flask 路由
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


# 定时任务
def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_run, 'interval', seconds=10)
    scheduler.start()


if __name__ == '__main__':
    # 加载配置
    conf = load_or_create_config()
    # 运行测速守护进程
    threading.Thread(target=run_scheduler).start()
    # 启动Flask
    app.run(host='0.0.0.0', debug=False, port=conf['port'])
