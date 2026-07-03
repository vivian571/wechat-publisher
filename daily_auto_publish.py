"""
公众号矩阵每日自动发布主控脚本（完整版）
每天晚上8点自动执行：内容生成 → 封面图生成 → 文章发布

包含三个项目的自动化流程：
1. My_Wechat_Matrix: 公众号矩阵内容生成和发布
2. temp/wechat_publisher: 多领域爆款文章生成
3. OmniPublish: 国际技术平台内容生成和发布
"""

import os
import sys
import time
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List

# 配置代理（如果需要）
PROXY_URL = "http://127.0.0.1:3067"
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

# 配置日志
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"daily_publish_{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class DailyPublisher:
    """每日自动发布管理器（包含内容生成）"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.success_count = 0
        self.failed_count = 0
        self.results = []
        
        # 初始化 AI 客户端
        self.ai_client = None
        self._init_ai_client()
        
    def _init_ai_client(self):
        """初始化 AI 客户端（支持多厂商）"""
        try:
            # 加载配置
            config_path = self.base_dir / "My_Wechat_Matrix" / "matrix_config.json"
            if not config_path.exists():
                logger.warning("⚠️ 未找到 matrix_config.json，尝试使用环境变量")
                self.provider = "openai"
                self.api_key = os.environ.get('OPENAI_API_KEY')
                self.base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')
                self.model = "gpt-4o-mini"
            else:
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                self.provider = self.config.get("ai_provider", "openai")
                api_config = self.config.get("api_config", {}).get(self.provider, {})
                self.api_key = api_config.get("api_key")
                self.model = api_config.get("model")
                self.base_url = api_config.get("base_url")

            if not self.api_key:
                logger.warning(f"⚠️ 未找到 {self.provider} 的 API 密钥")
                return

            if self.provider == "openai":
                from openai import OpenAI
                import httpx
                http_client = httpx.Client(proxy=PROXY_URL)
                self.ai_client = OpenAI(
                    api_key=self.api_key, 
                    base_url=self.base_url or "https://api.openai.com/v1",
                    http_client=http_client
                )
                logger.info("✅ OpenAI 客户端初始化成功")
            elif self.provider == "zhipu":
                from zhipuai import ZhipuAI
                self.ai_client = ZhipuAI(api_key=self.api_key)
                # 智谱通常不需要代理访问，如果需要也可以设置
                logger.info("✅ 智谱 AI 客户端初始化成功")
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.ai_client = genai.GenerativeModel(self.model or "gemini-pro")
                logger.info("✅ Gemini 客户端初始化成功")
                
        except Exception as e:
            logger.warning(f"⚠️ AI 客户端初始化失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    def _call_ai(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """统一的 AI 调用接口"""
        if not self.ai_client:
            raise Exception("AI 客户端未初始化")

        if self.provider == "openai" or self.provider == "zhipu":
            response = self.ai_client.chat.completions.create(
                model=self.model or ("gpt-4o-mini" if self.provider == "openai" else "glm-4-flash"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        elif self.provider == "gemini":
            prompt = f"{system_prompt}\n\n{user_prompt}"
            response = self.ai_client.generate_content(prompt)
            return response.text
        return ""
    
    def log_result(self, task_name: str, success: bool, message: str = ""):
        """记录任务结果"""
        status = "✅ 成功" if success else "❌ 失败"
        logger.info(f"{status} - {task_name}: {message}")
        
        self.results.append({
            "task": task_name,
            "success": success,
            "message": message,
            "time": datetime.now().strftime('%H:%M:%S')
        })
        
        if success:
            self.success_count += 1
        else:
            self.failed_count += 1
    
    def run_command(self, cmd: list, cwd: str, task_name: str, timeout: int = 600) -> bool:
        """执行命令并记录结果"""
        try:
            logger.info(f"🚀 开始执行: {task_name}")
            logger.info(f"   命令: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=False,  # 不使用 text=True 避免默认编码错误
                timeout=timeout
            )
            
            # 使用更稳健的解码过程
            def decode_output(output_bytes):
                if not output_bytes: return ""
                for enc in ['utf-8', 'gbk', 'utf-16']:
                    try:
                        return output_bytes.decode(enc)
                    except UnicodeDecodeError:
                        continue
                return output_bytes.decode('utf-8', errors='ignore')

            stdout = decode_output(result.stdout)
            stderr = decode_output(result.stderr)
            
            if result.returncode == 0:
                self.log_result(task_name, True, "执行成功")
                return True
            else:
                error_msg = stderr[:200] if stderr else "未知错误"
                self.log_result(task_name, False, error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            self.log_result(task_name, False, f"超时（>{timeout}秒）")
            return False
        except Exception as e:
            self.log_result(task_name, False, str(e))
            return False
    
    def search_hot_topics(self) -> str:
        """搜索今日热点话题"""
        logger.info("🔍 正在搜索今日热点话题...")
        
        today = datetime.now().strftime('%Y年%m月%d日')
        
        if self.ai_client:
            try:
                content = self._call_ai(
                    system_prompt="你是一个新闻编辑，擅长发现今日热点。",
                    user_prompt=f"""请列出{today}的5个热门话题，涵盖以下领域：
