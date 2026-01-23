import os
import httpx
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('HASHNODE_TOKEN')
use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
http_proxy = os.getenv('HTTP_PROXY')
https_proxy = os.getenv('HTTPS_PROXY')

proxies = None
if use_proxy and (http_proxy or https_proxy):
    proxies = {
        "http://": http_proxy,
        "https://": https_proxy
    }

query = """
query {
  me {
    publications(first: 10) {
      edges {
        node {
          id
          title
          domain
        }
      }
    }
  }
}
"""

print("正在查找 Hashnode Publication ID...")
try:
    response = httpx.post(
        "https://gql.hashnode.com",
        headers={
            "Authorization": token,
            "Content-Type": "application/json"
        },
        json={"query": query},
        proxies=proxies,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        if 'errors' in data:
            print(f"❌ 错误: {data['errors']}")
        else:
            pubs = data.get('data', {}).get('me', {}).get('publications', {}).get('edges', [])
            if not pubs:
                print("❌ 未在您的账号下找到任何 Publication。")
            else:
                print("✅ 找到以下 Publication:")
                for edge in pubs:
                    node = edge['node']
                    print(f"  - 标题: {node['title']}")
                    print(f"    ID: {node['id']}")
                    print(f"    域名: {node['domain']}")
                    print("-" * 20)
    else:
        print(f"❌ 错误: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ 异常: {e}")
