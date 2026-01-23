# -*- coding: utf-8 -*-
"""
每日自动化文章生成脚本
功能：抓取热点 + 根据各账户领域智能匹配选题 + 批量生成爆款文章 + 自动生成封面图片
推荐运行时间：每天早上 8:00
"""

import sys
import json
import random
import logging
from pathlib import Path
from datetime import datetime

import requests

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from generator import ContentGenerator
from image_generator import generate_cover_for_article

# ===== 日志配置 =====
LOG_FILE = Path(__file__).parent / "daily_auto_gen.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===== 各账户领域关键词配置 =====
# 根据账户领域定义独立的热点筛选关键词
ACCOUNT_KEYWORDS = {
    "Account_A_CrossBorder": {
        "name": "AI提示词实战",
        "keywords": ["AI", "ChatGPT", "人工智能", "机器人", "智能", "科技", "效率", "办公", "自动化", "GPT", "写作", "神器"],
        "fallback_topics": ["用ChatGPT提升工作效率的3个技巧", "AI时代普通人必学的提示词工程", "一个提示词让AI写出爆款文案"]
    },
    "Account_B_English": {
        "name": "AI科技赚钱",
        "keywords": ["钱", "赚", "副业", "收入", "变现", "创业", "致富", "月入", "薪", "穷", "富", "投资", "理财", "工资", "AI", "裁员", "失业", "就业"],
        "fallback_topics": ["2026年AI副业最赚钱的3种玩法", "普通人用AI月入过万的真实案例", "AI时代的信息差变现指南"]
    },
    "Account_C_Life": {
        "name": "治愈系小厨房",
        "keywords": ["吃", "菜", "美食", "餐", "做饭", "厨房", "食", "味", "烹", "下饭", "早餐", "零食", "甜品", "火锅", "烧烤", "网红"],
        "fallback_topics": ["冬天一定要学会的3道暖心汤", "超简单的家常下饭菜，连做3碗饭", "一人食也要精致，10分钟搞定一餐"]
    },
    "Account_D_Tech": {
        "name": "节气养生小馆",
        "keywords": ["养生", "健康", "医", "病", "睡", "累", "疲", "中医", "老年", "保健", "身体", "免疫", "感冒", "长寿", "节气", "寒冷", "保暖"],
        "fallback_topics": ["小寒节气养生指南：这3件事别再做了", "医生提醒：冬天这样吃最养身体", "老祖宗传下来的冬季养生偏方"]
    }
}


def fetch_baidu_hot(top_n: int = 50) -> list:
    """抓取百度热搜前N条"""
    url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://top.baidu.com/"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15, proxies={"http": None, "https": None})
        resp.raise_for_status()
        data = resp.json()
        hot_list = data["data"]["cards"][0]["content"][0]["content"][:top_n]
        return [item.get("word", "") for item in hot_list if item.get("word")]
    except Exception as e:
        logger.error(f"抓取百度热搜失败: {e}")
        return []


def match_topic_for_account(hot_list: list, account_id: str) -> str:
    """为指定账户匹配最合适的热点主题"""
    config = ACCOUNT_KEYWORDS.get(account_id, {})
    keywords = config.get("keywords", [])
    fallback_topics = config.get("fallback_topics", ["今日热门话题"])
    
    # 筛选包含该账户关键词的热点
    matched = []
    for title in hot_list:
        hit_keywords = [kw for kw in keywords if kw in title]
        if hit_keywords:
            matched.append((title, hit_keywords))
    
    if matched:
        # 随机选一个匹配的热点
        selected, hit_kws = random.choice(matched)
        logger.info(f"   🎯 命中热点（关键词: {hit_kws}）: {selected}")
        return selected
    else:
        # 保底：使用预设主题
        fallback = random.choice(fallback_topics)
        logger.info(f"   📝 使用保底主题: {fallback}")
        return fallback


def run_daily_generation():
    """执行每日生成任务（每个账户独立选题 + 封面图片）"""
    logger.info("=" * 60)
    logger.info(f"🚀 每日自动化任务启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    # 1. 抓取热点
    logger.info("📡 正在抓取百度热搜...")
    hot_list = fetch_baidu_hot(50)
    logger.info(f"   获取到 {len(hot_list)} 条热搜")
    
    # 2. 初始化生成器
    try:
        generator = ContentGenerator()
    except Exception as e:
        logger.error(f"❌ 初始化生成器失败: {e}")
        return
    
    # 3. 遍历每个账户，独立选题并生成
    accounts_dir = PROJECT_ROOT / "accounts"
    generated_count = 0
    cover_count = 0
    
    for account_dir in sorted(accounts_dir.iterdir()):
        if not account_dir.is_dir():
            continue
        
        account_id = account_dir.name
        account_config = ACCOUNT_KEYWORDS.get(account_id, {})
        account_name = account_config.get("name", account_id)
        
        logger.info(f"\n📌 【{account_name}】 正在选题...")
        
        # 为该账户匹配合适的热点
        topic = match_topic_for_account(hot_list, account_id)
        
        # 生成文章
        try:
            logger.info(f"   🧠 开始生成文章，主题: 「{topic}」")
            result = generator.generate_content(account_id, topic=topic)
            if result:
                generated_count += 1
                logger.info(f"   ✅ 文章生成完成: {result}")
                
                # 生成封面图片
                logger.info(f"   🎨 正在生成封面图片...")
                cover_path = generate_cover_for_article(topic, str(account_dir))
                if cover_path:
                    cover_count += 1
                    logger.info(f"   ✅ 封面生成完成: {cover_path}")
                else:
                    logger.warning(f"   ⚠️ 封面生成失败")
                    
        except Exception as e:
            logger.error(f"   ❌ 生成失败: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"🎉 每日任务执行完毕！共生成 {generated_count} 篇文章，{cover_count} 张封面")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_daily_generation()