1. 科技/AI
2. 跨境电商/出海
3. 生活/养生
4. 职场/成长
5. 英语学习

格式：每个话题一行，简洁描述。""",
                    max_tokens=500
                )
                logger.info(f"📰 今日热点:\n{content}")
                return content
            except Exception as e:
                logger.warning(f"⚠️ 搜索热点失败: {e}")
        
        # 默认热点
        return f"{today}热点：AI技术发展、跨境电商新趋势、冬季养生、职场效率、英语学习方法"
    
    # ==========================================
    # 阶段1：内容生成
    # ==========================================
    
    def generate_wechat_matrix_content(self, hot_topics: str):
        """生成公众号矩阵内容（My_Wechat_Matrix）"""
        logger.info("\n" + "="*60)
        logger.info("📝 阶段1.1: 生成公众号矩阵内容")
        logger.info("="*60)
        
        wechat_dir = self.base_dir / "My_Wechat_Matrix"
        
        # 使用已有的 generator.py 生成内容
        cmd = ["python", "generator.py", "--all", "--topic", hot_topics[:100]]
        self.run_command(cmd, str(wechat_dir), "公众号矩阵-内容生成", timeout=600)
    
    def generate_multi_domain_content(self, hot_topics: str):
        """生成多领域爆款文章（temp/wechat_publisher）"""
        logger.info("\n" + "="*60)
        logger.info("📝 阶段1.2: 生成多领域爆款文章")
        logger.info("="*60)
        
        publisher_dir = self.base_dir / "temp" / "wechat_publisher"
        prompts_dir = publisher_dir / "Prompts"
        documents_dir = publisher_dir / "documents"
        
        if not prompts_dir.exists():
            self.log_result("多领域文章-生成", False, "Prompts 目录不存在")
            return
        
        # 领域映射
        domain_mapping = {
            "AI流习社提示词.md": "AI流习社",
            "开源智核提示词.md": "开源智核",
            "平凡日子记提示词.md": "平凡日子记"
        }
        
        for prompt_file, domain_name in domain_mapping.items():
            prompt_path = prompts_dir / prompt_file
            if not prompt_path.exists():
                continue
            
            try:
                # 读取提示词
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_template = f.read()
                
                # 生成内容
                if self.ai_client:
                    logger.info(f"📝 正在生成 {domain_name} 文章...")
                    
                    content = self._call_ai(
                        system_prompt=prompt_template,
                        user_prompt=f"请基于今日热点写一篇文章：\n{hot_topics}",
                        max_tokens=3000
                    )
                    
                    # 保存到对应目录
                    output_dir = documents_dir / domain_name
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    today_str = datetime.now().strftime('%Y%m%d')
                    output_file = output_dir / f"daily_{today_str}.md"
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.log_result(f"多领域文章-{domain_name}", True, str(output_file))
                else:
                    self.log_result(f"多领域文章-{domain_name}", False, "AI 客户端未初始化")
                    
            except Exception as e:
                self.log_result(f"多领域文章-{domain_name}", False, str(e))
    
    def generate_international_content(self):
        """生成国际技术平台内容（OmniPublish）"""
        logger.info("\n" + "="*60)
        logger.info("📝 阶段1.3: 生成国际技术文章")
        logger.info("="*60)
        
        omnipublish_dir = self.base_dir / "OmniPublish"
        articles_dir = omnipublish_dir / "articles"
        
        if not articles_dir.exists():
            articles_dir.mkdir(parents=True, exist_ok=True)
        
        if not self.ai_client:
            self.log_result("国际文章-生成", False, "AI 客户端未初始化")
            return
        
        try:
            # 搜索国际技术热点
            logger.info("🔍 搜索国际技术编程热点...")
            
            response = self.ai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{
                    "role": "user",
                    "content": """List 3 trending topics in tech/programming for January 2026. 
