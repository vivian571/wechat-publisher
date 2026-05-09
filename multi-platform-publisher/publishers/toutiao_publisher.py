import os
import sys
import re
import json
import time
import random
import requests
import base64
from urllib.parse import urljoin, quote
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup
from .base import BasePublisher

# 设置控制台输出编码
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class Article:
    """文章数据类"""
    def __init__(self, title: str, content: str, **kwargs):
        self.title = title
        self.content = content
        self.summary = kwargs.get('summary', '')
        self.tags = kwargs.get('tags', [])
        self.cover_image = kwargs.get('cover_image', '')
        self.original = kwargs.get('original', True)  # 是否原创
        self.article_type = kwargs.get('article_type', 'normal')  # normal(普通), gallery(图集)
        self.category = kwargs.get('category', '')  # 文章分类
        self.original_url = kwargs.get('original_url', '')  # 原文链接
        self.rich_content = kwargs.get('rich_content', '')  # 富文本内容
        self.images = kwargs.get('images', [])  # 图片列表
        self.publish_time = kwargs.get('publish_time', int(time.time()))  # 发布时间戳

class ToutiaoPublisher(BasePublisher):
    """今日头条发布器"""
    platform_name = 'toutiao'
    BASE_URL = 'https://mp.toutiao.com'
    
    def __init__(self, account_name: str, platform_config: dict, common_config: 'Config'):
        super().__init__(account_name, platform_config, common_config)
        self.session = requests.Session()
        self.csrf_token = ''
        self.cookies = {}
        
        # 配置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Origin': self.BASE_URL,
            'Referer': f'{self.BASE_URL}/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
        # 从配置中获取账号信息
        self.username = self.platform_config.get('username')
        self.password = self.platform_config.get('password')
        self.cookie_str = self.platform_config.get('cookies', '')
        
        # 初始化会话
        self._init_session()
    
    def _init_session(self):
        """初始化会话，设置cookies"""
        if self.cookie_str:
            try:
                # 解析cookies字符串
                cookies = {}
                for item in self.cookie_str.split(';'):
                    item = item.strip()
                    if '=' in item:
                        k, v = item.split('=', 1)
                        cookies[k] = v
                self.session.cookies.update(cookies)
                self.cookies = cookies
                self.log_info("已从配置加载cookies")
            except Exception as e:
                self.log_error(f"解析cookies失败: {e}")
    
    def _get_csrf_token(self) -> str:
        """获取CSRF Token"""
        if self.csrf_token:
            return self.csrf_token
            
        try:
            # 访问首页获取CSRF Token
            response = self.session.get(f'{self.BASE_URL}/', timeout=10)
            response.raise_for_status()
            
            # 从HTML中提取CSRF Token
            match = re.search(r'"_csrf":"([^"]+)"', response.text)
            if match:
                self.csrf_token = match.group(1)
                self.log_info(f"获取到CSRF Token: {self.csrf_token}")
                return self.csrf_token
            else:
                self.log_error("未找到CSRF Token")
                return ''
        except Exception as e:
            self.log_error(f"获取CSRF Token失败: {e}")
            return ''
    
    def _login(self) -> bool:
        """登录今日头条"""
        if not self.username or not self.password:
            self.log_error("未配置用户名或密码")
            return False
            
        try:
            # 获取登录页面
            login_url = f'{self.BASE_URL}/login/'
            response = self.session.get(login_url, timeout=10)
            response.raise_for_status()
            
            # 获取验证码参数
            captcha_url = f'{self.BASE_URL}/api/v1/captcha/get/'
            params = {
                't': int(time.time() * 1000),
                'type': 'login',
                'account': self.username,
            }
            response = self.session.get(captcha_url, params=params)
            captcha_data = response.json()
            
            if captcha_data.get('code') != 0:
                self.log_error(f"获取验证码失败: {captcha_data.get('message')}")
                return False
                
            captcha_id = captcha_data['data']['id']
            captcha_url = captcha_data['data']['url']
            
            # 这里需要人工输入验证码，或者集成验证码识别服务
            self.log_info(f"请访问以下链接完成验证码识别: {captcha_url}")
            verify_code = input("请输入验证码: ")
            
            # 提交登录请求
            login_api = f'{self.BASE_URL}/api/v1/login/'
            data = {
                'account': self.username,
                'password': self.password,
                'captcha_code': verify_code,
                'captcha_id': captcha_id,
                'is_remember': 'true',
                'login_type': 'account',
                'mix_mode': '1',
                'source': 'mp',
                'token': self._get_csrf_token(),
            }
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-CSRFToken': self._get_csrf_token(),
            }
            
            response = self.session.post(login_api, json=data, headers=headers)
            result = response.json()
            
            if result.get('code') == 0:
                self.log_success("登录成功")
                # 更新cookies
                self.cookies = dict(self.session.cookies.items())
                return True
            else:
                self.log_error(f"登录失败: {result.get('message')}")
                return False
                
        except Exception as e:
            self.log_error(f"登录过程中发生错误: {e}", exc_info=True)
            return False

    def process_document(self, file_path: str) -> bool:
        """
        处理Markdown文档并发布到今日头条
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            bool: 发布是否成功
        """
        try:
            # 读取Markdown内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取元数据
            metadata = {}
            if content.startswith('---'):
                _, frontmatter, content = content.split('---', 2)
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
            
            # 创建文章对象
            title = metadata.get('title', os.path.basename(file_path).rsplit('.', 1)[0])
            tags = [t.strip() for t in metadata.get('tags', '').split(',') if t.strip()]
            
            article = Article(
                title=title,
                content=content,
                summary=metadata.get('summary', ''),
                tags=tags,
                cover_image=metadata.get('cover', ''),
                original=metadata.get('original', 'true').lower() == 'true',
                category=metadata.get('category', ''),
                original_url=metadata.get('original_url', '')
            )
            
            # 调用publish方法发布文章
            return self.publish(article)
            
        except Exception as e:
            self.log_error(f"处理文档时出错: {e}", exc_info=True)
            return False
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到今日头条图床
        
        Args:
            image_path: 图片本地路径
            
        Returns:
            str: 图片URL，上传失败返回None
        """
        try:
            if not os.path.exists(image_path):
                self.log_error(f"图片文件不存在: {image_path}")
                return None
                
            # 确保已登录
            if not self._get_csrf_token():
                self.log_error("未获取到CSRF Token，无法上传图片")
                return None
            
            # 上传图片
            upload_url = f'{self.BASE_URL}/api/v1/image/upload/'
            files = {
                'file': (os.path.basename(image_path), open(image_path, 'rb'), 'image/jpeg')
            }
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': self._get_csrf_token(),
            }
            
            response = self.session.post(upload_url, files=files, headers=headers)
            result = response.json()
            
            if result.get('code') == 0 and 'data' in result and 'url' in result['data']:
                image_url = result['data']['url']
                self.log_info(f"图片上传成功: {image_url}")
                return image_url
            else:
                self.log_error(f"图片上传失败: {result.get('message')}")
                return None
                
        except Exception as e:
            self.log_error(f"上传图片时出错: {e}", exc_info=True)
            return None
    
    def publish(self, article) -> bool:
        """
        发布文章到今日头条
        
        Args:
            article: Article对象，包含文章内容
            
        Returns:
            bool: 发布是否成功
        """
        self.log_info(f"开始发布到今日头条: {article.title}")
        
        try:
            # 1. 确保已登录
            if not self._get_csrf_token():
                self.log_error("未获取到CSRF Token，请先登录")
                return False
            
            # 2. 处理封面图
            cover_image_url = ''
            if article.cover_image and os.path.exists(article.cover_image):
                cover_image_url = self.upload_image(article.cover_image)
            
            # 3. 处理内容中的图片
            # 这里简化处理，实际应该解析Markdown中的图片并上传
            
            # 4. 准备发布数据
            publish_data = {
                'title': article.title,
                'content': article.content,
                'summary': article.summary or article.content[:100],
                'cover_image': cover_image_url,
                'is_original': article.original,
                'tag': ','.join(article.tags) if article.tags else '',
                'article_type': article.article_type,
                'source': 'mp',
                'token': self._get_csrf_token(),
            }
            
            # 5. 发布文章
            publish_url = f'{self.BASE_URL}/api/v1/article/publish/'
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-CSRFToken': self._get_csrf_token(),
            }
            
            response = self.session.post(
                publish_url,
                json=publish_data,
                headers=headers
            )
            
            result = response.json()
            
            if result.get('code') == 0 and 'data' in result and 'article_id' in result['data']:
                article_id = result['data']['article_id']
                article_url = f'https://www.toutiao.com/article/{article_id}/'
                self.log_success(f"文章发布成功! 文章ID: {article_id}")
                self.log_info(f"文章链接: {article_url}")
                return True
            else:
                error_msg = result.get('message', '未知错误')
                self.log_error(f"文章发布失败: {error_msg}")
                return False
                
        except Exception as e:
            self.log_error(f"发布文章时发生错误: {e}", exc_info=True)
            return False
