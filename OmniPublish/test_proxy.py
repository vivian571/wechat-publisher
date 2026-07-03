"""测试代理配置"""
import os
from dotenv import load_dotenv
import httpx

# 加载环境变量
load_dotenv()

# 读取代理配置
use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
http_proxy = os.getenv('HTTP_PROXY')
https_proxy = os.getenv('HTTPS_PROXY')

print("=" * 60)
print("代理配置检查")
print("=" * 60)
print(f"USE_PROXY: {use_proxy}")
print(f"HTTP_PROXY: {http_proxy}")
print(f"HTTPS_PROXY: {https_proxy}")
print()

if use_proxy and (http_proxy or https_proxy):
    proxies = {
        "http://": http_proxy,
        "https://": https_proxy
    }
    print("✅ 代理已启用")
    print(f"代理配置: {proxies}")
    print()
    
    # 测试连接
    print("测试连接到 Dev.to API...")
    try:
        response = httpx.get(
            "https://dev.to/api/articles",
            proxies=proxies,
            timeout=10
        )
        print(f"✅ 连接成功! 状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
else:
    print("⚠️ 代理未启用或未配置")
    print()
    print("请在 .env 文件中添加以下配置:")
    print("USE_PROXY=true")
    print("HTTP_PROXY=http://127.0.0.1:3067")
    print("HTTPS_PROXY=http://127.0.0.1:3067")