Focus on: AI tools, open source projects, developer productivity.
Format: Just the topic names, one per line."""
                }],
                temperature=0.7,
                max_tokens=200
            )
            
            topics = response.choices[0].message.content.strip().split('\n')
            logger.info(f"📰 国际热点: {topics}")
            
            # 为第一个热点生成文章
            if topics:
                topic = topics[0].strip()
                logger.info(f"📝 正在生成国际技术文章: {topic}")
                
                content = self._call_ai(
                    system_prompt="You are a professional tech blogger.",
                    user_prompt=f"""Write a technical blog post about: {topic}

Requirements:
- Target audience: developers
- Length: 800-1200 words
- Include practical examples
- Conversational but professional tone

Format the output as a Dev.to/Hashnode compatible markdown article with proper frontmatter:

---
title: "Your Title"
published: true
description: "Brief description"
tags: tag1, tag2, tag3, tag4
cover_image: https://images.pexels.com/photos/8386440/pexels-photo-8386440.jpeg
canonical_url: null
---

[Article content here]""",
                    max_tokens=2500
                )
                
                # 保存文章
                today_str = datetime.now().strftime('%Y%m%d')
                slug = topic.lower().replace(' ', '-')[:50]
                output_file = articles_dir / f"{slug}-{today_str}.md"
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.log_result("国际文章-生成", True, str(output_file))
                
        except Exception as e:
            self.log_result("国际文章-生成", False, str(e))
    
    def generate_cover_images(self):
        """生成封面图片"""
        logger.info("\n" + "="*60)
        logger.info("🖼️ 阶段1.4: 生成封面图片")
        logger.info("="*60)
        
        wechat_dir = self.base_dir / "My_Wechat_Matrix"
        accounts_dir = wechat_dir / "accounts"
        
        # 检查是否有图片生成脚本
        image_gen_script = wechat_dir / "image_generator.py"
        
        if image_gen_script.exists():
            for account_dir in accounts_dir.iterdir():
                if account_dir.is_dir():
                    cmd = ["python", "image_generator.py", "--account", account_dir.name]
                    self.run_command(cmd, str(wechat_dir), f"封面图-{account_dir.name}", timeout=120)
        else:
            logger.info("⏭️ 跳过封面图生成（未找到 image_generator.py）")
    
    # ==========================================
    # 阶段2：发布
    # ==========================================
    
    def publish_wechat_accounts(self, target_account_name: str = None):
        """发布公众号矩阵"""
        logger.info("\n" + "="*60)
        logger.info("📱 阶段2.1: 发布公众号矩阵")
        logger.info("="*60)
        
        all_accounts = [
            "Account_A_CrossBorder",
            "Account_B_English",
            "Account_C_Life",
            "Account_D_Tech"
        ]
        
        # 如果指定了账号且在列表中，则只发布该账号
        accounts_to_publish = [target_account_name] if target_account_name and target_account_name in all_accounts else all_accounts
        
        wechat_dir = self.base_dir / "My_Wechat_Matrix"
        
        for account in accounts_to_publish:
            account_dir = wechat_dir / "accounts" / account
            if not account_dir.exists():
                self.log_result(f"公众号-{account}", False, "账号目录不存在")
                continue
            
            # 柔性检查：只要有 .md, .html 或 .txt 任一即可
            content_found = any(account_dir.glob("*.md")) or \
                            (account_dir / "output.html").exists() or \
                            (account_dir / "output.txt").exists()
            
            if not content_found:
                logger.info(f"⏭️  账号 {account} 未检测到今日生成内容，已跳过。")
                self.log_result(f"公众号-{account}", True, "跳过（无内容）")
                continue
            
            logger.info(f"🚀 正在发布账号: {account}")
            cmd = ["python", "wechat_auto_post.py", "--account", account]
            self.run_command(cmd, str(wechat_dir), f"公众号-{account}", timeout=300)
            
            time.sleep(5)
    
    def publish_international_platforms(self):
        """发布国际平台（Dev.to + Hashnode）"""
        logger.info("\n" + "="*60)
        logger.info("🌍 阶段2.2: 发布国际平台")
        logger.info("="*60)
        
        omnipublish_dir = self.base_dir / "OmniPublish"
        articles_dir = omnipublish_dir / "articles"
        
        articles = list(articles_dir.glob("*.md"))
        
        if not articles:
            self.log_result("国际平台", False, "没有找到文章")
            return
        
        # 只发布今天生成的文章
        today_str = datetime.now().strftime('%Y%m%d')
        today_articles = [a for a in articles if today_str in a.name]
        
        if not today_articles:
            today_articles = articles[:1]  # 如果没有今天的，发布最新的一篇
        
        for article in today_articles:
            cmd = [
                "python", "main.py",
                "--file", f"articles/{article.name}",
                "--skip-validation"
            ]
            
            self.run_command(cmd, str(omnipublish_dir), f"国际平台-{article.stem}", timeout=60)
            time.sleep(3)
    
    # ==========================================
    # 报告生成
    # ==========================================
    
    def generate_summary_report(self):
        """生成执行摘要报告"""
        logger.info("\n" + "="*60)
        logger.info("📊 执行摘要报告")
        logger.info("="*60)
        
        total = self.success_count + self.failed_count
        success_rate = (self.success_count / total * 100) if total > 0 else 0
        
        logger.info(f"总任务数: {total}")
        logger.info(f"成功: {self.success_count}")
        logger.info(f"失败: {self.failed_count}")
        logger.info(f"成功率: {success_rate:.1f}%")
        
        if self.failed_count > 0:
            logger.info("\n❌ 失败任务列表:")
            for result in self.results:
                if not result['success']:
                    logger.info(f"   - {result['task']}: {result['message']}")
        
        # 保存报告
        report_file = log_dir / f"summary_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"公众号矩阵每日发布报告\n")
            f.write(f"日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"总任务数: {total}\n")
            f.write(f"成功: {self.success_count}\n")
            f.write(f"失败: {self.failed_count}\n")
            f.write(f"成功率: {success_rate:.1f}%\n\n")
            
            f.write("详细结果:\n")
            for result in self.results:
                status = "✅" if result['success'] else "❌"
                f.write(f"{status} [{result['time']}] {result['task']}: {result['message']}\n")
        
        logger.info(f"\n📄 详细报告已保存: {report_file}")
    
    # ==========================================
    # 主流程
    # ==========================================
    
    def run(self, target_account: str = None):
        """执行完整流程"""
        logger.info("="*60)
        logger.info("🚀 公众号矩阵每日自动发布开始（完整版）")
        logger.info(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if target_account:
            logger.info(f"🎯 聚焦模式: 仅针对 {target_account} 执行操作")
        logger.info("="*60)
        
        try:
            # 仅在非特定账号模式下搜索热点
            hot_topics = ""
            if not target_account:
                hot_topics = self.search_hot_topics()
            else:
                logger.info("⏭️  检测到聚焦模式，跳过热点搜索。")
            
            # ====== 阶段1: 内容生成 ======
            logger.info("\n" + "🔷"*30)
            logger.info("📝 阶段1: 内容生成")
            logger.info("🔷"*30)
            
            # 这里默认跳过，因为用户可能已经手动准备好了内容
            if not target_account:
                # 1.1 生成公众号矩阵内容
                self.generate_wechat_matrix_content(hot_topics)
                
                # 1.2 生成多领域爆款文章
                self.generate_multi_domain_content(hot_topics)
                
                # 1.3 生成国际技术文章
                self.generate_international_content()
                
                # 1.4 生成封面图片
                self.generate_cover_images()
            else:
                logger.info("⏭️  检测到聚焦模式，跳过全局生成，直接进入发布阶段。")
            
            # ====== 阶段2: 发布 ======
            logger.info("\n" + "🔶"*30)
            logger.info("📤 阶段2: 发布")
            logger.info("🔶"*30)
            
            # 2.1 发布公众号矩阵 (支持单账号)
            self.publish_wechat_accounts(target_account)
            
            # 2.2 发布国际平台 (仅在非特定账号模式下执行)
            if not target_account:
                self.publish_international_platforms()
            
            # ====== 阶段3: 报告 ======
            self.generate_summary_report()
            
            logger.info("\n" + "="*60)
            logger.info("✅ 公众号矩阵每日自动发布完成")
            logger.info("="*60)
            
        except Exception as e:
            logger.error(f"❌ 执行过程中发生异常: {e}")
            import traceback
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="公众号矩阵每日自动发布主控脚本")
    parser.add_argument("--account", type=str, help="指定要发布的账号名称")
    parser.add_argument("--dry-run", action="store_true", help="模拟测试模式")
    
    args = parser.parse_args()
    
    publisher = DailyPublisher()
    publisher.run(target_account=args.account)
