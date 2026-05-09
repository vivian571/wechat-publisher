import os
import time
import json
import requests
from typing import Dict, Optional, List, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .base import BasePublisher

class JuejinPublisher(BasePublisher):
    platform_name = 'juejin'
    """掘金平台发布器"""
    
    BASE_URL = "https://api.juejin.cn"
    LOGIN_URL = "https://juejin.cn/passport/web/user/login"
    
    def __init__(self, account_name: str, platform_config: dict, common_config: 'Config'):
        super().__init__(account_name, platform_config, common_config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://juejin.cn/',
            'Origin': 'https://juejin.cn',
        })
        self.token = None
        self.user_id = None
        self._login()
    
    def _login(self) -> bool:
        """登录掘金账号"""
        username = self.platform_config.get('username')
        password = self.platform_config.get('password')
        
        if not username or not password:
            self.log_error("缺少掘金账号或密码配置")
            return False
            
        try:
            # 获取登录页面，获取必要的cookies
            self.log_info("正在获取登录页面...")
            response = self.session.get('https://juejin.cn/', timeout=10)
            if response.status_code != 200:
                self.log_error(f"获取登录页面失败: HTTP {response.status_code}")
                return False
            
            self.log_info("正在发送登录请求...")
            # 发送登录请求
            login_data = {
                'account': username,
                'password': password,
                'captcha': '',
                'remember': 'true',
                'token': '',
                'source': 'web',
                'provider': 'password',
                'type': 'login',
            }
            
            response = self.session.post(
                self.LOGIN_URL,
                json=login_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-Agent': 'Juejin/Web',
                    'Referer': 'https://juejin.cn/',
                    'Origin': 'https://juejin.cn'
                },
                timeout=15
            )
            
            self.log_info(f"登录响应状态码: {response.status_code}")
            
            # 检查响应内容
            if not response.text.strip():
                self.log_error("登录失败: 服务器返回空响应")
                return False
                
            try:
                data = response.json()
            except ValueError as e:
                self.log_error(f"解析登录响应失败: {e}, 响应内容: {response.text[:200]}...")
                return False
            
            self.log_info(f"登录响应数据: {data}")
            
            if not isinstance(data, dict):
                self.log_error(f"登录失败: 无效的响应格式: {data}")
                return False
                
            if data.get('err_no') != 0:
                self.log_error(f"登录失败: {data.get('err_msg') or '未知错误'}")
                return False
                
            if not data.get('data') or 'token' not in data['data'] or 'user_id' not in data['data']:
                self.log_error(f"登录失败: 响应数据不完整: {data}")
                return False
                
            self.token = data['data']['token']
            self.user_id = data['data']['user_id']
            
            # 更新session的headers
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'X-Agent': 'Juejin/Web',
            })
            
            self.log_success(f"登录成功，用户ID: {self.user_id}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.log_error(f"网络请求失败: {str(e)}")
            return False
        except Exception as e:
            self.log_error(f"登录过程中发生错误: {str(e)}", exc_info=True)
            return False
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """上传图片到掘金"""
        if not self.token:
            self.log_error("未登录，无法上传图片")
            return None
            
        upload_url = f"{self.BASE_URL}/article_api/v1/upload_image"
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                response = self.session.post(upload_url, files=files)
                
            if response.status_code != 200:
                self.log_error(f"上传图片失败: HTTP {response.status_code}")
                return None
                
            data = response.json()
            if data.get('err_no') != 0:
                self.log_error(f"上传图片失败: {data.get('err_msg')}")
                return None
                
            image_url = data['data']['url']
            self.log_success(f"图片上传成功: {os.path.basename(image_path)}")
            return image_url
            
        except Exception as e:
            self.log_error(f"上传图片过程中发生错误: {e}", exc_info=True)
            return None
    
    def _process_content(self, content: str, image_dir: str) -> str:
        """处理内容中的图片"""
        soup = BeautifulSoup(content, 'html.parser')
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if not src.startswith(('http://', 'https://')):
                # 处理相对路径
                image_path = os.path.join(image_dir, src)
                if os.path.exists(image_path):
                    remote_url = self.upload_image(image_path)
                    if remote_url:
                        img['src'] = remote_url
        
        return str(soup)
    
    def publish(self, content_path: str, **kwargs) -> bool:
        """发布内容到掘金"""
        if not self.token:
            self.log_error("未登录，无法发布内容")
            return False
            
        try:
            # 读取Markdown内容
            with open(content_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取元数据
            metadata = {}
            if content.startswith('---'):
                _, frontmatter, content = content.split('---', 2)
                for line in frontmatter.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
            
            title = metadata.get('title', os.path.splitext(os.path.basename(content_path))[0])
            
            # 处理内容中的图片
            content_dir = os.path.dirname(content_path)
            processed_content = self._process_content(content, content_dir)
            
            # 准备发布数据
            article_data = {
                'title': title,
                'mark_content': processed_content,
                'brief_content': metadata.get('description', '')[:200],
                'cover_image': metadata.get('cover', ''),
                'category_id': self.config.get('category_id', '6809637767543259144'),  # 默认分类：后端
                'tag_ids': self.config.get('tag_ids', ['6809640407484334093']),    # 默认标签：后端
                'edit_type': 10,  # 10:markdown, 20:富文本
                'html_content': '',
                'link_url': '',
                'is_english': False,
                'is_original': True,
                'original_author': '',
                'original_url': '',
            }
            
            # 创建草稿
            draft_url = f"{self.BASE_URL}/content_api/v1/article/create"
            response = self.session.post(draft_url, json=article_data)
            
            if response.status_code != 200:
                self.log_error(f"创建草稿失败: HTTP {response.status_code}")
                return False
                
            data = response.json()
            if data.get('err_no') != 0:
                self.log_error(f"创建草稿失败: {data.get('err_msg')}")
                return False
                
            article_id = data['data']['id']
            article_url = f"https://juejin.cn/editor/drafts/{article_id}"
            
            self.log_success(f"文章草稿创建成功: {article_url}")
            return True
            
        except Exception as e:
            self.log_error(f"发布过程中发生错误: {e}", exc_info=True)
            return False
