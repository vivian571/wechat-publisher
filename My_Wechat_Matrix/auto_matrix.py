#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Matrix Auto Scheduler
全自动矩阵发布脚本：每隔指定时间自动生成文章、封面并发布
"""

import os
import sys
import time
import json
import random
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# 代理设置（如需要）
PROXY_URL = "http://127.0.0.1:3067"
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL
os.environ["http_proxy"] = PROXY_URL
os.environ["https_proxy"] = PROXY_URL

# 尝试导入 AI 库
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI 库未安装，请运行: pip install openai")

# 智谱使用 OpenAI 兼容接口，不需要单独的库
ZHIPU_AVAILABLE = OPENAI_AVAILABLE  # 复用 OpenAI 库

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False



class MatrixAutoScheduler:
    """矩阵自动调度器"""
    
    def __init__(self, config_path: str = "matrix_config.json"):
        self.base_dir = Path(__file__).parent
        self.accounts_dir = self.base_dir / "accounts"
        
        # 加载配置
        config_file = self.base_dir / config_path
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            # 默认配置
            self.config = {
                "ai_provider": "zhipu",
                "api_config": {
                    "zhipu": {"api_key": "", "model": "glm-4-flash"},
                    "gemini": {"api_key": "", "model": "gemini-2.0-flash-exp"},
                    "openai": {"api_key": "", "model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1"}
                },
                "generation_settings": {"temperature": 0.8, "max_tokens": 3000}
            }
        
        # 初始化 AI 客户端
        self.ai_client = self._init_ai_client()
        
        # 各账号的主题池
        self.topic_pools = {}
        
        # 预设文章模板（当 API 不可用时使用）
        self.fallback_templates = self._load_fallback_templates()
    
    def _init_ai_client(self):
        """初始化 AI 客户端"""
        provider = self.config.get("ai_provider", "zhipu")
        
        # 优先使用智谱（通过 OpenAI 兼容接口）
        if provider == "zhipu" and ZHIPU_AVAILABLE:
            api_config = self.config.get("api_config", {}).get("zhipu", {})
            if api_config.get("api_key"):
                print(f"✅ 使用智谱 AI ({api_config.get('model', 'glm-4-flash')})")
                return OpenAI(
                    api_key=api_config["api_key"],
                    base_url="https://open.bigmodel.cn/api/paas/v4/"
                )
        
        # 其次使用 OpenAI
        if provider == "openai" and OPENAI_AVAILABLE:
            api_config = self.config["api_config"]["openai"]
            if api_config.get("api_key"):
                print(f"✅ 使用 OpenAI ({api_config.get('model', 'gpt-4o-mini')})")
                return OpenAI(
                    api_key=api_config["api_key"],
                    base_url=api_config.get("base_url", "https://api.openai.com/v1")
                )
        
        # 最后尝试 Gemini
        if provider == "gemini" and GEMINI_AVAILABLE:
            api_config = self.config["api_config"]["gemini"]
            if api_config.get("api_key"):
                print(f"✅ 使用 Gemini ({api_config.get('model', 'gemini-2.0-flash-exp')})")
                genai.configure(api_key=api_config["api_key"])
                return genai.GenerativeModel(api_config["model"])
        
        print("⚠️ AI 客户端初始化失败，将使用预设模板")
        return None
    
    def _load_fallback_templates(self) -> Dict:
        """预设模板已禁用，只使用 AI 生成"""
        return {}

    
    def get_enabled_accounts(self) -> List[Path]:
        """获取所有启用的账号目录"""
        accounts = []
        for account_dir in sorted(self.accounts_dir.iterdir()):
            if account_dir.is_dir() and account_dir.name.startswith("Account_"):
                # 检查是否有必要的配置文件
                if (account_dir / "system_prompt.md").exists():
                    accounts.append(account_dir)
        return accounts
    
    def load_account_config(self, account_dir: Path) -> Dict:
        """加载账号配置"""
        result = {"name": account_dir.name}
        
        # 读取系统提示词
        prompt_file = account_dir / "system_prompt.md"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                result["system_prompt"] = f.read()
        
        # 读取风格参考
        style_file = account_dir / "style_reference.txt"
        if style_file.exists():
            with open(style_file, 'r', encoding='utf-8') as f:
                result["style_reference"] = f.read()
        
        # 读取账号配置
        config_file = account_dir / "account_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                result["config"] = json.load(f)
        
        return result
    
    def generate_topic(self, account_config: Dict) -> str:
        """根据账号配置生成话题"""
        account_name = account_config["name"]
        
        # 根据账号类型生成不同的话题
        if "English" in account_name or "Tech" in account_name:
            # 技术/英语类：热门开源项目
            topics = [
                "最近爆火的开源项目", "AI工具推荐", "效率神器分享",
                "程序员必备工具", "2025年技术趋势", "自动化脚本技巧"
            ]
        elif "Life" in account_name:
            # 生活类：季节食材
            topics = [
                "冬季养生食材", "应季蔬菜推荐", "家常炖菜做法",
                "快手早餐", "一人食菜谱", "暖胃汤品"
            ]
        elif "CrossBorder" in account_name:
            # 跨境类
            topics = [
                "跨境电商选品", "亚马逊运营技巧", "独立站搭建",
                "海外仓储物流", "外贸谈判技巧"
            ]
        else:
            topics = ["今日分享", "干货推荐", "实用技巧"]
        
        return random.choice(topics)
    
    def generate_article(self, account_dir: Path, topic: str) -> Optional[str]:
        """使用 AI 生成文章，失败时使用预设模板"""
        account_config = self.load_account_config(account_dir)
        account_name = account_config["name"]
        
        print(f"   🧠 正在生成文章: {topic}")
        
        # 如果 AI 客户端不可用，直接使用预设模板
        if not self.ai_client:
            print("   ⚠️ AI 客户端不可用，使用预设模板")
            return self._use_fallback_template(account_dir, account_name)
        
        # 构建提示词
        system_prompt = account_config.get("system_prompt", "你是一位专业的内容创作者。")
        style_reference = account_config.get("style_reference", "")
        
        user_prompt = f"""请根据以下主题写一篇文章：「{topic}」

