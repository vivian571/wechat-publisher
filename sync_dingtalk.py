
import json
import os
from pathlib import Path

# 1. 配置路径
config_path = Path.home() / ".clawdbot" / "moltbot.json"
config_dir = Path.home() / ".clawdbot"

# 2. 填入你的 Client 凭证 (从钉钉开发者后台获取)
DINGTALK_CLIENT_ID = "dingfjlbnem5o7joxfyz"
DINGTALK_CLIENT_SECRET = "L9urC5ZGtkV0XJ6nOkOVDB1KeA3mkfXq_QucDxhSYFFkLRKftuPrs-ecY6rwPJnm"

def sync_dingtalk_config():
    # 确保目录存在
    if not config_dir.exists():
        config_dir.mkdir(parents=True)
        print(f"📁 已创建配置目录: {config_dir}")

    # 读取现有配置
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
    else:
        config = {}

    # 初始化 channels 结构
    if "channels" not in config:
        config["channels"] = {}
    
    # 3. 执行“外科手术式”精准更新
    # 这种写法即使你之前有旧字段，也会被新的逻辑完美覆盖
    config["channels"]["dingtalk"] = {
        "enabled": True,
        "client_id": DINGTALK_CLIENT_ID,
        "client_secret": DINGTALK_CLIENT_SECRET,
        "sync_skills": True,
        "mode": "websocket",  # 推荐使用 WebSocket 模式，免公网 IP 回调
        "description": "Yi An's Hardcore Agent (M4 Power)"
    }

    # 4. 写回文件
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("-" * 30)
    print("✅ 同步成功！Client ID 已注入。")
    print(f"📍 配置文件地址: {config_path}")
    print("-" * 30)
    print("💡 接下来：重启 Moltbot，并在钉钉后台开启‘机器人消息回调’。")

if __name__ == "__main__":
    sync_dingtalk_config()
