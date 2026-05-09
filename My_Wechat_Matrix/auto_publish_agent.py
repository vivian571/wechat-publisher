#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Matrix Auto-Publish Agent
自动化子代理：监控文章生成并自动触发网页发布流程

功能：
1. 监控 accounts 目录下的 output.txt 文件变化
2. 检测到新文章后自动调用 wechat_auto_post.py 发布
3. 支持多账号并发/串行发布
4. 智能去重，避免重复发布
"""

import os
import sys
import time
import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class ArticlePublishAgent(FileSystemEventHandler):
    """文章发布代理 - 监控文件变化并自动发布"""
    
    def __init__(self, base_dir: Path, config_path: str = "agent_config.json"):
        """
        初始化发布代理
        
        Args:
            base_dir: My_Wechat_Matrix 项目根目录
            config_path: 代理配置文件路径
        """
        self.base_dir = base_dir
        self.accounts_dir = base_dir / "accounts"
        self.config_path = base_dir / config_path
        
        # 初始化已发布哈希集合（必须在 _load_config 之前）
        self.published_hashes: Set[str] = set()
        
        # 加载或创建配置
        self.config = self._load_config()
        
        # 更新已发布哈希集合
        self.published_hashes = set(self.config.get("published_hashes", []))
        
        # 发布队列（账号名 -> 文章路径）
        self.publish_queue: Dict[str, Path] = {}
        
        # 正在发布的账号
        self.publishing_accounts: Set[str] = set()
        
        print(f"✅ 发布代理已初始化")
        print(f"📁 监控目录: {self.accounts_dir}")
        print(f"📊 已发布文章数: {len(self.published_hashes)}")
    
    def _load_config(self) -> Dict:
        """加载代理配置"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # 默认配置
            default_config = {
                "enabled": True,
                "auto_publish": True,
                "publish_delay_seconds": 5,  # 检测到文章后等待N秒再发布
                "concurrent_publish": False,  # 是否并发发布（建议False避免冲突）
                "published_hashes": [],
                "excluded_accounts": []  # 排除的账号列表
            }
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict = None):
        """保存配置"""
        if config is None:
            config = self.config
        
        # 更新已发布哈希列表
        config["published_hashes"] = list(self.published_hashes)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件内容的哈希值"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except Exception as e:
            print(f"⚠️ 计算哈希失败: {e}")
            return ""
    
    def _is_published(self, file_path: Path) -> bool:
        """检查文章是否已发布"""
        file_hash = self._get_file_hash(file_path)
        return file_hash in self.published_hashes
    
    def _mark_as_published(self, file_path: Path):
        """标记文章为已发布"""
        file_hash = self._get_file_hash(file_path)
        if file_hash:
            self.published_hashes.add(file_hash)
            self._save_config()
    
    def _get_account_name(self, file_path: Path) -> Optional[str]:
        """从文件路径提取账号名称"""
        try:
            # 路径格式: .../accounts/Account_A_CrossBorder/output.txt
            parts = file_path.parts
            accounts_index = parts.index("accounts")
            account_name = parts[accounts_index + 1]
            
            # 检查是否在排除列表中
            if account_name in self.config.get("excluded_accounts", []):
                return None
            
            return account_name
        except (ValueError, IndexError):
            return None
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
        
        self._handle_file_change(event.src_path)
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        self._handle_file_change(event.src_path)
    
    def _handle_file_change(self, file_path_str: str):
        """处理文件变化"""
        file_path = Path(file_path_str)
        
        # 只处理 output.txt 或 .md 文件
        if file_path.name not in ["output.txt"] and file_path.suffix != ".md":
            return
        
        # 排除 system_prompt.md
        if "system_prompt" in file_path.name:
            return
        
        # 获取账号名称
        account_name = self._get_account_name(file_path)
        if not account_name:
            return
        
        # 检查是否已发布
        if self._is_published(file_path):
            print(f"⏭️  [{account_name}] 文章已发布过，跳过")
            return
        
        # 检查文件是否有效
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or len(content) < 100:  # 内容太短，可能还在写入
                    return
        except Exception as e:
            print(f"⚠️ 读取文件失败: {e}")
            return
        
        # 添加到发布队列
        current_time = datetime.now().strftime('%H:%M:%S')
        print(f"\n[{current_time}] 🔔 检测到新文章: {account_name}/{file_path.name}")
        
        self.publish_queue[account_name] = file_path
        
        # 如果启用自动发布，触发发布
        if self.config.get("auto_publish", True):
            delay = self.config.get("publish_delay_seconds", 5)
            print(f"⏳ 将在 {delay} 秒后发布...")
            time.sleep(delay)
            self._process_queue()
    
    def _process_queue(self):
        """处理发布队列"""
        if not self.publish_queue:
            return
        
        # 串行发布（推荐）
        if not self.config.get("concurrent_publish", False):
            for account_name, file_path in list(self.publish_queue.items()):
                if account_name in self.publishing_accounts:
                    print(f"⏸️  [{account_name}] 正在发布中，跳过")
                    continue
                
                self._publish_article(account_name, file_path)
                del self.publish_queue[account_name]
        
        # 并发发布（不推荐，可能导致浏览器冲突）
        else:
            import threading
            for account_name, file_path in list(self.publish_queue.items()):
                if account_name in self.publishing_accounts:
                    continue
                
                thread = threading.Thread(
                    target=self._publish_article,
                    args=(account_name, file_path)
                )
                thread.start()
                del self.publish_queue[account_name]
    
    def _publish_article(self, account_name: str, file_path: Path) -> bool:
        """
        发布文章
        
        Args:
            account_name: 账号名称
            file_path: 文章文件路径
            
        Returns:
            是否发布成功
        """
        self.publishing_accounts.add(account_name)
        
        try:
            print(f"\n{'='*60}")
            print(f"📤 开始发布: {account_name}")
            print(f"📄 文件: {file_path.name}")
            print(f"{'='*60}\n")
            
            # 调用 wechat_auto_post.py
            result = subprocess.run(
                [sys.executable, "wechat_auto_post.py", "--account", account_name],
                cwd=str(self.base_dir),
                timeout=600,  # 10分钟超时
                capture_output=False  # 不捕获输出，让用户看到扫码提示
            )
            
            if result.returncode == 0:
                print(f"\n✅ [{account_name}] 发布成功！")
                self._mark_as_published(file_path)
                
                # 记录发布日志
                self._log_publish(account_name, file_path, success=True)
                
                return True
            else:
                print(f"\n⚠️ [{account_name}] 发布返回非零状态码: {result.returncode}")
                self._log_publish(account_name, file_path, success=False, 
                                error=f"返回码: {result.returncode}")
                return False
        
        except subprocess.TimeoutExpired:
            print(f"\n⚠️ [{account_name}] 发布超时")
            self._log_publish(account_name, file_path, success=False, error="超时")
            return False
        
        except Exception as e:
            print(f"\n❌ [{account_name}] 发布失败: {e}")
            self._log_publish(account_name, file_path, success=False, error=str(e))
            return False
        
        finally:
            self.publishing_accounts.remove(account_name)
    
    def _log_publish(self, account_name: str, file_path: Path, 
                     success: bool, error: str = ""):
        """记录发布日志"""
        log_file = self.base_dir / "auto_publish_agent.log"
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "SUCCESS" if success else "FAILED"
        
        log_entry = {
            "timestamp": timestamp,
            "account": account_name,
            "file": str(file_path),
            "status": status,
            "error": error
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"⚠️ 写入日志失败: {e}")
    
    def run(self):
        """启动监控"""
        print(f"\n{'='*60}")
        print(f"🤖 WeChat Matrix 自动发布代理")
        print(f"{'='*60}")
        print(f"📁 监控目录: {self.accounts_dir}")
        print(f"🔄 自动发布: {'启用' if self.config.get('auto_publish') else '禁用'}")
        print(f"⏱️  发布延迟: {self.config.get('publish_delay_seconds')}秒")
        print(f"🚀 发布模式: {'并发' if self.config.get('concurrent_publish') else '串行'}")
        print(f"🛑 按 Ctrl+C 停止")
        print(f"{'='*60}\n")
        
        # 创建观察者
        observer = Observer()
        observer.schedule(self, str(self.accounts_dir), recursive=True)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n🛑 正在停止代理...")
            observer.stop()
        
        observer.join()
        print(f"✅ 代理已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat Matrix 自动发布代理")
    parser.add_argument(
        "--config",
        type=str,
        default="agent_config.json",
        help="配置文件路径"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="重置已发布记录"
    )
    
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent
    
    # 重置已发布记录
    if args.reset:
        config_path = base_dir / args.config
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            config["published_hashes"] = []
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print("✅ 已重置发布记录")
        return
    
    # 启动代理
    agent = ArticlePublishAgent(base_dir, args.config)
    agent.run()


if __name__ == "__main__":
    main()
