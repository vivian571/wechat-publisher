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
    "fluent fan": {
        "name": "英语学习爱好者",
        "keywords": ["英语", "外语", "学习", "口语", "翻译", "出海", "全球", "留学"],
        "fallback_topics": ["如何用AI打造沉浸式英语学习环境", "2026年出海人必备的翻译神器", "从零开始起号海外社媒"]
    },
    "初心录": {
        "name": "AI工具深度解析",
        "keywords": ["AI", "ChatGPT", "Claude", "Agent", "自动化", "效率", "工具", "生产力", "机器人"],
        "fallback_topics": ["DeepSeek R1 深度实测：国产大模型之光", "2026年个人AI Agent构建指南", "用AI重塑你的工作流"]
    },
    "美丽好风景": {
        "name": "赛博美学与风景",
        "keywords": ["风景", "美学", "图片", "视觉", "摄影", "生活", "艺术", "创意", "旅行"],
        "fallback_topics": ["AI生成的绝美风景图，甚至比实拍还动人", "赛博朋克风摄影调色教程", "寻找城市中的赛博美学"]
    },
    "零更_PromptBook": {
        "name": "爆款提示词实战",
        "keywords": ["Prompt", "提示词", "指令", "大模型", "技巧", "实战", "调教", "文案", "创作"],
        "fallback_topics": ["万能提示词框架 CO-STAR 实战解析", "如何写出让 AI 乖乖听话的指令", "爆款文案背后的提示词逻辑"]
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


def run_daily_generation(source="baidu"):
    """执行每日生成任务（每个账户独立选题 + 封面图片）"""
    logger.info("=" * 60)
    logger.info(f"🚀 每日自动化任务启动 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📍 内容来源: {source}")
    logger.info("=" * 60)
    
    # 1. 抓取热点/简报
    hot_list = []
    horizon_items = []
    
    if source == "horizon":
        from horizon_bridge import get_latest_summary, parse_horizon_summary
        summary_file = get_latest_summary("zh")
        if summary_file:
            horizon_items = parse_horizon_summary(summary_file)
            logger.info(f"📡 从 Horizon 简报获取到 {len(horizon_items)} 条高价值资讯")
        else:
            logger.warning("⚠️ 未找到 Horizon 简报，回退到百度热搜")
            source = "baidu"
            
    if source == "baidu":
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
        account_config = ACCOUNT_KEYWORDS.get(account_id)
        if not account_config:
            continue
            
        account_name = account_config.get("name", account_id)
        
        logger.info(f"\n📌 【{account_name}】 正在选题...")
        
        # 选题逻辑
        topic = ""
        if source == "horizon" and horizon_items:
            from horizon_bridge import match_item_for_account
            item = match_item_for_account(horizon_items, account_id)
            if item:
                topic = item['title']
                logger.info(f"   🎯 命中 Horizon 资讯: {topic}")
        
        if not topic:
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
    import argparse
    parser = argparse.ArgumentParser(description="Daily Auto Generation")
    parser.add_argument("--source", choices=["baidu", "horizon"], default="baidu", help="热点来源: baidu (默认) 或 horizon")
    args = parser.parse_args()
    
    run_daily_generation(source=args.source)

