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

# 先获取用户名
me_query = """
query {
  me {
    username
  }
}
"""

try:
    print("获取用户信息...")
    me_resp = httpx.post(
        "https://gql.hashnode.com",
        headers={"Authorization": token, "Content-Type": "application/json"},
        json={"query": me_query},
        proxies=proxies,
        timeout=10
    )
    me_data = me_resp.json()
    username = me_data.get('data', {}).get('me', {}).get('username')
    
    if not username:
        print("❌ 无法获取用户名，请检查 Token。")
        exit(1)
        
    print(f"✅ 用户名: {username}")

    # 获取 Publication
    pub_query = """
    query {
      user(username: "%s") {
        publications(first: 5) {
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
    """ % username

    print("查询 Publications...")
    pub_resp = httpx.post(
        "https://gql.hashnode.com",
        headers={"Authorization": token, "Content-Type": "application/json"},
        json={"query": pub_query},
        proxies=proxies,
        timeout=10
    )
    
    pub_data = pub_resp.json()
    if 'errors' in pub_data:
        print(f"❌ 错误: {pub_data['errors']}")
    else:
        pubs = pub_data.get('data', {}).get('user', {}).get('publications', {}).get('edges', [])
        if not pubs:
            print("❌ 未找到任何 Publication。")
        else:
            print("✅ 找到以下 Publication ID:")
            for edge in pubs:
                node = edge['node']
                print(f"  - {node['title']} ({node['domain']}): {node['id']}")
                
except Exception as e:
    print(f"❌ 异常: {e}")
