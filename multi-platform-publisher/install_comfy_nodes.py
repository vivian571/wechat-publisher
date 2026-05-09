import os

base_dir = r"f:\公众号写作\multi-platform-publisher\ComfyUI\custom_nodes\ComfyUI_Auto_Publisher"
os.makedirs(base_dir, exist_ok=True)

# __init__.py
init_code = """from .nodes import TrendCollectorNode, LLMArticleGeneratorNode, PlatformPublisherNode

NODE_CLASS_MAPPINGS = {
    "TrendCollectorNode": TrendCollectorNode,
    "LLMArticleGeneratorNode": LLMArticleGeneratorNode,
    "PlatformPublisherNode": PlatformPublisherNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TrendCollectorNode": "🔍 Trend Collector (Auto-Pub)",
    "LLMArticleGeneratorNode": "✍️ LLM Article Generator (Auto-Pub)",
    "PlatformPublisherNode": "🚀 Platform Publisher (Auto-Pub)"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
"""

with open(os.path.join(base_dir, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_code)

# nodes.py
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
    Fetches trending topics from various sources (GitHub, etc.)
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
            
        # Format outputs
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
            return [{"title": "Error collecting trends", "description": str(e)}]

    def _collect_hashnode(self, limit):
        # Placeholder
        return [{"title": "Hashnode Trend Placeholder", "description": "Not implemented yet"}]

class LLMArticleGeneratorNode:
    '''
    Generates an article using an LLM.
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "trend_data": ("STRING", {"forceInput": True}),
                "api_key": ("STRING", {"multiline": False}),
                "prompt_template": ("STRING", {"multiline": True, "default": "Write a technical blog post about: {title}\nDescription: {description}"}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("article_markdown",)
    FUNCTION = "generate_article"
    CATEGORY = "AutoPublisher"

    def generate_article(self, trend_data, api_key, prompt_template):
        try:
            trends = json.loads(trend_data)
            if not trends:
                return ("No trends found.",)
            
            # Simple logic: Pick the first trend
            topic = trends[0]
            title = topic.get('title', 'Unknown')
            desc = topic.get('description', '')
            
            # Placeholder for actual LLM call
            article = f"# {title}\n\n**Description**: {desc}\n\n(Generated Content Placeholder)\n\nPowered by {api_key[:4]}..."
            return (article,)
        except Exception as e:
            return (f"Error: {e}",)

class PlatformPublisherNode:
    '''
    Publishes content.
    '''
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "title": ("STRING", {"default": "My Article"}),
                "content_markdown": ("STRING", {"forceInput": True}),
                "platform": (["medium", "devto"],),
                "api_token": ("STRING", {"multiline": False}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("published_url",)
    FUNCTION = "publish"
    CATEGORY = "AutoPublisher"

    def publish(self, title, content_markdown, platform, api_token):
        return (f"https://{platform}.com/mock-url-for-{title}",)
"""

with open(os.path.join(base_dir, "nodes.py"), "w", encoding="utf-8") as f:
    f.write(nodes_code)

# requirements.txt
with open(os.path.join(base_dir, "requirements.txt"), "w", encoding="utf-8") as f:
    f.write("requests\n")

print("Files created successfully.")
