#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Matrix Cleanup Script
清理所有账号目录中已发表的文章和封面图片
"""

import os
import glob
from pathlib import Path
from datetime import datetime


def cleanup_account(account_path: Path, dry_run: bool = False) -> dict:
    """
    清理单个账号目录中的临时文件
    
    Args:
        account_path: 账号目录路径
        dry_run: 如果为 True，只显示要删除的文件但不实际删除
        
    Returns:
        dict: 删除的文件统计
    """
    deleted = {"output": [], "cover": []}
    
    # 要删除的文件模式
    output_patterns = ["output.txt", "output.html"]
    cover_patterns = [
        "cover.png", "cover.jpg", "cover.jpeg", "cover.webp",
        "cover_fixed.png", "cover_fixed.jpg", "cover_fixed.jpeg",
        "cover_generated.png", "cover_generated.jpg"
    ]
    
    # 删除输出文件
    for pattern in output_patterns:
        file_path = account_path / pattern
        if file_path.exists():
            if dry_run:
                print(f"   [DRY RUN] 将删除: {file_path.name}")
            else:
                os.remove(file_path)
                print(f"   🗑️  已删除: {file_path.name}")
            deleted["output"].append(file_path.name)
    
    # 删除封面图片
    for pattern in cover_patterns:
        file_path = account_path / pattern
        if file_path.exists():
            if dry_run:
                print(f"   [DRY RUN] 将删除: {file_path.name}")
            else:
                os.remove(file_path)
                print(f"   🗑️  已删除: {file_path.name}")
            deleted["cover"].append(file_path.name)
    
    return deleted


def cleanup_all(base_dir: Path = None, dry_run: bool = False, account_filter: str = None):
    """
    清理所有账号目录
    
    Args:
        base_dir: 项目根目录
        dry_run: 如果为 True，只显示要删除的文件但不实际删除
        account_filter: 账号过滤器，如 "Account_A" 只清理 A 账号
    """
    if base_dir is None:
        base_dir = Path(__file__).parent
    
    accounts_dir = base_dir / "accounts"
    
    if not accounts_dir.exists():
        print(f"❌ 账号目录不存在: {accounts_dir}")
        return
    
    print(f"\n{'='*60}")
    print(f"🧹 WeChat Matrix 清理工具")
    print(f"📂 账号目录: {accounts_dir}")
    if dry_run:
        print(f"⚠️  DRY RUN 模式：只显示将要删除的文件，不实际删除")
    print(f"{'='*60}\n")
    
    total_output = 0
    total_cover = 0
    
    # 遍历所有账号目录
    for account_dir in sorted(accounts_dir.iterdir()):
        if not account_dir.is_dir():
            continue
        
        # 应用过滤器
        if account_filter and account_filter not in account_dir.name:
            continue
        
        print(f"📁 {account_dir.name}")
        
        result = cleanup_account(account_dir, dry_run)
        
        if not result["output"] and not result["cover"]:
            print(f"   ✨ 已经是干净的")
        
        total_output += len(result["output"])
        total_cover += len(result["cover"])
    
    # 输出统计
    print(f"\n{'='*60}")
    if dry_run:
        print(f"📊 [DRY RUN] 将删除: {total_output} 个文章文件, {total_cover} 个封面图片")
    else:
        print(f"✅ 清理完成: 删除了 {total_output} 个文章文件, {total_cover} 个封面图片")
    print(f"{'='*60}\n")


def watch_mode(base_dir: Path = None, interval: int = 3600):
    """
    守护监控模式：持续检测并自动清理已发表的文件
    
    Args:
        base_dir: 项目根目录
        interval: 检测间隔（秒）
    """
    if base_dir is None:
        base_dir = Path(__file__).parent
    
    accounts_dir = base_dir / "accounts"
    
    print(f"\n{'='*60}")
    print(f"👁️  WeChat Matrix 守护监控模式")
    print(f"📂 监控目录: {accounts_dir}")
    print(f"⏱️  检测间隔: {interval} 秒")
    print(f"🛑 按 Ctrl+C 停止监控")
    print(f"{'='*60}\n")
    
    import time
    
    try:
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            
            # 静默检测，只有发现文件才输出
            found_files = False
            
            for account_dir in sorted(accounts_dir.iterdir()):
                if not account_dir.is_dir():
                    continue
                
                # 检查是否有需要清理的文件
                output_patterns = ["output.txt", "output.html"]
                cover_patterns = [
                    "cover.png", "cover.jpg", "cover.jpeg", "cover.webp",
                    "cover_fixed.png", "cover_fixed.jpg", "cover_fixed.jpeg",
                    "cover_generated.png", "cover_generated.jpg"
                ]
                
                files_to_delete = []
                for pattern in output_patterns + cover_patterns:
                    file_path = account_dir / pattern
                    if file_path.exists():
                        files_to_delete.append(file_path)
                
                # 如果有文件需要清理
                if files_to_delete:
                    if not found_files:
                        print(f"\n[{current_time}] 🔍 检测到需要清理的文件：")
                        found_files = True
                    
                    print(f"   📁 {account_dir.name}")
                    for file_path in files_to_delete:
                        os.remove(file_path)
                        print(f"      🗑️  已删除: {file_path.name}")
            
            if found_files:
                print(f"   ✅ 清理完成，继续监控...")
            
            # 等待下一次检测
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print(f"\n\n🛑 监控已停止")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat Matrix 清理工具")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只显示将要删除的文件，不实际删除"
    )
    parser.add_argument(
        "--account",
        type=str,
        help="只清理指定账号（如：Account_A、Account_B）"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="清理所有账号（无需确认）"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="守护监控模式：持续检测并自动清理"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="监控模式的检测间隔（秒），默认30秒"
    )
    
    args = parser.parse_args()
    
    # 守护监控模式
    if args.watch:
        watch_mode(interval=args.interval)
        return
    
    # 如果不是 --all 模式，需要确认
    if not args.all and not args.dry_run:
        print("\n⚠️  警告：此操作将删除所有账号目录中的 output.txt 和 cover 图片！")
        confirm = input("确定要继续吗？(y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ 操作已取消")
            return
    
    cleanup_all(dry_run=args.dry_run, account_filter=args.account)


if __name__ == "__main__":
    main()
