#!/usr/bin/env python3

import os
import time
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/ax/wechat-publisher/international_publish.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class InternationalArticlePublisher:
    """国际平台文章自动发布器"""
    
    def __init__(self):
        self.articles_dir = Path("/Users/ax/wechat-publisher/OmniPublish/articles")
        self.video_dir = Path("/Users/ax/wechat-publisher/social-auto-upload/videoFile")
        self.published_log = Path("/Users/ax/wechat-publisher/international_published.log")
        self.processed_log = Path("/Users/ax/wechat-publisher/international_processed.log")
        
        # 国际平台配置（使用现有支持的tiktok，其他平台模拟）
        self.international_platforms = {
            'tiktok': {
                'enabled': True,
                'account': 'main',
                'description': 'Quick tech tips and AI trends',
                'real_platform': 'tiktok'
            },
            'youtube': {
                'enabled': True,
                'account': 'main', 
                'description': 'Tech insights and AI developments',
                'real_platform': 'tiktok'  # 使用tiktok作为测试平台
            },
            'instagram': {
                'enabled': True,
                'account': 'main',
                'description': 'Tech content and programming insights', 
                'real_platform': 'tiktok'  # 使用tiktok作为测试平台
            }
        }
        
        # 文件监控配置
        self.check_interval = 300  # 5分钟检查一次
        self.max_retry_count = 3
        self.retry_delay = 60  # 重试延迟（秒）
        
    def get_new_articles(self) -> List[Path]:
        """获取新文章列表"""
        if not self.articles_dir.exists():
            logger.warning(f"文章目录不存在: {self.articles_dir}")
            return []
        
        # 获取所有带日期的文章文件
        all_articles = list(self.articles_dir.glob("2026-*.md"))
        
        # 获取已处理的文章
        processed_articles = self.get_processed_articles()
        
        # 筛选新文章
        new_articles = [
            article for article in all_articles 
            if str(article) not in processed_articles
        ]
        
        logger.info(f"发现 {len(new_articles)} 篇新文章，总共 {len(all_articles)} 篇")
        return new_articles
    
    def get_processed_articles(self) -> set:
        """获取已处理的文章列表"""
        if not self.processed_log.exists():
            return set()
        
        try:
            with open(self.processed_log, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f.read().splitlines() if line.strip())
        except Exception as e:
            logger.error(f"读取处理记录失败: {e}")
            return set()
    
    def mark_article_processed(self, article_path: Path, status: str = "success"):
        """标记文章为已处理"""
        try:
            with open(self.processed_log, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp}|{status}|{article_path}\n")
        except Exception as e:
            logger.error(f"记录处理状态失败: {e}")
    
    async def convert_article_to_video(self, article_path: Path) -> Optional[Path]:
        """将文章转换为视频"""
        try:
            logger.info(f"开始转换文章: {article_path.name}")
            
            # 运行文章转换脚本
            cmd = [
                'python3', '/Users/ax/wechat-publisher/auto_publish_articles.py',
                '--single', str(article_path)
            ]
            
            # 修改脚本以支持单文件处理
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd='/Users/ax/wechat-publisher'
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"文章转换成功: {article_path.name}")
                
                # 查找最新生成的视频文件
                video_files = sorted(self.video_dir.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True)
                
                if video_files:
                    latest_video = video_files[0]
                    # 检查是否是最新生成的（1分钟内）
                    file_age = time.time() - latest_video.stat().st_mtime
                    if file_age < 300:  # 5分钟内
                        return latest_video
                
                return None
            else:
                logger.error(f"文章转换失败: {article_path.name}")
                logger.error(f"错误信息: {stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"转换文章失败 {article_path}: {e}")
            return None
    
    async def publish_to_international_platforms(self, video_path: Path, article_path: Path) -> Dict[str, bool]:
        """发布到国际平台"""
        results = {}
        
        logger.info(f"开始发布视频到国际平台: {video_path.name}")
        
        # 获取文章信息用于生成标题和描述
        article_title = self.extract_article_title(article_path)
        
        for platform, config in self.international_platforms.items():
            if not config['enabled']:
                continue
            
            try:
                logger.info(f"发布到 {platform}...")
                
                # 构建发布命令
                publish_cmd = self.build_publish_command(platform, video_path, article_title, config)
                
                # 执行发布
                success = await self.execute_publish_command(publish_cmd, platform)
                results[platform] = success
                
                if success:
                    logger.info(f"✅ {platform} 发布成功")
                else:
                    logger.error(f"❌ {platform} 发布失败")
                
                # 平台间延迟，避免触发限制
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"发布到 {platform} 失败: {e}")
                results[platform] = False
        
        return results
    
    def extract_article_title(self, article_path: Path) -> str:
        """从文章文件中提取标题"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试提取Markdown标题
            import re
            title_match = re.search(r'^#\s+\[?([^\]\n]+)\]?', content)
            if title_match:
                return title_match.group(1).strip()
            
            # 如果没有找到标题，使用文件名
            return article_path.stem.replace('-', ' ').replace('_', ' ')
            
        except Exception as e:
            logger.error(f"提取文章标题失败: {e}")
            return article_path.stem
    
    def build_publish_command(self, platform: str, video_path: Path, title: str, config: Dict) -> List[str]:
        """构建发布命令"""
        # 使用实际支持的平台（tiktok）
        real_platform = config.get('real_platform', platform)
        
        # 生成适合国际平台的标题和描述
        international_title = self.generate_international_title(title)
        description = self.generate_international_description(title, platform)
        
        # 使用现有的发布系统 - 注意cli_main.py的参数格式
        base_cmd = [
            'python3', '/Users/ax/wechat-publisher/social-auto-upload/cli_main.py',
            real_platform, config['account'], 'upload', str(video_path)
        ]
        
        return base_cmd
    
    def generate_international_title(self, original_title: str) -> str:
        """生成适合国际平台的标题"""
        # 简化标题，适合国际观众
        title = original_title.replace('2026', '').strip()
        
        # 添加吸引人的元素
        if 'AI' in title or '人工智能' in title:
            return f"🔥 {title} - Must Watch for Tech Enthusiasts!"
        elif 'programming' in title.lower() or 'code' in title.lower():
            return f"💻 {title} - Essential Developer Guide"
        elif 'performance' in title.lower():
            return f"⚡ {title} - Optimization Tips Inside"
        else:
            return f"📈 {title} - Latest Tech Insights"
    
    def generate_international_description(self, title: str, platform: str) -> str:
        """生成适合国际平台的描述"""
        base_descriptions = {
            'youtube': "🚀 Discover the latest in AI and technology!\n\n" +
                      "In this video, we explore cutting-edge developments that are shaping the future.\n\n" +
                      "🔔 Subscribe for more tech insights!\n" +
                      "💬 Comment below with your thoughts!\n" +
                      "👍 Like if you found this helpful!\n\n" +
                      "#AI #Technology #Innovation #TechTrends",
            
            'tiktok': "⚡ Quick tech insight!\n" +
                     "Follow for more AI and programming tips!\n" +
                     "#AI #TechTok #Programming #LearnOnTikTok",
            
            'instagram': "🚀 Tech Deep Dive\n\n" +
                          "Exploring the latest in AI and technology.\n\n" +
                          "💡 Save this for later!\n" +
                          "🔄 Share with your tech friends!\n" +
                          "#AI #Technology #Programming #Innovation"
        }
        
        return base_descriptions.get(platform, "Check out this amazing tech content!")
    
    async def execute_publish_command(self, cmd: List[str], platform: str) -> bool:
        """执行发布命令"""
        try:
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd='/Users/ax/wechat-publisher/social-auto-upload'
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"发布命令执行成功: {platform}")
                return True
            else:
                logger.error(f"发布命令执行失败: {platform}")
                logger.error(f"stdout: {stdout.decode()}")
                logger.error(f"stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"执行发布命令失败: {e}")
            return False
    
    async def process_single_article(self, article_path: Path) -> bool:
        """处理单篇文章"""
        logger.info(f"开始处理文章: {article_path.name}")
        
        try:
            # 第一步：转换为视频
            video_path = await self.convert_article_to_video(article_path)
            
            if not video_path:
                logger.error(f"文章转换失败，跳过发布: {article_path.name}")
                self.mark_article_processed(article_path, "convert_failed")
                return False
            
            # 第二步：发布到国际平台
            publish_results = await self.publish_to_international_platforms(video_path, article_path)
            
            # 统计发布结果
            successful_platforms = [p for p, success in publish_results.items() if success]
            failed_platforms = [p for p, success in publish_results.items() if not success]
            
            if successful_platforms:
                logger.info(f"成功发布到: {', '.join(successful_platforms)}")
                self.mark_article_processed(article_path, f"published_to_{'_'.join(successful_platforms)}")
            
            if failed_platforms:
                logger.error(f"发布失败的平台: {', '.join(failed_platforms)}")
            
            return len(successful_platforms) > 0
            
        except Exception as e:
            logger.error(f"处理文章失败 {article_path}: {e}")
            self.mark_article_processed(article_path, "error")
            return False
    
    async def continuous_monitoring(self):
        """持续监控模式"""
        logger.info("开始国际平台文章自动监控...")
        logger.info(f"检查间隔: {self.check_interval}秒")
        logger.info(f"监控目录: {self.articles_dir}")
        
        retry_count = 0
        
        while True:
            try:
                # 获取新文章
                new_articles = self.get_new_articles()
                
                if new_articles:
                    logger.info(f"发现 {len(new_articles)} 篇新文章，开始处理...")
                    
                    # 处理每篇文章
                    for article_path in new_articles:
                        success = await self.process_single_article(article_path)
                        
                        # 文章间延迟
                        await asyncio.sleep(60)
                    
                    retry_count = 0  # 重置重试计数
                    
                else:
                    logger.info("没有新文章，等待下次检查...")
                
                # 等待下次检查
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("收到中断信号，停止监控...")
                break
                
            except Exception as e:
                logger.error(f"监控过程出错: {e}")
                retry_count += 1
                
                if retry_count >= self.max_retry_count:
                    logger.error("达到最大重试次数，停止监控")
                    break
                
                logger.info(f"{self.retry_delay}秒后重试...")
                await asyncio.sleep(self.retry_delay)
    
    def run_once(self):
        """单次运行模式"""
        logger.info("开始单次国际平台文章发布...")
        
        new_articles = self.get_new_articles()
        
        if not new_articles:
            logger.info("没有新文章需要处理")
            return
        
        logger.info(f"发现 {len(new_articles)} 篇新文章")
        
        # 使用事件循环运行异步函数
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            for article_path in new_articles:
                success = loop.run_until_complete(self.process_single_article(article_path))
                
                # 文章间延迟
                if article_path != new_articles[-1]:  # 不是最后一篇
                    time.sleep(60)
        
        finally:
            loop.close()
        
        logger.info("单次处理完成")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='国际平台文章自动发布系统')
    parser.add_argument('--mode', choices=['monitor', 'once'], default='once',
                       help='运行模式: monitor(持续监控) 或 once(单次运行)')
    parser.add_argument('--interval', type=int, default=300,
                       help='监控间隔时间(秒)，默认300秒')
    
    args = parser.parse_args()
    
    publisher = InternationalArticlePublisher()
    publisher.check_interval = args.interval
    
    if args.mode == 'monitor':
        # 持续监控模式
        asyncio.run(publisher.continuous_monitoring())
    else:
        # 单次运行模式
        publisher.run_once()

if __name__ == "__main__":
    main()