#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信公众号草稿箱自动发布工具

自动检测指定目录中的文章，将图片上传为永久素材，
然后将文章内容发布到微信公众号草稿箱。

使用方法：
    python wechat_draft_publisher.py --dir "文章目录" --config "配置文件路径"
"""

import os
import re
import json
import time
import logging
import argparse
import requests
import markdown
from datetime import datetime
from bs4 import BeautifulSoup

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wechat_publisher.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("WeChatPublisher")


class WeChatDraftPublisher:
    """微信公众号草稿箱发布工具"""

    def __init__(self, config_path="config.json"):
        """初始化微信公众号发布工具

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.access_token = None
        self.token_expires = 0
        self.media_cache = {}  # 缓存已上传的媒体文件，避免重复上传

    def load_config(self):
        """加载配置文件

        Returns:
            包含微信公众号配置的字典
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 创建默认配置
                default_config = {
                    "app_id": "",
                    "app_secret": "",
                    "api_base_url": "https://api.weixin.qq.com",
                    "processed_mark": ".published",
                    "image_extensions": [".jpg", ".jpeg", ".png", ".gif"],
                    "max_title_length": 64,
                    "max_retry": 3,
                    "retry_interval": 5
                }
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                logger.warning(f"配置文件不存在，已创建默认配置: {self.config_path}")
                logger.warning(f"请编辑配置文件，填入您的app_id和app_secret")
                return default_config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise

    def get_access_token(self, force_refresh=False):
        """获取微信公众号访问令牌

        Args:
            force_refresh: 是否强制刷新token

        Returns:
            access_token: 访问令牌
        """
        # 检查是否需要刷新token
        current_time = time.time()
        if not force_refresh and self.access_token and current_time < self.token_expires - 300:
            return self.access_token

        # 获取新token
        app_id = self.config.get("app_id")
        app_secret = self.config.get("app_secret")
        if not app_id or not app_secret:
            raise ValueError("请在配置文件中设置app_id和app_secret")

        api_url = f"{self.config['api_base_url']}/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": app_id,
            "secret": app_secret
        }

        try:
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            result = response.json()

            if "access_token" in result:
                self.access_token = result["access_token"]
                self.token_expires = current_time + result["expires_in"]
                logger.info(f"成功获取access_token，有效期至: {datetime.fromtimestamp(self.token_expires)}")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {result}")
                raise Exception(f"获取access_token失败: {result.get('errmsg', '未知错误')}")
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            raise

    def upload_image(self, image_path):
        """上传图片素材到微信公众号

        Args:
            image_path: 图片路径

        Returns:
            media_id: 媒体文件ID
        """
        # 检查缓存，避免重复上传
        if image_path in self.media_cache:
            logger.info(f"使用缓存的media_id: {self.media_cache[image_path]}")
            return self.media_cache[image_path]

        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error(f"图片文件不存在: {image_path}")
            return None

        # 检查文件扩展名
        _, ext = os.path.splitext(image_path)
        if ext.lower() not in self.config.get("image_extensions", [".jpg", ".jpeg", ".png", ".gif"]):
            logger.warning(f"不支持的图片格式: {ext}")
            return None

        # 获取access_token
        access_token = self.get_access_token()

        # 上传图片
        api_url = f"{self.config['api_base_url']}/cgi-bin/material/add_material"
        params = {"access_token": access_token, "type": "image"}

        try:
            with open(image_path, 'rb') as f:
                files = {'media': (os.path.basename(image_path), f, f"image/{ext.lstrip('.')}")}
                response = requests.post(api_url, params=params, files=files)
                response.raise_for_status()
                result = response.json()

                if "media_id" in result:
                    media_id = result["media_id"]
                    # 缓存media_id
                    self.media_cache[image_path] = media_id
                    logger.info(f"成功上传图片: {image_path}, media_id: {media_id}")
                    return media_id
                else:
                    logger.error(f"上传图片失败: {result}")
                    return None
        except Exception as e:
            logger.error(f"上传图片异常: {e}")
            return None

    def extract_images_from_markdown(self, md_content, base_dir):
        """从Markdown内容中提取图片，并上传到微信公众号

        Args:
            md_content: Markdown内容
            base_dir: 基础目录，用于解析相对路径

        Returns:
            处理后的HTML内容，图片已替换为微信素材URL
        """
        # 将Markdown转换为HTML
        html_content = markdown.markdown(md_content, extensions=['extra'])
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有图片标签
        img_tags = soup.find_all('img')
        for img in img_tags:
            src = img.get('src', '')
            if not src:
                continue
                
            # 处理相对路径
            if not src.startswith(('http://', 'https://', 'data:')):
                # 解析相对路径
                if os.path.isabs(src):
                    img_path = src
                else:
                    img_path = os.path.join(base_dir, src)
                    img_path = os.path.normpath(img_path)
                
                # 上传图片到微信
                media_id = self.upload_image(img_path)
                if media_id:
                    # 替换图片链接为微信素材URL
                    img['src'] = f"https://mmbiz.qpic.cn/mmbiz_jpg/{media_id}/0?wx_fmt=jpeg"
                    logger.info(f"已替换图片: {src} -> {img['src']}")
        
        return str(soup)

    def add_draft(self, title, content, thumb_media_id=None, author="", digest=""):
        """添加草稿

        Args:
            title: 文章标题
            content: 文章内容（HTML格式）
            thumb_media_id: 封面图片media_id
            author: 作者
            digest: 摘要

        Returns:
            是否成功
        """
        # 获取access_token
        access_token = self.get_access_token()
        
        # 检查标题长度
        if len(title.encode('utf-8')) > self.config.get("max_title_length", 64):
            logger.warning(f"标题长度超出限制: {len(title.encode('utf-8'))} 字节")
            title = self._truncate_title(title)
            
        # 准备请求数据
        api_url = f"{self.config['api_base_url']}/cgi-bin/draft/add"
        params = {"access_token": access_token}
        
        # 构建文章数据
        article = {
            "title": title,
            "content": content,
            "author": author,
            "digest": digest,
            "content_source_url": "",
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }
        
        # 如果有封面图片，添加到文章数据
        if thumb_media_id:
            article["thumb_media_id"] = thumb_media_id
        
        # 构建请求数据
        data = {"articles": [article]}
        
        # 发送请求
        try:
            response = requests.post(api_url, params=params, json=data)
            response.raise_for_status()
            result = response.json()
            
            if result.get("errcode") == 0:
                media_id = result.get("media_id")
                logger.info(f"成功添加草稿: {title}, media_id: {media_id}")
                return True, media_id
            else:
                logger.error(f"添加草稿失败: {result}")
                return False, None
        except Exception as e:
            logger.error(f"添加草稿异常: {e}")
            return False, None

    def _truncate_title(self, title):
        """截断标题，确保不超过字节限制
        
        Args:
            title: 原始标题
            
        Returns:
            截断后的标题
        """
        max_bytes = self.config.get("max_title_length", 64)
        encoded = title.encode('utf-8')
        if len(encoded) <= max_bytes:
            return title
            
        # 二分查找合适的截断位置
        left, right = 0, len(title)
        while left < right:
            mid = (left + right + 1) // 2
            if len(title[:mid].encode('utf-8')) <= max_bytes:
                left = mid
            else:
                right = mid - 1
                
        truncated = title[:left]
        if truncated != title:
            truncated += "..."
            # 确保添加省略号后仍不超过字节限制
            while len(truncated.encode('utf-8')) > max_bytes:
                truncated = truncated[:-4] + "..."
                
        logger.info(f"标题已截断: {title} -> {truncated}")
        return truncated

    def process_article(self, md_file_path):
        """处理单篇文章，上传图片并发布到草稿箱

        Args:
            md_file_path: Markdown文件路径

        Returns:
            是否成功处理
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(md_file_path):
                logger.error(f"文件不存在: {md_file_path}")
                return False

            # 检查是否已处理
            mark_file = md_file_path + self.config.get("processed_mark", ".published")
            if os.path.exists(mark_file):
                logger.info(f"文件已处理，跳过: {md_file_path}")
                return True

            # 读取文件内容
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # 提取标题
            title = self._extract_title(md_content) or os.path.basename(md_file_path)
            
            # 提取作者和摘要
            author = self._extract_author(md_content) or ""
            digest = self._extract_digest(md_content) or ""

            # 处理文章中的图片
            base_dir = os.path.dirname(md_file_path)
            html_content = self.extract_images_from_markdown(md_content, base_dir)

            # 查找封面图片
            thumb_media_id = self._find_cover_image(md_content, base_dir)

            # 添加到草稿箱
            success, media_id = self.add_draft(title, html_content, thumb_media_id, author, digest)
            if success:
                # 标记为已处理
                with open(mark_file, 'w', encoding='utf-8') as f:
                    f.write(f"发布时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"草稿media_id: {media_id}\n")
                logger.info(f"文章已成功发布到草稿箱: {md_file_path}")
                return True
            else:
                logger.error(f"发布文章到草稿箱失败: {md_file_path}")
                return False
        except Exception as e:
            logger.error(f"处理文章异常: {md_file_path}, {e}")
            return False

    def _extract_title(self, md_content):
        """从Markdown内容中提取标题

        Args:
            md_content: Markdown内容

        Returns:
            标题字符串
        """
        # 尝试从一级标题提取
        h1_match = re.search(r'^\s*#\s+(.+?)\s*$', md_content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1)

        # 尝试从文件开头提取（假设第一行是标题）
        lines = md_content.strip().split('\n')
        if lines:
            return lines[0].strip('#').strip()

        return None

    def _extract_author(self, md_content):
        """从Markdown内容中提取作者信息

        Args:
            md_content: Markdown内容

        Returns:
            作者字符串
        """
        # 尝试从元数据或特定格式中提取作者信息
        author_match = re.search(r'作者[：:](\s*)([^\n]+)', md_content)
        if author_match:
            return author_match.group(2).strip()
            
        # 尝试从YAML前置元数据中提取
        yaml_match = re.search(r'^---\s*\n(.+?)\n---', md_content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            author_yaml = re.search(r'author\s*:\s*([^\n]+)', yaml_content)
            if author_yaml:
                return author_yaml.group(1).strip()
                
        return None

    def _extract_digest(self, md_content):
        """从Markdown内容中提取摘要

        Args:
            md_content: Markdown内容

        Returns:
            摘要字符串
        """
        # 尝试从元数据或特定格式中提取摘要
        digest_match = re.search(r'摘要[：:](\s*)([^\n]+)', md_content)
        if digest_match:
            return digest_match.group(2).strip()
            
        # 尝试从YAML前置元数据中提取
        yaml_match = re.search(r'^---\s*\n(.+?)\n---', md_content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            digest_yaml = re.search(r'(summary|digest|description)\s*:\s*([^\n]+)', yaml_content)
            if digest_yaml:
                return digest_yaml.group(2).strip()
                
        # 如果没有明确的摘要，提取文章前100个字符作为摘要
        # 先去除YAML前置元数据和标题
        content = re.sub(r'^---\s*\n.+?\n---', '', md_content, flags=re.DOTALL)
        content = re.sub(r'^\s*#\s+.+?\n', '', content)
        
        # 提取纯文本
        text = re.sub(r'\!?\[.*?\]\(.*?\)', '', content)  # 移除链接和图片
        text = re.sub(r'[\*_`#>]+', '', text)  # 移除Markdown标记
        text = re.sub(r'\s+', ' ', text).strip()  # 规范化空白
        
        if text:
            # 截取前100个字符
            digest = text[:100].strip()
            if len(text) > 100:
                digest += "..."
            return digest
                
        return None

    def _find_cover_image(self, md_content, base_dir):
        """从Markdown内容中查找封面图片

        Args:
            md_content: Markdown内容
            base_dir: 基础目录，用于解析相对路径

        Returns:
            封面图片的media_id
        """
        # 尝试从元数据中查找封面图片
        cover_match = re.search(r'封面[：:](\s*)([^\n]+)', md_content)
        if cover_match:
            cover_path = cover_match.group(2).strip()
            if not os.path.isabs(cover_path):
                cover_path = os.path.join(base_dir, cover_path)
                cover_path = os.path.normpath(cover_path)
            return self.upload_image(cover_path)
            
        # 尝试从YAML前置元数据中提取
        yaml_match = re.search(r'^---\s*\n(.+?)\n---', md_content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            cover_yaml = re.search(r'(cover|thumbnail|featured_image)\s*:\s*([^\n]+)', yaml_content)
            if cover_yaml:
                cover_path = cover_yaml.group(2).strip()
                if not os.path.isabs(cover_path):
                    cover_path = os.path.join(base_dir, cover_path)
                    cover_path = os.path.normpath(cover_path)
                return self.upload_image(cover_path)
        
        # 尝试查找文章中的第一张图片作为封面
        img_match = re.search(r'!\[(.*?)\]\((.*?)\)', md_content)
        if img_match:
            img_path = img_match.group(2).strip()
            if not os.path.isabs(img_path) and not img_path.startswith(('http://', 'https://', 'data:')):
                img_path = os.path.join(base_dir, img_path)
                img_path = os.path.normpath(img_path)
            return self.upload_image(img_path)
            
        return None

    def scan_directory(self, directory):
        """扫描目录，处理所有Markdown文件

        Args:
            directory: 要扫描的目录路径

        Returns:
            处理的文件数量和成功数量
        """
        if not os.path.exists(directory) or not os.path.isdir(directory):
            logger.error(f"目录不存在: {directory}")
            return 0, 0

        total_count = 0
        success_count = 0

        # 遍历目录中的所有Markdown文件
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".md") and not file.endswith(self.config.get("processed_mark", ".published")):
                    md_file_path = os.path.join(root, file)
                    logger.info(f"处理文件: {md_file_path}")
                    
                    total_count += 1
                    if self.process_article(md_file_path):
                        success_count += 1

        return total_count, success_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="微信公众号草稿箱自动发布工具")
    parser.add_argument("--dir", "-d", required=True, help="要处理的文章目录")
    parser.add_argument("--config", "-c", default="config.json", help="配置文件路径")
    parser.add_argument("--file", "-f", help="处理单个文件")
    parser.add_argument("--force", action="store_true", help="强制处理已发布的文件")
    args = parser.parse_args()

    try:
        publisher = WeChatDraftPublisher(args.config)
        
        if args.force:
            # 移除已处理标记
            if args.file:
                mark_file = args.file + publisher.config.get("processed_mark", ".published")
                if os.path.exists(mark_file):
                    os.remove(mark_file)
                    logger.info(f"已移除处理标记: {mark_file}")
            elif args.dir:
                for root, _, files in os.walk(args.dir):
                    for file in files:
                        if file.endswith(publisher.config.get("processed_mark", ".published")):
                            mark_file = os.path.join(root, file)
                            os.remove(mark_file)
                            logger.info(f"已移除处理标记: {mark_file}")
        
        if args.file:
            # 处理单个文件
            if publisher.process_article(args.file):
                logger.info("文件处理成功")
            else:
                logger.error("文件处理失败")
        else:
            # 处理目录
            total, success = publisher.scan_directory(args.dir)
            logger.info(f"处理完成: 总共 {total} 个文件, 成功 {success} 个")
    except Exception as e:
        logger.error(f"程序执行异常: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())