# api_weight_monitor_optimized.py
import time
import requests
import csv
import certifi
import ssl
from datetime import datetime
from urllib3.util.ssl_ import create_urllib3_context

LOG_FILE = "api_weight_log.csv"

# 初始化日志文件
with open(LOG_FILE, "a", newline="") as f:
    writer = csv.writer(f)
    if f.tell() == 0:
        writer.writerow(["timestamp", "weight", "status"])

print(f"监控Binance API权重使用情况，日志保存在: {LOG_FILE}")
print("按 Ctrl+C 停止监控...")

# 创建SSL上下文
ctx = create_urllib3_context()
ctx.minimum_version = ssl.TLSVersion.TLSv1_2  # 强制TLSv1.2+
ctx.load_verify_locations(certifi.where())     # 加载最新CA证书

# 自定义适配器类
class CustomHTTPAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        kwargs["ssl_context"] = ctx
        return super().init_poolmanager(*args, **kwargs)

# 创建会话并挂载适配器
session = requests.Session()
adapter = CustomHTTPAdapter(max_retries=3)
session.mount("https://", adapter)
session.verify = certifi.where()  # 启用证书验证

try:
    while True:
        try:
            # 发送请求（不再传递ssl_context参数）
            response = session.head(
                "https://api.binance.com/api/v3/ping",
                timeout=10,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            weight = response.headers.get("x-mbx-used-weight-1m", "0")
            status = "success"
        except Exception as e:
            weight = "error"
            status = str(e)
            print(f"请求失败: {str(e)}")

        # 记录日志（与原逻辑一致）
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, weight, status])

        if status == "success":
            print(f"[{timestamp}] API权重使用: {weight}/1200")
            if int(weight) > 1000:
                print("! 警告: API权重使用超过1000 !")
        else:
            print(f"[{timestamp}] 错误: {status}")

        time.sleep(60)

except KeyboardInterrupt:
    print("\n监控已停止")
