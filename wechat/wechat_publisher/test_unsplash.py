import os
import requests
from dotenv import load_dotenv

print("=" * 60)
print("Unsplash API 测试")
print("=" * 60)
print()

# 加载环境变量
load_dotenv()

access_key = os.getenv('UNSPLASH_ACCESS_KEY')

if not access_key or access_key == '你的访问密钥':
    print("❌ 错误: 未配置 UNSPLASH_ACCESS_KEY")
    print()
    print("请在 .env 文件中添加:")
    print("UNSPLASH_ACCESS_KEY=你的实际访问密钥")
    exit(1)

print(f"✓ 已加载 Access Key: {access_key[:10]}...")
print()

# 测试 API 连接
print("【1】测试 API 连接")
print("-" * 60)

try:
    api_url = "https://api.unsplash.com/search/photos"
    headers = {
        'Authorization': f'Client-ID {access_key}',
        'Accept-Version': 'v1'
    }
    params = {
        'query': 'technology',
        'per_page': 3,
        'orientation': 'landscape'
    }
    
    response = requests.get(api_url, headers=headers, params=params, timeout=10)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        results = data.get('results', [])
        
        print(f"✓ API 连接成功!")
        print(f"  找到 {total} 张相关图片")
        print()
        
        if results:
            print("【2】图片示例")
            print("-" * 60)
            for i, photo in enumerate(results[:3], 1):
                print(f"\n图片 {i}:")
                print(f"  ID: {photo['id']}")
                print(f"  描述: {photo.get('description') or photo.get('alt_description') or '无描述'}")
                print(f"  作者: {photo['user']['name']}")
                print(f"  Regular URL: {photo['urls']['regular']}")
                print(f"  Small URL: {photo['urls']['small']}")
        
        # 检查 API 限制
        print()
        print("【3】API 使用情况")
        print("-" * 60)
        rate_limit = response.headers.get('X-Ratelimit-Limit', 'N/A')
        rate_remaining = response.headers.get('X-Ratelimit-Remaining', 'N/A')
        print(f"  每小时限制: {rate_limit} 次")
        print(f"  剩余次数: {rate_remaining} 次")
        
    elif response.status_code == 401:
        print("❌ 认证失败!")
        print("  请检查 UNSPLASH_ACCESS_KEY 是否正确")
        print(f"  当前值: {access_key[:10]}...")
    elif response.status_code == 403:
        print("❌ 访问被拒绝!")
        print("  可能原因:")
        print("  1. API 配额已用完")
        print("  2. Access Key 权限不足")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        print(f"  响应: {response.text}")
        
except requests.RequestException as e:
    print(f"❌ 网络错误: {e}")
except Exception as e:
    print(f"❌ 未知错误: {e}")

print()
print("=" * 60)
print("测试完成")
print("=" * 60)
