# -*- coding: utf-8 -*-
"""
百度实时热搜抓取脚本
功能：抓取Top50热点，智能筛选社会情绪/搞钱/职场类话题
"""

import requests

# 筛选关键词
KEYWORDS = ['钱', '赚', '职', '业', '薪', '穷', '富', '女', '房', '医', '累', '在这个']

def get_matched_keywords(title):
    """返回标题中命中的关键词列表"""
    return [kw for kw in KEYWORDS if kw in title]

def get_baidu_hot():
    """抓取百度热搜并智能筛选"""
    url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://top.baidu.com/"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15, proxies={"http": None, "https": None})
        resp.raise_for_status()
        data = resp.json()
        
        hot_list = data["data"]["cards"][0]["content"][0]["content"][:50]
        
        # 筛选命中关键词的热搜
        matched = []
        for item in hot_list:
            title = item.get("word", "")
            keywords = get_matched_keywords(title)
            if keywords:
                matched.append((title, keywords))
        
        print("\n📌 百度热搜智能筛选结果:\n" + "=" * 50)
        
        if matched:
            for i, (title, keywords) in enumerate(matched, 1):
                kw_str = ",".join(keywords)
                print(f"{i:2}. [{kw_str}] {title}")
        else:
            # 保底机制：无命中则输出前3条
            print("⚠️ 无关键词命中，保底输出前3条：")
            for i, item in enumerate(hot_list[:3], 1):
                print(f"{i:2}. {item.get('word', '')}")
        
        print("=" * 50)
        print(f"📊 统计: Top50中命中 {len(matched)} 条")
        
    except Exception as e:
        print(f"❌ 抓取失败: {e}")

if __name__ == "__main__":
    get_baidu_hot()
