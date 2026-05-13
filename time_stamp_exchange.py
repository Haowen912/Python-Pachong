import re
from datetime import datetime

def convert_dotnet_date(date_str):
    # 转换 .NET /Date(1599031347000+0800)/ 格式为标准时间

    # 1. 正则提取 毫秒时间戳 和 时区
    match = re.match(r'/Date\((\d+)([+-]\d+)\)/', date_str)
    if not match:
        return "格式错误"

    # 2. 获取毫秒时间戳（转成秒：Python 时间戳单位是秒）
    timestamp_ms = int(match.group(1))
    timestamp = timestamp_ms / 1000  # 关键：毫秒 → 秒

    # 3. 转换为本地时间 / UTC 时间
    utc_time = datetime.utcfromtimestamp(timestamp)  # UTC时间
    local_time = datetime.fromtimestamp(timestamp)  # 本地时间（你的系统时区）

    return {
        "原始字符串": date_str,
        "毫秒时间戳": timestamp_ms,
        "秒时间戳": timestamp,
        "UTC时间": utc_time.strftime('%Y-%m-%d %H:%M:%S'),
        "本地时间": local_time.strftime('%Y-%m-%d %H:%M:%S')
    }


# 测试
dotnet_date = "/Date(1599031347000+0800)/"
result = convert_dotnet_date(dotnet_date)
for k, v in result.items():
    print(f"{k}: {v}")
