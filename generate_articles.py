import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"
# Using a widely available fallback model to avoid decommission errors
# We will use llama3-8b-8192 if others fail, but start with llama-3.3-70b-versatile
MODEL_ID = "llama-3.3-70b-versatile"

def fetch_trending_projects(limit=7):
    print("🌐 正在抓取今日 GitHub 热榜...")
    url = 'https://github.com/trending'
    headers = {'User-Agent': 'Mozilla/5.0'}
    projects = []
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        repos = soup.select('article.Box-row')
        
        for repo in repos[:limit]:
            title = repo.select_one('h2 a').text.strip().replace('\n', '').replace(' ', '')
            desc_elem = repo.select_one('p')
            desc = desc_elem.text.strip() if desc_elem else 'No description available.'
            projects.append({"repo": title, "desc": desc})
        return projects
    except Exception as e:
        print(f"❌ 抓取热榜失败: {e}")
        return []

def generate_content(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 3000
    }
    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except requests.exceptions.HTTPError as e:
        if response.status_code == 429:
            print("⚠️ 触发 Groq API 频率限制，等待 15 秒后重试...")
            time.sleep(15)
            # Retry once
            response = requests.post(URL, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        else:
            print(f"❌ API 请求错误: {e}")
            if 'response' in locals():
                print(response.text)
            return None
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return None

directories = [
    "/Users/ax/wechat-publisher/wechat/documents/AI流习社",
    "/Users/ax/wechat-publisher/wechat/documents/开源智核",
    "/Users/ax/wechat-publisher/wechat/documents/fluent fan",
    "/Users/ax/wechat-publisher/wechat/documents/初心录",
    "/Users/ax/wechat-publisher/wechat/documents/平凡日子记",
    "/Users/ax/wechat-publisher/wechat/documents/美丽好风景",
    "/Users/ax/wechat-publisher/wechat/documents/零更_PromptBook"
]

system_prompt = """
你是一个顶级的公众号爆款作者，擅长将硬核的 GitHub 科技项目转化为通俗易懂、幽默有趣、且极具深度的干货文章。

【核心任务】
根据提供的 GitHub 项目信息，写一篇引人注目的深度文章。

【写作框架与要求】
1. 标题：必须极具吸引力，包含项目名，让人有点击欲望。使用Markdown一级标题。
2. 痛点引入（为什么会有这个项目？）：用大白话和生活/工作中的痛点引入，引发共鸣。
3. 核心拆解（项目是什么？）：把底层的硬核逻辑用“学生都能听懂的大白话”讲清楚。避免堆砌专业词汇，用比喻。
4. 实操指南（怎么样运行运用项目？）：加入具体、详细、保姆级的操作使用步骤（包含命令行、代码片段或界面操作）。
5. 实用案例：列举至少 3 个不同场景下的实用方法案例，展示它如何改变生产力。
6. 价值提示词 (Prompt)：将该项目的核心逻辑本质，整理成一份具体详细的、可供用户直接复制使用的高级价值提示词。
7. 多角度深度分析：从效率、行业、未来进化等多个维度深度剖析它的价值。
8. 避坑指南：必须加入这一章节，列出至少 3 个可能遇到的问题、坑点以及相应的防范建议。

【语言风格与篇幅】
- 语言风格：短句发力，节奏明快，逻辑闭环，高频刺激，说人话。带点幽默感和自嘲，像是一个极客朋友在和你聊天。
- 字数要求：内容必须极其详实，字数在 2500 字左右（越长越详尽越好，不要偷工减料）。
- 排版：使用丰富的 Markdown 语法（加粗、引用、列表、代码块）提升阅读体验。
"""

def main():
    trending = fetch_trending_projects(7)
    if not trending:
        return

    for i, p in enumerate(trending):
        repo_name = p['repo'].split('/')[-1]
        target_dir = directories[i % len(directories)]
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_name = f"{date_str}-{repo_name}.md"
        file_path = os.path.join(target_dir, file_name)
        
        if os.path.exists(file_path):
            print(f"⏭️ 文件 {file_path} 已存在，跳过。")
            continue
            
        print(f"\n✍️ 正在生成文章: {repo_name} -> {target_dir.split('/')[-1]}")
        
        full_prompt = system_prompt + f"\n\n请为 GitHub 今日热门项目【{p['repo']}】写一篇文章。项目简介：{p['desc']}"
        
        content = generate_content(full_prompt)
        if content:
            os.makedirs(target_dir, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 成功生成并写入: {file_name}")
            # Add delay to avoid aggressive rate limiting
            time.sleep(3)
        else:
            print(f"❌ 生成 {repo_name} 失败。")

if __name__ == "__main__":
    main()
