# 保存为 api_weight_monitor.py
# for binance
import time
import requests
import csv
from datetime import datetime

LOG_FILE = "api_weight_log.csv"

# 初始化日志文件
with open(LOG_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    if f.tell() == 0:  # 空文件时写入标题
        writer.writerow(["timestamp", "weight"])

print(f"监控Binance API权重使用情况，日志保存在: {LOG_FILE}")
print("按 Ctrl+C 停止监控...")

try:
    while True:
        # 获取API权重
        response = requests.head("https://api.binance.com/api/v3/ping")
        weight = response.headers.get("x-mbx-used-weight-1m", "0")

        # 记录日志
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, weight])

        print(f"[{timestamp}] API权重使用: {weight}/1200")

        # 简单预警
        if int(weight) > 1000:
            print("! 警告: API权重使用超过1000 !")

        time.sleep(60)  # 每分钟检查一次

except KeyboardInterrupt:
    print("\n监控已停止")
