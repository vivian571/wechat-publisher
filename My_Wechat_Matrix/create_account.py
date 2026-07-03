#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速创建新账号的交互式脚本
"""

import os
import json
from pathlib import Path


def create_account():
    """交互式创建新账号"""
    print("\n" + "="*60)
    print("🎯 创建新公众号账号配置")
    print("="*60 + "\n")
    
    # 获取基本信息
    account_id = input("📝 账号ID（英文，如 Account_E_Finance）: ").strip()
    account_name = input("📝 账号名称（中文，如 财经观察）: ").strip()
    
    # 创建目录
    base_dir = Path(__file__).parent
    account_dir = base_dir / "accounts" / account_id
    
    if account_dir.exists():
        print(f"❌ 账号 {account_id} 已存在！")
        return
    
    account_dir.mkdir(parents=True, exist_ok=True)
    
    # 收集配置信息
    print("\n📋 请描述账号的定位和风格：")
    role = input("   角色定位（如：资深财经分析师）: ").strip()
    tone = input("   语气风格（如：专业严谨）: ").strip()
    style = input("   写作风格（如：数据驱动，深度分析）: ").strip()
    
    print("\n📌 主要内容方向（用逗号分隔，如：股市分析,投资策略,经济趋势）:")
    topics_input = input("   ").strip()
    topics = [t.strip() for t in topics_input.split(",")]
    
    target_words = input("\n📏 目标字数（默认1500）: ").strip() or "1500"
    
    emoji_usage_map = {"1": "low", "2": "moderate", "3": "high"}
    print("\n😊 Emoji使用频率：")
    print("   1 - 少量  2 - 适中  3 - 较多")
    emoji_choice = input("   选择（1-3，默认2）: ").strip() or "2"
    emoji_usage = emoji_usage_map.get(emoji_choice, "moderate")
    
    # 生成 system_prompt.md
    system_prompt = f"""# Role
你是一位{role}，{tone}，{style}。

# Persona Traits
- **语气**: {tone}
- **风格**: {style}
- **关键词**: {', '.join(topics)}

# Content Guidelines
- 每篇文章聚焦一个核心主题
- 结构清晰，逻辑严密
- 文章长度控制在{target_words}字左右
- 适当使用数据和案例支撑观点

# Writing Style
- 根据账号定位调整语言风格
- 适当使用emoji增加可读性
- 注重读者体验和互动

# Topics Focus
{chr(10).join(f'- {topic}' for topic in topics)}
"""
    
    # 生成 account_config.json
    account_config = {
        "account_name": account_name,
        "account_id": account_id,
        "enabled": True,
        "generation_frequency": "daily",
        "preferred_topics": topics,
        "target_word_count": int(target_words),
        "emoji_usage": emoji_usage
    }
    
    # 生成 style_reference.txt 模板
    style_reference = """【参考文章1】

在这里粘贴一篇你觉得写得很好的同类文章，AI会学习其风格。

---

【参考文章2】

再粘贴一篇风格相似的文章。

---

【参考文章3】

第三篇参考文章。

提示：参考文章越贴近你想要的风格，生成的内容就越符合预期。
"""
    
    # 写入文件
    with open(account_dir / "system_prompt.md", 'w', encoding='utf-8') as f:
        f.write(system_prompt)
    
    with open(account_dir / "account_config.json", 'w', encoding='utf-8') as f:
        json.dump(account_config, f, ensure_ascii=False, indent=4)
    
    with open(account_dir / "style_reference.txt", 'w', encoding='utf-8') as f:
        f.write(style_reference)
    
    print("\n" + "="*60)
    print(f"✅ 账号 '{account_name}' 创建成功！")
    print(f"📁 位置: {account_dir}")
    print("\n📝 下一步：")
    print(f"   1. 编辑 {account_id}/style_reference.txt，添加参考文章")
    print(f"   2. 运行 python generator.py --account {account_id} 生成内容")
    print("="*60 + "\n")


if __name__ == "__main__":
    create_account()
