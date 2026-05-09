#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证自动发布代理是否正常工作
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime


def create_test_article(account_name: str, base_dir: Path):
    """创建测试文章"""
    account_dir = base_dir / "accounts" / account_name
    
    if not account_dir.exists():
        print(f"❌ 账号目录不存在: {account_name}")
        return False
    
    # 创建测试内容
    test_content = f"""AI提示词测试文章 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

这是一篇由自动发布代理测试脚本生成的测试文章。

🎯 测试目的
验证自动发布代理是否能够正确检测到新文章并触发发布流程。

📝 测试内容
1. 文章生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
2. 账号名称: {account_name}
3. 测试编号: {int(time.time())}

🔍 预期行为
- 代理应在 5 秒内检测到此文件
- 自动调用 wechat_auto_post.py 发布
- 打开浏览器并填充内容
- 等待用户扫码确认

✅ 如果看到浏览器自动打开，说明代理工作正常！

━━━━━━━━━━━━━━━━━━━━━━

💡 提示词技巧分享

想让AI写出更好的文章？试试这个万能模板：

角色设定 + 任务描述 + 输出要求 + 风格参考

例如：
"你是一位资深的技术博主，请写一篇关于Python装饰器的教程。要求：1500字，包含代码示例，语言通俗易懂。参考风格：廖雪峰的Python教程。"

🚀 立刻试试吧！

关注我，获取更多AI提示词技巧！
"""
    
    output_file = account_dir / "output.txt"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"✅ 测试文章已创建: {output_file}")
        print(f"📄 内容长度: {len(test_content)} 字符")
        return True
    
    except Exception as e:
        print(f"❌ 创建测试文章失败: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("🧪 自动发布代理测试脚本")
    print("="*60)
    
    base_dir = Path(__file__).parent
    
    # 获取所有账号
    accounts_dir = base_dir / "accounts"
    accounts = [d.name for d in accounts_dir.iterdir() 
                if d.is_dir() and d.name.startswith("Account_")]
    
    if not accounts:
        print("❌ 未找到任何账号")
        return
    
    print(f"\n📊 找到 {len(accounts)} 个账号:")
    for i, acc in enumerate(accounts, 1):
        print(f"  {i}. {acc}")
    
    # 选择账号
    print(f"\n请选择要测试的账号 (1-{len(accounts)}):")
    try:
        choice = int(input("> "))
        if choice < 1 or choice > len(accounts):
            print("❌ 无效选项")
            return
        
        account_name = accounts[choice - 1]
    except (ValueError, KeyboardInterrupt):
        print("\n❌ 已取消")
        return
    
    print(f"\n📝 将为账号 '{account_name}' 创建测试文章")
    print("⚠️  请确保自动发布代理已启动！")
    print("\n按 Enter 继续，Ctrl+C 取消...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ 已取消")
        return
    
    # 创建测试文章
    if create_test_article(account_name, base_dir):
        print("\n" + "="*60)
        print("✅ 测试文章已创建！")
        print("="*60)
        print("\n📌 接下来应该发生的事情:")
        print("  1. 代理检测到新文章（约 1-2 秒）")
        print("  2. 等待 5 秒后开始发布")
        print("  3. 自动打开浏览器")
        print("  4. 填充文章内容")
        print("  5. 等待你扫码确认")
        print("\n👀 请观察代理的日志输出...")
        print("📱 准备好手机扫码！")
        print("\n" + "="*60)
    else:
        print("\n❌ 测试失败")


if __name__ == "__main__":
    main()
