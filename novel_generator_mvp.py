import os
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

API_KEY = os.environ.get("GROQ_API_KEY", "")
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_ID = "llama-3.3-70b-versatile"

def fetch_trending_projects(limit=5):
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

def generate_novel_concepts(projects_info):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """
你是一个顶级的“技术现实主义”科幻小说家。
你的核心理念是：真正吸引人的不是技术本身，而是技术造成的人性变化和时代恐惧感。

【核心任务】
基于以下 GitHub 热门项目，提取其背后的技术本质，并想象当它全面普及后，对社会、伦理、人际关系带来的灾难性或异化影响。
为每个项目生成 1 个具有“现实侵入感”和“极强爆款潜力”的小说设定脑洞。

【要求】
每个项目的分析和设定必须包含：
1. **项目名称与本质**：用一句话说明它是干什么的。
2. **社会后果/人性异化**：它会如何改变人类的职业、婚姻、信任、记忆或生死观？
3. **爆款小说设定**：用 100-200 字写出一个极具冲突感、让人不寒而栗的故事简介（类似黑镜、赛博朋克）。必须具体到角色的具体遭遇。
4. **核心恐惧点/爽点**：读者看这个故事到底在害怕什么？（例如：“如果死去的妻子重新发来消息”、“如果我不知道今天开会的是自己还是 AI 替身”）

【语言风格】
冷静、犀利、一针见血，带有强烈的悬疑色彩。

【今日热门项目列表】
"""
    for p in projects_info:
        prompt += f"- {p['repo']}: {p['desc']}\n"
        
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 4000
    }
    
    print("🧠 正在请求大模型进行「社会恐惧感」剧本解构...")
    try:
        response = requests.post(URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"❌ API 请求错误: {e}")
        return None

def main():
    trending = fetch_trending_projects(5)
    if not trending:
        return
        
    projects_info_str = "\n".join([f"{p['repo']}: {p['desc']}" for p in trending])
    print(f"✅ 成功抓取 {len(trending)} 个项目:\n{projects_info_str}\n")
    
    novel_concepts = generate_novel_concepts(trending)
    
    if novel_concepts:
        date_str = datetime.now().strftime('%Y-%m-%d')
        target_dir = "/Users/ax/wechat-publisher/wechat/documents/小说"
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, f"{date_str}-Trending-Novel-Concepts.md")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {date_str} GitHub Trending 自动解构（技术现实主义）\n\n")
            f.write(novel_concepts)
            
        print(f"\n✅ 成功生成小说脑洞设定！已保存至: {file_path}")
        print("\n--- 生成内容预览 ---\n")
        print(novel_concepts)
    else:
        print("❌ 生成脑洞设定失败。")

if __name__ == "__main__":
    main()