要求：
1. 字数控制在1500-2500字
2. 必须输出纯文本，严禁使用Markdown语法（如#、**、---等）
3. 第一行是标题
4. 第二行空行
5. 第三行开始是正文
6. 使用空行分段，可用emoji和序号增强可读性
7. 参考以下风格：
{style_reference[:1000]}
"""
        
        try:
            provider = self.config.get("ai_provider", "zhipu")
            
            if provider == "zhipu":
                # 智谱 AI
                model = self.config.get("api_config", {}).get("zhipu", {}).get("model", "glm-4-flash")
                response = self.ai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=3000
                )
                content = response.choices[0].message.content
                
            elif provider == "gemini":
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = self.ai_client.generate_content(
                    full_prompt,
                    generation_config={
                        "temperature": 0.8,
                        "max_output_tokens": 3000
                    },
                    request_options={"timeout": 600}
                )
                content = response.text
                
            else:  # openai
                model = self.config["api_config"]["openai"]["model"]
                response = self.ai_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=3000
                )
                content = response.choices[0].message.content
            
            # 保存到 output.txt
            output_file = account_dir / "output.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ 文章已生成: {output_file.name}")
            return content
            
        except Exception as e:
            print(f"   ❌ AI 生成失败: {e}")
            print(f"   📄 使用预设模板...")
            return self._use_fallback_template(account_dir, account_name)
    
    def _use_fallback_template(self, account_dir: Path, account_name: str) -> Optional[str]:
        """使用预设模板"""
        # 根据账号名称匹配模板
        template_key = None
        for key in self.fallback_templates.keys():
            if key in account_name:
                template_key = key
                break
        
        if template_key and self.fallback_templates.get(template_key):
            content = random.choice(self.fallback_templates[template_key])
            
            # 保存到 output.txt
            output_file = account_dir / "output.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ 已使用预设模板: {output_file.name}")
            return content
        else:
            print(f"   ❌ 未找到匹配的预设模板")
            return None
    
    def generate_cover(self, account_dir: Path, title: str) -> Optional[str]:
        """生成封面图片（暂时跳过，让发布脚本从正文选择）"""
        print(f"   🎨 封面：将从正文图片中选择")
        # 暂时跳过封面生成，wechat_auto_post.py 会自动从正文选择图片作为封面
        # 如果正文没有图片，可以手动上传或后续添加封面生成逻辑
        return None
    
    def publish_article(self, account_dir: Path) -> bool:
        """调用发布脚本发布文章"""
        account_name = account_dir.name
        print(f"   📤 正在发布文章...")
        print(f"   🔗 执行: python wechat_auto_post.py --account {account_name}")
        
        try:
            # 调用 wechat_auto_post.py - 不捕获输出，让用户看到扫码提示
            result = subprocess.run(
                ["python", "wechat_auto_post.py", "--account", account_name],
                cwd=str(self.base_dir),
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print(f"   ✅ 发布成功")
                return True
            else:
                print(f"   ⚠️ 发布返回非零状态码: {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   ⚠️ 发布超时")
            return False
        except Exception as e:
            print(f"   ❌ 发布失败: {e}")
            return False
    
    def process_account(self, account_dir: Path) -> bool:
        """处理单个账号的完整流程"""
        account_name = account_dir.name
        print(f"\n📁 处理账号: {account_name}")
        
        # 1. 生成话题
        account_config = self.load_account_config(account_dir)
        topic = self.generate_topic(account_config)
        print(f"   📝 话题: {topic}")
        
        # 2. 生成文章
        content = self.generate_article(account_dir, topic)
        if not content:
            return False
        
        # 3. 提取标题
        lines = content.strip().split('\n')
        title = lines[0].strip() if lines else "未命名文章"
        
        # 4. 生成封面
        self.generate_cover(account_dir, title)
        
        # 5. 发布文章
        success = self.publish_article(account_dir)
        
        # 6. 发布成功后清理
        if success:
            self._cleanup_after_publish(account_dir)
        
        return success
    
    def has_pending_content(self, account_dir: Path) -> bool:
        """检查账号目录是否有待发布的内容（output.txt 存在）"""
        output_file = account_dir / "output.txt"
        return output_file.exists()
    
    def publish_existing_content(self, account_dir: Path) -> bool:
        """发布已存在的内容（不生成新文章）"""
        account_name = account_dir.name
        print(f"\n📁 发布账号: {account_name}")
        
        output_file = account_dir / "output.txt"
        if not output_file.exists():
            print(f"   ⚠️ 没有待发布内容，跳过")
            return False
        
        # 读取文章内容
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.strip().split('\n')
        title = lines[0].strip() if lines else "未命名文章"
        print(f"   📝 标题: {title[:30]}...")
        
        # 检查是否有封面
        cover_exists = any((account_dir / f).exists() for f in 
                          ["cover.png", "cover.jpg", "cover_fixed.png", "cover_fixed.jpg", "cover_generated.jpg"])
        if cover_exists:
            print(f"   🖼️ 封面已就绪")
        else:
            print(f"   🎨 封面：将从正文图片中选择")
        
        # 发布
        success = self.publish_article(account_dir)
        
        # 发布成功后清理
        if success:
            self._cleanup_after_publish(account_dir)
        
        return success
    
    def _cleanup_after_publish(self, account_dir: Path):
        """发布成功后清理临时文件"""
        print(f"   🧹 清理临时文件...")
        patterns = ["output.txt", "output.html", 
                   "cover.png", "cover.jpg", "cover_fixed.png", 
                   "cover_fixed.jpg", "cover_generated.jpg"]
        for pattern in patterns:
            file_path = account_dir / pattern
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"      🗑️ 已删除: {pattern}")
                except:
                    pass
    
    def run_once(self):
        """执行一轮发布（所有账号）"""
        print(f"\n{'='*60}")
        print(f"🚀 开始执行矩阵发布 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        accounts = self.get_enabled_accounts()
        print(f"📊 找到 {len(accounts)} 个账号\n")
        
        success_count = 0
        for account_dir in accounts:
            try:
                if self.process_account(account_dir):
                    success_count += 1
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
            
            # 账号之间间隔，避免被限制
            time.sleep(30)
        
        print(f"\n{'='*60}")
        print(f"✅ 本轮完成: 成功 {success_count}/{len(accounts)}")
        print(f"{'='*60}\n")
    
    def run_watch_mode(self, interval_minutes: int = 60):
        """检测模式：每隔指定时间检查并发布有新内容的账号"""
        print(f"\n{'='*60}")
        print(f"👁️ WeChat Matrix 检测发布模式")
        print(f"⏱️  检测间隔: {interval_minutes} 分钟")
        print(f"📌 只发布有 output.txt 的账号，发布后自动清理")
        print(f"🛑 按 Ctrl+C 停止")
        print(f"{'='*60}\n")
        
        try:
            while True:
                current_time = datetime.now().strftime('%H:%M:%S')
                accounts = self.get_enabled_accounts()
                
                # 检查哪些账号有待发布内容
                pending_accounts = [acc for acc in accounts if self.has_pending_content(acc)]
                
                if pending_accounts:
                    print(f"\n[{current_time}] 🔍 检测到 {len(pending_accounts)} 个账号有待发布内容")
                    
                    success_count = 0
                    for account_dir in pending_accounts:
                        try:
                            if self.publish_existing_content(account_dir):
                                success_count += 1
                        except Exception as e:
                            print(f"   ❌ 发布失败: {e}")
                        time.sleep(30)
                    
                    print(f"\n✅ 本轮完成: 成功 {success_count}/{len(pending_accounts)}")
                else:
                    print(f"[{current_time}] 😴 无待发布内容，等待下一次检测...")
                
                # 等待下一轮
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 检测模式已停止")
    
    def run_loop(self, interval_minutes: int = 60):
        """循环执行"""
        print(f"\n{'='*60}")
        print(f"🔄 WeChat Matrix 自动调度器")
        print(f"⏱️  执行间隔: {interval_minutes} 分钟")
        print(f"🛑 按 Ctrl+C 停止")
        print(f"{'='*60}\n")
        
        try:
            while True:
                self.run_once()
                
                next_run = datetime.now().strftime('%H:%M:%S')
                print(f"⏳ 下一轮将在 {interval_minutes} 分钟后执行...")
                print(f"   （当前时间: {next_run}）\n")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 调度器已停止")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="WeChat Matrix 自动调度器")
    parser.add_argument(
        "--once",
        action="store_true",
        help="只执行一轮，不循环"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="检测模式：只发布有 output.txt 的账号，发布后自动清理"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="执行间隔（分钟），默认60分钟"
    )
    parser.add_argument(
        "--account",
        type=str,
        help="只处理指定账号"
    )
    
    args = parser.parse_args()
    
    scheduler = MatrixAutoScheduler()
    
    if args.account:
        # 只处理指定账号
        account_dir = scheduler.accounts_dir / args.account
        if account_dir.exists():
            scheduler.process_account(account_dir)
        else:
            print(f"❌ 账号不存在: {args.account}")
    elif args.watch:
        # 检测模式
        scheduler.run_watch_mode(interval_minutes=args.interval)
    elif args.once:
        scheduler.run_once()
    else:
        scheduler.run_loop(interval_minutes=args.interval)


if __name__ == "__main__":
    main()
