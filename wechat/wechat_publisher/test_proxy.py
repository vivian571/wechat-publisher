import os
import requests

print("=" * 60)
print("代理连接测试")
print("=" * 60)
print()

# 检查环境变量
print("【1】环境变量检查")
print("-" * 60)
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy']
for var in proxy_vars:
    value = os.environ.get(var)
    if value:
        print(f"  ✓ {var} = {value}")
    else:
        print(f"  ✗ {var} = (未设置)")
print()

# 测试常见代理端口
print("【2】代理端口测试")
print("-" * 60)
common_proxies = [
    "http://127.0.0.1:7890",  # Clash
    "http://127.0.0.1:10809", # V2Ray
    "http://127.0.0.1:1080",  # Shadowsocks
]

for proxy_url in common_proxies:
    try:
        session = requests.Session()
        session.proxies = {'http': proxy_url, 'https': proxy_url}
        response = session.get('http://www.google.com', timeout=5)
        print(f"  ✓ {proxy_url} - 可用 (状态码: {response.status_code})")
    except requests.exceptions.ProxyError as e:
        print(f"  ✗ {proxy_url} - 代理错误: {str(e)[:50]}...")
    except requests.exceptions.Timeout:
        print(f"  ✗ {proxy_url} - 超时")
    except Exception as e:
        print(f"  ✗ {proxy_url} - 其他错误: {str(e)[:50]}...")
print()

# 测试直连
print("【3】直连测试（不使用代理）")
print("-" * 60)
try:
    session = requests.Session()
    session.proxies = {'http': None, 'https': None}
    session.trust_env = False
    response = session.get('http://www.baidu.com', timeout=5)
    print(f"  ✓ 直连可用 (状态码: {response.status_code})")
except Exception as e:
    print(f"  ✗ 直连失败: {e}")
print()

# 测试 GitHub
print("【4】GitHub 访问测试")
print("-" * 60)
test_urls = [
    'https://github.com',
    'https://api.github.com',
    'https://opengraph.githubassets.com',
]

for url in test_urls:
    # 尝试使用系统代理
    try:
        session = requests.Session()
        session.trust_env = True  # 使用系统代理
        response = session.head(url, timeout=10)
        print(f"  ✓ {url} - 可访问 (状态码: {response.status_code})")
    except requests.exceptions.ProxyError as e:
        print(f"  ✗ {url} - 代理错误")
        # 尝试直连
        try:
            session2 = requests.Session()
            session2.proxies = {'http': None, 'https': None}
            session2.trust_env = False
            response2 = session2.head(url, timeout=10)
            print(f"     但直连可用 (状态码: {response2.status_code})")
        except:
            print(f"     直连也失败")
    except Exception as e:
        print(f"  ✗ {url} - 错误: {str(e)[:50]}...")
print()

print("=" * 60)
print("测试完成")
print("=" * 60)
