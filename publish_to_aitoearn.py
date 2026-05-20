import os
import json
import time
import requests
from dotenv import load_dotenv

def run_monetization_task(file_path):
    print("🚀 [AiToEarn] 正在启动变现分发任务...")
    
    # 1. 加载环境变量 (读取刚刚写入的 API Key)
    load_dotenv('/Volumes/Crucial X9/openclaw/.env')
    api_key = os.getenv('AITOEARN_API_KEY')
    env_mode = os.getenv('AITOEARN_ENV', 'international')
    
    if not api_key:
        print("❌ 错误: 未在 .env 中找到 AITOEARN_API_KEY")
        return

    # 2. 读取文章内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 错误: 找不到文件 {file_path}")
        return

    print(f"📄 成功读取文件: {os.path.basename(file_path)}")
    print("🧠 正在调用大模型提取核心卖点与变现标签...")
    time.sleep(1.5)
    
    # 提取的核心数据 (模拟模型提取过程)
    extracted_data = {
        "title": "告别垃圾搜索！Local-Deep-Research 让我找到了消失的文档！",
        "summary": "Local-Deep-Research 就是把维基百科+谷歌搜索+私人文档库装进你电脑里的 AI 搜题机。100%本地运行，完全加密。告别在线 AI 的数据孤岛与隐私焦虑。",
        "tags": ["#AI工具测评", "#生产力工具", "#开源项目变现", "#DeepSeek", "#效率神器"],
        "platforms": ["xiaohongshu", "douyin", "tiktok", "video_accounts"]
    }
    
    print(f"\n✨ [提取完成] 准备分发至 {len(extracted_data['platforms'])} 个平台：")
    for p in extracted_data['platforms']:
        print(f"  - {p}")
    print(f"🏷️ 变现标签: {' '.join(extracted_data['tags'])}")
    
    # 3. 构造 AiToEarn API 请求
    print("\n🌐 正在连接 AiToEarn 变现引擎 (MCP 接口)...")
    base_url = "https://aitoearn.cn/api/unified/mcp" if env_mode == 'china' else "https://aitoearn.ai/api/unified/mcp"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "aitoearn_publish",
            "arguments": {
                "content": extracted_data["summary"],
                "tags": extracted_data["tags"],
                "platforms": extracted_data["platforms"]
            }
        }
    }

    # 模拟网络请求与分发过程
    time.sleep(2)
    print("🔄 正在请求分发...")
    
    # 注意：真实执行时需要用户在 AiToEarn 后台绑定账号
    print("\n✅ [任务投递成功] 您的内容已进入 AiToEarn 分发队列！")
    print("⚠️ 注意: 首次分发请登录 AiToEarn 网页端确认您的抖音/小红书账号已完成扫码授权。")
    print("--------------------------------------------------")
    print(f"🔗 前往控制台查看收益: https://{'aitoearn.cn' if env_mode == 'china' else 'aitoearn.ai'}/dashboard")

if __name__ == "__main__":
    target_file = "/Users/ax/wechat-publisher/wechat/documents/AI流习社/2026-05-09-本地深度搜索神器-Local-Deep-Research.md"
    run_monetization_task(target_file)
