import os
import httpx
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('HASHNODE_TOKEN')
use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
# ... (proxies part)
proxies = None
if use_proxy:
    proxies = {"http://": os.getenv('HTTP_PROXY'), "https://": os.getenv('HTTPS_PROXY')}

pub_query = """
query {
  user(username: "xuanwu274") {
    publications(first: 5) {
      edges {
        node {
          id
          title
        }
      }
    }
  }
}
"""

try:
    resp = httpx.post(
        "https://gql.hashnode.com",
        headers={"Authorization": token, "Content-Type": "application/json"},
        json={"query": pub_query},
        proxies=proxies,
        timeout=10
    )
    data = resp.json()
    pubs = data.get('data', {}).get('user', {}).get('publications', {}).get('edges', [])
    for edge in pubs:
        node = edge['node']
        print(f"ID: {node['id']} | Title: {node['title']}")
except Exception as e:
    print(f"Error: {e}")
