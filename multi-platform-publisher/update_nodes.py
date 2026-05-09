import os

nodes_code = r"""import os
import sys
import json
import logging
import requests
import datetime

# Setup logger
logger = logging.getLogger("ComfyUI_Auto_Publisher")

class TrendCollectorNode:
    '''
    Fetches trending topics from various sources (GitHub, Hashnode).
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "source": (["github", "hashnode"], {"default": "github"}),
                "limit": ("INT", {"default": 3, "min": 1, "max": 10}),
                "days_lookback": ("INT", {"default": 7, "min": 1, "max": 30}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("title_list", "trend_data_json")
    FUNCTION = "collect_trends"
    CATEGORY = "AutoPublisher"

    def collect_trends(self, source, limit, days_lookback):
        logger.info(f"Collecting trends from {source}...")
        results = []
        
        if source == "github":
            results = self._collect_github(limit, days_lookback)
        elif source == "hashnode":
            results = self._collect_hashnode(limit)
            
        titles = "\n".join([f"{i+1}. {item['title']}" for i, item in enumerate(results)])
        data_json = json.dumps(results, indent=2)
        
        return (titles, data_json)

    def _collect_github(self, limit, days_lookback):
        try:
            date_ago = (datetime.datetime.now() - datetime.timedelta(days=days_lookback)).strftime('%Y-%m-%d')
            url = f"https://api.github.com/search/repositories?q=created:>{date_ago}&sort=stars&order=desc&per_page={limit}"
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "ComfyUI-Auto-Publisher"}
            
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            for item in data.get('items', []):
                items.append({
                    "title": item.get('full_name'),
                    "description": item.get('description'),
                    "url": item.get('html_url'),
                    "stars": item.get('stargazers_count'),
                    "source": "github"
                })
            return items
        except Exception as e:
            logger.error(f"GitHub collection failed: {e}")
            return [{"title": "Error", "description": str(e)}]

    def _collect_hashnode(self, limit):
        try:
            url = "https://gql.hashnode.com"
            query = '''
            query {
              feed(first: %d, filter: {type: RECENT}) {
                edges {
                  node {
                    title
                    brief
                    slug
                    coverImage { url }
                    url
                  }
                }
              }
            }
            ''' % limit
            
            resp = requests.post(url, json={'query': query}, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            items = []
            edges = data.get('data', {}).get('feed', {}).get('edges', [])
            if not edges:
                logger.warning("No edges found in Hashnode response")
                
            for edge in edges:
                node = edge['node']
                items.append({
                    "title": node['title'],
                    "description": node['brief'],
                    "url": node['url'],
                    "image": node.get('coverImage', {}).get('url'),
                    "source": "hashnode"
                })
            return items
        except Exception as e:
            logger.error(f"Hashnode collection failed: {e}")
            return [{"title": "Error", "description": str(e)}]

class LLMArticleGeneratorNode:
    '''
    Generates an article using an LLM (OpenAI Compatible).
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "trend_data": ("STRING", {"forceInput": True}),
                "api_key": ("STRING", {"multiline": False}),
                "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
                "model": ("STRING", {"default": "gpt-3.5-turbo"}),
                "prompt_template": ("STRING", {"multiline": True, "default": "Write a technical blog post about: {title}\nDescription: {description}\n\nReturn in Markdown format."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("article_markdown",)
    FUNCTION = "generate_article"
    CATEGORY = "AutoPublisher"

    def generate_article(self, trend_data, api_key, base_url, model, prompt_template):
        try:
            trends = json.loads(trend_data)
            if not trends:
                return ("No trends found.",)
            
            item = trends[0]
            title = item.get('title', 'Unknown')
            desc = item.get('description', '')
            
            prompt = prompt_template.replace("{title}", title).replace("{description}", desc)
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            resp = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=60)
            if resp.status_code != 200:
                return (f"Error: API returned {resp.status_code} {resp.text}",)
                
            result = resp.json()
            content = result['choices'][0]['message']['content']
            return (content,)
            
        except Exception as e:
            return (f"Error calling LLM: {e}",)

class PlatformPublisherNode:
    '''
    Publishes content to Dev.to or Medium.
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "title": ("STRING", {"default": "My Article"}),
                "content_markdown": ("STRING", {"forceInput": True}),
                "platform": (["devto", "medium"],),
                "api_token": ("STRING", {"multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("published_url",)
    FUNCTION = "publish"
    CATEGORY = "AutoPublisher"

    def publish(self, title, content_markdown, platform, api_token):
        try:
            if platform == "devto":
                return self._publish_devto(title, content_markdown, api_token)
            elif platform == "medium":
                return self._publish_medium(title, content_markdown, api_token)
            return ("Unknown platform",)
        except Exception as e:
            return (f"Error publishing: {e}",)

    def _publish_devto(self, title, content, token):
        url = "https://dev.to/api/articles"
        headers = {
            "api-key": token,
            "Content-Type": "application/json"
        }
        data = {
            "article": {
                "title": title,
                "body_markdown": content,
                "published": False 
            }
        }
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        if resp.status_code in [200, 201]:
            return (resp.json().get('url'),)
        return (f"Failed: {resp.text}",)

    def _publish_medium(self, title, content, token):
        # 1. Get User ID
        user_resp = requests.get("https://api.medium.com/v1/me", headers={"Authorization": f"Bearer {token}"})
        if user_resp.status_code != 200:
            return (f"Failed to get Medium User ID: {user_resp.text}",)
        
        user_id = user_resp.json()['data']['id']
        
        # 2. Publish
        url = f"https://api.medium.com/v1/users/{user_id}/posts"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = {
            "title": title,
            "contentFormat": "markdown",
            "content": content,
            "publishStatus": "draft"
        }
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        if resp.status_code in [200, 201]:
            return (resp.json()['data']['url'],)
        return (f"Failed: {resp.text}",)
"""

outfile = r"f:\公众号写作\multi-platform-publisher\ComfyUI\custom_nodes\ComfyUI_Auto_Publisher\nodes.py"
with open(outfile, "w", encoding="utf-8") as f:
    f.write(nodes_code)

print("Nodes updated successfully.")
