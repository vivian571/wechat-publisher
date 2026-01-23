#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号自动定时发布调度器
每小时检测目录下的 .txt 文件，按 ABCD 顺序轮流发表
"""

import os
import sys
import time
import glob
import shutil
from pathlib import Path
from datetime import datetime
import argparse

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wechat_auto_post import WeChatAutoPoster

# 账号顺序
ACCOUNT_ORDER = [
    "Account_A_CrossBorder",
    "Account_B_English", 
    "Account_C_Life",
    "Account_D_Tech"
]

# 基础目录
BASE_DIR = Path(__file__).parent
ACCOUNTS_DIR = BASE_DIR / "accounts"

# 已发布文件的存档目录
PUBLISHED_DIR_NAME = "_published"


def get_pending_articles(account_name: str) -> list[Path]:
    """
    获取账号目录下待发布的 .txt 文件
    排除 output.txt（保留兼容）、style_reference.txt 等系统文件
    """
    account_dir = ACCOUNTS_DIR / account_name
    if not account_dir.exists():
        return []
    
    # 排除的文件模式
    exclude_files = [
        "output.txt",
        "output.html", 
        "style_reference.txt",
        "config.json",
    ]
    
    pending = []
    for txt_file in account_dir.glob("*.txt"):
        filename = txt_file.name
        # 排除系统文件和已发布目录
        if filename not in exclude_files and not filename.startswith("_published"):
            pending.append(txt_file)
    
    # 也检查 output.txt（兼容旧模式）
    output_file = account_dir / "output.txt"
    if output_file.exists():
        pending.insert(0, output_file)  # 优先发布 output.txt
    
    return pending


def move_to_published(txt_file: Path):
    """
    将已发布的文件移动到 _published 目录
    """
    published_dir = txt_file.parent / PUBLISHED_DIR_NAME
    published_dir.mkdir(exist_ok=True)
    
    # 添加时间戳避免文件名冲突
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"{timestamp}_{txt_file.name}"
    dest = published_dir / new_name
    
    shutil.move(str(txt_file), str(dest))
    print(f"   📦 已归档: {dest.name}")


def publish_article(account_name: str, txt_file: Path) -> bool:
    """
    发布单篇文章
    
    Args:
        account_name: 账号名称
        txt_file: 文章文件路径
        
    Returns:
        是否发布成功
    """
    print(f"\n{'='*60}")
    print(f"📰 正在发布文章...")
    print(f"📱 账号: {account_name}")
    print(f"📄 文件: {txt_file.name}")
    print(f"{'='*60}\n")
    
    try:
        # 如果不是 output.txt，需要临时复制为 output.txt
        account_dir = ACCOUNTS_DIR / account_name
        output_file = account_dir / "output.txt"
        
        is_temp_copy = False
        original_output_backup = None
        
        if txt_file.name != "output.txt":
            # 备份原有的 output.txt（如果存在）
            if output_file.exists():
                original_output_backup = account_dir / "_temp_output_backup.txt"
                shutil.copy(str(output_file), str(original_output_backup))
            
            # 复制文章文件为 output.txt
            shutil.copy(str(txt_file), str(output_file))
            is_temp_copy = True
            print(f"   📋 临时复制为 output.txt")
        
        # 创建发布器并发布
        poster = WeChatAutoPoster(account_name)
        poster.post()
        
        # 清理临时文件
        if is_temp_copy:
            if original_output_backup and original_output_backup.exists():
                shutil.move(str(original_output_backup), str(output_file))
            else:
                output_file.unlink(missing_ok=True)
        
        # 将原文件移动到已发布目录
        if txt_file.exists():
            move_to_published(txt_file)
        
        print(f"\n✅ 发布成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 发布失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_next_account_with_pending(start_index: int = 0) -> tuple[str, Path] | None:
    """
    按顺序查找下一个有待发布文章的账号
    
    Args:
        start_index: 起始账号索引
        
    Returns:
        (account_name, txt_file) 或 None
    """
    for i in range(len(ACCOUNT_ORDER)):
        idx = (start_index + i) % len(ACCOUNT_ORDER)
        account_name = ACCOUNT_ORDER[idx]
        pending = get_pending_articles(account_name)
        
        if pending:
            return account_name, pending[0]
    
    return None


def run_scheduler(interval_minutes: int = 60, once: bool = False):
    """
    运行定时调度器
    
    Args:
        interval_minutes: 检测间隔（分钟）
        once: 是否只运行一次
    """
    print(f"\n{'='*60}")
    print(f"🚀 微信公众号自动发布调度器")
    print(f"⏰ 检测间隔: {interval_minutes} 分钟")
    print(f"📂 账号目录: {ACCOUNTS_DIR}")
    print(f"📋 账号顺序: {' → '.join([a.split('_')[1] for a in ACCOUNT_ORDER])}")
    print(f"{'='*60}\n")
    
    current_account_index = 0
    
    while True:
        now = datetime.now()
        print(f"\n⏰ [{now.strftime('%Y-%m-%d %H:%M:%S')}] 开始检测...")
        
        # 查找有待发布文章的账号
        result = get_next_account_with_pending(current_account_index)
        
        if result:
            account_name, txt_file = result
            
            # 更新索引（下次从下一个账号开始）
            current_account_index = (ACCOUNT_ORDER.index(account_name) + 1) % len(ACCOUNT_ORDER)
            
            # 发布文章
            success = publish_article(account_name, txt_file)
            
            if success:
                print(f"\n✅ 本轮发布完成，下一个账号: {ACCOUNT_ORDER[current_account_index]}")
        else:
            print(f"   📭 没有待发布的文章")
        
        if once:
            print(f"\n💡 单次运行模式，退出")
            break
        
        # 等待下一次检测
        next_check = now.replace(second=0, microsecond=0)
        from datetime import timedelta
        next_check = next_check + timedelta(minutes=interval_minutes)
        
        wait_seconds = (next_check - datetime.now()).total_seconds()
        if wait_seconds > 0:
            print(f"\n💤 下次检测时间: {next_check.strftime('%H:%M:%S')}")
            print(f"   等待 {int(wait_seconds // 60)} 分钟 {int(wait_seconds % 60)} 秒...")
            time.sleep(wait_seconds)


def list_pending():
    """列出所有待发布的文章"""
    print(f"\n📋 待发布文章列表:")
    print(f"{'='*60}\n")
    
    total = 0
    for account_name in ACCOUNT_ORDER:
        pending = get_pending_articles(account_name)
        if pending:
            print(f"📱 {account_name}:")
            for p in pending:
                print(f"   📄 {p.name}")
                total += 1
            print()
    
    if total == 0:
        print("   📭 没有待发布的文章\n")
    else:
        print(f"{'='*60}")
        print(f"📊 共 {total} 篇待发布\n")


def main():
    parser = argparse.ArgumentParser(description="微信公众号自动定时发布调度器")
    
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=60,
        help="检测间隔（分钟），默认 60"
    )
    
    parser.add_argument(
        "--once", "-o",
        action="store_true",
        help="只运行一次（发布一篇后退出）"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="列出所有待发布的文章"
    )
    
    parser.add_argument(
        "--account", "-a",
        type=str,
        help="指定账号发布"
    )
    
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="指定发布的文件路径"
    )
    
    args = parser.parse_args()
    
    if args.list:
        list_pending()
        return
    
    # 指定账号和文件发布
    if args.account and args.file:
        txt_file = Path(args.file)
        if not txt_file.exists():
            print(f"❌ 文件不存在: {args.file}")
            return
        publish_article(args.account, txt_file)
        return
    
    # 指定账号发布（自动选择文件）
    if args.account:
        pending = get_pending_articles(args.account)
        if pending:
            publish_article(args.account, pending[0])
        else:
            print(f"❌ {args.account} 没有待发布的文章")
        return
    
    # 运行调度器
    try:
        run_scheduler(interval_minutes=args.interval, once=args.once)
    except KeyboardInterrupt:
        print(f"\n\n👋 调度器已停止")


if __name__ == "__main__":
    main()
