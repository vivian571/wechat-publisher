#!/usr/bin/env python3

import os
import re
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import tempfile
import sys
sys.path.append('/Users/ax/wechat-publisher')
from simple_video_creator import SimpleVideoCreator

class ArticleToVideoConverter:
    """将文章转换为视频的转换器"""
    
    def __init__(self, output_dir: str = "/Users/ax/wechat-publisher/social-auto-upload/videoFile"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 临时文件目录
        self.temp_dir = Path(tempfile.gettempdir()) / "article_to_video"
        self.temp_dir.mkdir(exist_ok=True)
        
    def parse_article(self, article_path: Path) -> Dict:
        """解析文章文件"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title_match = re.search(r'^#\s+\[([^\]]+)\]', content)
            title = title_match.group(1) if title_match else article_path.stem
            
            # 提取图片URL
            image_matches = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
            main_image = image_matches[0] if image_matches else None
            
            # 提取正文内容（移除标题和图片）
            body_content = re.sub(r'^#\s+\[.*?\]\s*\n', '', content)
            body_content = re.sub(r'!\[.*?\]\([^)]+\)\s*\n?', '', body_content)
            body_content = re.sub(r'---.*?---\s*\n?', '', body_content, flags=re.DOTALL)
            
            # 提取发布日期
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', article_path.name)
            publish_date = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
            
            return {
                'title': title.strip(),
                'main_image': main_image,
                'content': body_content.strip(),
                'publish_date': publish_date,
                'source_file': str(article_path),
                'filename': article_path.name
            }
            
        except Exception as e:
            print(f"解析文章失败 {article_path}: {e}")
            return None
    
    def extract_key_points(self, content: str) -> List[str]:
        """提取文章的关键点"""
        key_points = []
        
        # 提取小标题
        headers = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
        key_points.extend(headers)
        
        # 提取列表项
        list_items = re.findall(r'^\s*[-*+]\s+(.+)$', content, re.MULTILINE)
        key_points.extend(list_items[:5])  # 限制数量
        
        # 提取重要段落的第一句
        paragraphs = re.split(r'\n\s*\n', content)
        for para in paragraphs[:3]:
            para = para.strip()
            if para and not para.startswith('#') and len(para) > 50:
                first_sentence = re.split(r'[.!?]', para)[0]
                if len(first_sentence) > 20:
                    key_points.append(first_sentence)
        
        return key_points[:8]  # 最多8个关键点
    
    def generate_video_script(self, article_data: Dict) -> str:
        """生成视频脚本"""
        title = article_data['title']
        content = article_data['content']
        key_points = self.extract_key_points(content)
        
        script_parts = [
            f"大家好，今天我们来聊聊：{title}",
            "",
            "这个话题非常有趣，让我们一起来看看主要内容：",
            ""
        ]
        
        # 添加关键点
        for i, point in enumerate(key_points, 1):
            script_parts.append(f"第{i}点：{point}")
            script_parts.append("")
        
        script_parts.extend([
            "总结一下，",
            "这个话题确实值得我们深入思考。",
            "希望这个视频对你有帮助，记得点赞关注哦！"
        ])
        
        return '\n'.join(script_parts)
    
    async def download_image(self, url: str, output_path: Path) -> bool:
        """下载图片"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        with open(output_path, 'wb') as f:
                            f.write(await response.read())
                        return True
        except Exception as e:
            print(f"下载图片失败 {url}: {e}")
        return False
    
    def create_text_video(self, article_data: Dict, script: str, add_audio: bool = True) -> Optional[Path]:
        """创建文字视频（使用简单的视频创建器）"""
        try:
            # 使用新的视频创建器
            video_creator = SimpleVideoCreator(str(self.output_dir))
            
            # 生成输出文件名
            safe_title = re.sub(r'[^\w\-_.]', '_', article_data['title'])[:50]
            
            # 创建视频
            video_path = video_creator.create_simple_video(
                article_data['title'],
                script,
                safe_title,
                add_audio  # 传递音频选项
            )
            
            return video_path
            
        except Exception as e:
            print(f"创建视频失败: {e}")
            return None
    
    async def convert_article_to_video(self, article_path: Path) -> Optional[Path]:
        """将文章转换为视频的主函数"""
        print(f"正在处理文章: {article_path.name}")
        
        # 解析文章
        article_data = self.parse_article(article_path)
        if not article_data:
            return None
        
        print(f"文章标题: {article_data['title']}")
        
        # 生成视频脚本
        script = self.generate_video_script(article_data)
        print("已生成视频脚本")
        
        # 创建视频
        video_path = self.create_text_video(article_data, script)
        
        if video_path:
            print(f"文章转视频完成: {video_path}")
            return video_path
        
        return None
    
    async def convert_all_articles(self, articles_dir: Path) -> List[Path]:
        """转换目录中的所有文章"""
        converted_videos = []
        
        # 查找所有带日期的文章文件
        article_files = list(articles_dir.glob("2026-*.md"))
        
        if not article_files:
            print("未找到带日期的文章文件")
            return converted_videos
        
        print(f"找到 {len(article_files)} 篇文章")
        
        for article_file in article_files:
            try:
                video_path = await self.convert_article_to_video(article_file)
                if video_path:
                    converted_videos.append(video_path)
            except Exception as e:
                print(f"处理文章失败 {article_file}: {e}")
                continue
        
        return converted_videos

class ArticlePublisher:
    """文章自动发布器"""
    
    def __init__(self):
        self.articles_dir = Path("/Users/ax/wechat-publisher/OmniPublish/articles")
        self.video_converter = ArticleToVideoConverter()
        self.published_log = Path("/Users/ax/wechat-publisher/published_articles.log")
        
    def is_article_published(self, article_path: Path) -> bool:
        """检查文章是否已经发布过"""
        if not self.published_log.exists():
            return False
        
        try:
            with open(self.published_log, 'r', encoding='utf-8') as f:
                published_articles = f.read().splitlines()
            return str(article_path) in published_articles
        except Exception:
            return False
    
    def mark_article_published(self, article_path: Path):
        """标记文章为已发布"""
        try:
            with open(self.published_log, 'a', encoding='utf-8') as f:
                f.write(f"{article_path}\n")
        except Exception as e:
            print(f"记录发布状态失败: {e}")
    
    async def publish_articles(self):
        """发布所有未发布的文章"""
        print("开始文章自动发布流程...")
        
        # 获取所有带日期的文章
        article_files = list(self.articles_dir.glob("2026-*.md"))
        
        if not article_files:
            print("未找到待发布的文章")
            return
        
        new_articles = [f for f in article_files if not self.is_article_published(f)]
        
        if not new_articles:
            print("没有新的文章需要发布")
            return
        
        print(f"发现 {len(new_articles)} 篇新文章")
        
        # 转换文章为视频
        converted_videos = []
        
        for article_file in new_articles:
            try:
                print(f"\n处理文章: {article_file.name}")
                
                # 转换为视频
                video_path = await self.video_converter.convert_article_to_video(article_file)
                
                if video_path:
                    converted_videos.append(video_path)
                    self.mark_article_published(article_file)
                    print(f"✅ 文章转换成功: {article_file.name} -> {video_path.name}")
                else:
                    print(f"❌ 文章转换失败: {article_file.name}")
                    
            except Exception as e:
                print(f"处理文章失败 {article_file.name}: {e}")
                continue
        
        print(f"\n文章转换完成，共生成 {len(converted_videos)} 个视频")
        
        if converted_videos:
            print("视频文件已保存到:", "/Users/ax/wechat-publisher/social-auto-upload/videoFile")
            for video in converted_videos:
                print(f"  - {video.name}")
        
        return converted_videos

async def main():
    """主函数"""
    publisher = ArticlePublisher()
    
    try:
        # 发布文章
        videos = await publisher.publish_articles()
        
        if videos:
            print(f"\n🎉 成功生成 {len(videos)} 个视频！")
            print("您可以使用以下命令发布这些视频:")
            print("  cd /Users/ax/wechat-publisher")
            print("  ./video_manager.sh publish")
        else:
            print("\n没有新的文章需要处理")
            
    except Exception as e:
        print(f"文章发布过程出错: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    # 运行异步主函数
    result = asyncio.run(main())
    exit(result)