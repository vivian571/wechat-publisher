# -*- coding: utf-8 -*-
"""
Horizon Bridge - 将 Horizon 简报集成到 WeChat Matrix
功能：解析 Horizon 生成的每日简报，提取高质量新闻，并自动触发公众号文章生成。
"""

import os
import re
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from generator import ContentGenerator

# ===== 配置 =====
HORIZON_DIR = PROJECT_ROOT.parent / "horizon_radar"
SUMMARIES_DIR = HORIZON_DIR / "data" / "summaries"

# 日志配置
LOG_FILE = Path(__file__).parent / "horizon_bridge.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 各账户对应的关键词（用于从简报中筛选最相关的条目）
# 建议与 daily_auto_gen.py 保持同步或进行扩展
ACCOUNT_MAPPING = {
    "fluent fan": ["英语", "外语", "学习", "口语", "翻译", "出海"],
    "初心录": ["AI", "GPT", "Claude", "Agent", "自动化", "效率", "工具"],
    "美丽好风景": ["风景", "美学", "图片", "视觉", "摄影", "生活"],
    "零更_PromptBook": ["Prompt", "提示词", "指令", "大模型", "技巧", "实战"]
}

def get_latest_summary(lang="zh"):
    """获取最新的简报文件"""
    if not SUMMARIES_DIR.exists():
        logger.error(f"❌ Horizon 简报目录不存在: {SUMMARIES_DIR}")
        return None
    
    pattern = f"horizon-*-{lang}.md"
    files = list(SUMMARIES_DIR.glob(pattern))
    if not files:
        logger.warning(f"⚠️ 未找到语言为 {lang} 的简报文件")
        return None
    
    # 按修改时间排序
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0]

def parse_horizon_summary(file_path):
    """解析 Horizon 简报，提取新闻条目"""
    if not file_path:
        return []
    
    logger.info(f"📖 正在解析简报: {file_path.name}")
    content = file_path.read_text(encoding="utf-8")
    
    # 简单的正则匹配新闻条目
    # Horizon 格式通常是 ### [标题](链接) 或类似的
    # 我们提取所有 ### 开头的标题行
    items = []
    
    # 查找所有项目区块
    # 格式通常是：
    # ### [标题](URL)
    # **来源** · 评分
    # 摘要内容
    
    sections = re.split(r'\n### ', content)
    for section in sections[1:]: # 跳过第一个区块（通常是 Header/TOC）
        lines = section.strip().split('\n')
        if not lines:
            continue
            
        header_line = lines[0]
        # 提取标题：[标题](URL) 或 标题
        title_match = re.search(r'\[(.*?)\]', header_line)
        title = title_match.group(1) if title_match else header_line.split('{#')[0].strip()
        
        # 提取摘要（通常在第二行之后，直到下一个加粗部分或结尾）
        summary = ""
        for line in lines[1:]:
            line = line.strip()
            if not line or line.startswith('**') or line.startswith('-'):
                continue
            summary = line
            break
            
        items.append({
            "title": title,
            "summary": summary,
            "full_text": section
        })
        
    logger.info(f"✅ 成功提取 {len(items)} 条新闻")
    return items

def match_item_for_account(items, account_id):
    """为账号匹配最相关的简报条目"""
    keywords = ACCOUNT_MAPPING.get(account_id, [])
    if not keywords:
        return items[0] if items else None
        
    best_item = None
    max_hits = -1
    
    for item in items:
        text = (item['title'] + item['summary']).lower()
        hits = sum(1 for kw in keywords if kw.lower() in text)
        if hits > max_hits:
            max_hits = hits
            best_item = item
            
    return best_item

def run_bridge(dry_run=False):
    """运行桥接程序：获取简报 -> 筛选 -> 生成"""
    logger.info(f"🚀 Horizon Bridge 启动 {'(模拟模式)' if dry_run else ''}")
    
    # 1. 获取最新简报
    summary_file = get_latest_summary("zh")
    if not summary_file:
        logger.error("❌ 无法获取 Horizon 简报，请确保 Horizon 已运行并生成了简报。")
        return
        
    # 2. 解析简报
    items = parse_horizon_summary(summary_file)
    if not items:
        logger.error("❌ 简报中未找到有效新闻。")
        return
        
    # 3. 初始化生成器
    generator = None
    if not dry_run:
        try:
            generator = ContentGenerator()
        except Exception as e:
            logger.error(f"❌ 初始化生成器失败: {e}")
            return
        
    # 4. 遍历账号进行生成
    accounts_dir = PROJECT_ROOT / "accounts"
    for account_dir in sorted(accounts_dir.iterdir()):
        if not account_dir.is_dir():
            continue
            
        account_id = account_dir.name
        if account_id not in ACCOUNT_MAPPING:
            continue
            
        logger.info(f"📌 正在为账号 【{account_id}】 匹配新闻...")
        item = match_item_for_account(items, account_id)
        
        if item:
            topic = item['title']
            context = item['summary']
            logger.info(f"   🎯 匹配成功: 「{topic}」")
            
            if dry_run:
                logger.info(f"   [DRY RUN] 将会生成文章: {topic}")
                continue

            try:
                # 触发生成，传入 context 帮助 AI 更好理解
                result = generator.generate_content(account_id, topic=topic)
                if result:
                    logger.info(f"   ✅ 文章生成完成: {result}")
            except Exception as e:
                logger.error(f"   ❌ 生成失败: {e}")
        else:
            logger.warning(f"   ⚠️ 账号 {account_id} 未能匹配到合适的新闻。")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Horizon Bridge")
    parser.add_argument("--dry-run", action="store_true", help="仅模拟解析和匹配，不调用 AI 生成")
    args = parser.parse_args()
    
    run_bridge(dry_run=args.dry_run)
