import os
import sys
import re
import json
import time
import random
import requests
import base64
from urllib.parse import urljoin, quote, unquote
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
        self.topics = kwargs.get('topics', [])  # 话题
        self.column = kwargs.get('column', '')  # 专栏
        self.cover_image = kwargs.get('cover_image', '')  # 封面图
        self.original = kwargs.get('original', True)  # 是否原创
        self.original_url = kwargs.get('original_url', '')  # 原文链接
        self.commentable = kwargs.get('commentable', True)  # 是否允许评论
        self.publish_time = kwargs.get('publish_time', int(time.time()))  # 发布时间戳

class ZhihuPublisher(BasePublisher):
    """知乎发布器"""
    platform_name = 'zhihu'
    BASE_URL = 'https://www.zhihu.com'
    API_BASE_URL = 'https://api.zhihu.com'
    
    def __init__(self, account_name: str, platform_config: dict, common_config: 'Config'):
        super().__init__(account_name, platform_config, common_config)
        self.session = requests.Session()
        self.xsrf_token = ''
        self.cookies = {}
        
        # 配置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Host': 'www.zhihu.com',
            'Origin': self.BASE_URL,
            'Referer': f'{self.BASE_URL}/',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
        # 从配置中获取账号信息
        self.email = self.platform_config.get('email')
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
                
                # 从cookies中获取xsrf token
                self.xsrf_token = self.cookies.get('_xsrf', '')
                if self.xsrf_token:
                    self.xsrf_token = unquote(self.xsrf_token)
            except Exception as e:
                self.log_error(f"解析cookies失败: {e}")
    
    def _get_xsrf_token(self) -> str:
        """获取XSRF Token"""
        if self.xsrf_token:
            return self.xsrf_token
            
        try:
            # 访问首页获取XSRF Token
            response = self.session.get(f'{self.BASE_URL}/', timeout=10)
            response.raise_for_status()
            
            # 从cookies中获取XSRF Token
            if '_xsrf' in self.session.cookies:
                self.xsrf_token = unquote(self.session.cookies['_xsrf'])
                self.log_info(f"获取到XSRF Token: {self.xsrf_token}")
                return self.xsrf_token
            else:
                # 从HTML中提取XSRF Token
                match = re.search(r'name="_xsrf" value="([^"]+)"', response.text)
                if match:
                    self.xsrf_token = match.group(1)
                    self.log_info(f"从HTML中获取到XSRF Token: {self.xsrf_token}")
                    return self.xsrf_token
                else:
                    self.log_warning("未找到XSRF Token，可能需要登录")
                    return ''
        except Exception as e:
            self.log_error(f"获取XSRF Token失败: {e}")
            return ''
    
    def _login(self) -> bool:
        """登录知乎"""
        if not self.email or not self.password:
            self.log_error("未配置邮箱或密码")
            return False
            
        try:
            # 1. 获取登录页面
            login_url = f'{self.BASE_URL}/signin'
            response = self.session.get(login_url, timeout=10)
            response.raise_for_status()
            
            # 2. 获取验证码参数
            captcha_url = f'{self.BASE_URL}/api/v3/oauth/captcha?lang=en'
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-Xsrftoken': self._get_xsrf_token(),
            }
            response = self.session.get(captcha_url, headers=headers)
            captcha_data = response.json()
            
            captcha = ''
            if captcha_data.get('show_captcha', False):
                # 需要验证码
                captcha_url = f'{self.BASE_URL}/api/v3/oauth/captcha?lang=en'
                response = self.session.put(captcha_url, headers=headers)
                captcha_data = response.json()
                
                if 'img_base64' in captcha_data:
                    # 显示验证码图片并等待用户输入
                    img_data = captcha_data['img_base64']
                    self.log_info("需要输入验证码，请查看图片并输入验证码")
                    # 这里可以添加显示图片的代码，或者直接要求用户输入
                    captcha = input("请输入验证码: ")
            
            # 3. 提交登录请求
            login_api = f'{self.BASE_URL}/api/v3/oauth/sign_in'
            data = {
                'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',  # 固定值
                'grant_type': 'password',
                'source': 'com.zhihu.web',
                'username': self.email,
                'password': self.password,
                'lang': 'en',
                'ref_source': 'homepage',
                'utm_source': '',
                'signature': '',
                'captcha': captcha,
                'timestamp': int(time.time() * 1000),
            }
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-Xsrftoken': self._get_xsrf_token(),
                'Content-Type': 'application/json',
            }
            
            response = self.session.post(login_api, json=data, headers=headers)
            result = response.json()
            
            if 'error' in result:
                self.log_error(f"登录失败: {result.get('error', {}).get('message', '未知错误')}")
                return False
            else:
                self.log_success("登录成功")
                # 更新cookies和xsrf token
                self.cookies = dict(self.session.cookies.items())
                if '_xsrf' in self.cookies:
                    self.xsrf_token = unquote(self.cookies['_xsrf'])
                return True
                
        except Exception as e:
            self.log_error(f"登录过程中发生错误: {e}", exc_info=True)
            return False

    def process_document(self, file_path: str) -> bool:
        """
        处理Markdown文档并发布到知乎
        
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
                        metadata[key.strip()] = value.strip().strip('\"\'')
            
            # 创建文章对象
            title = metadata.get('title', os.path.basename(file_path).rsplit('.', 1)[0])
            topics = [t.strip() for t in metadata.get('topics', '').split(',') if t.strip()]
            
            article = Article(
                title=title,
                content=content,
                summary=metadata.get('summary', ''),
                topics=topics,
                column=metadata.get('column', ''),
                cover_image=metadata.get('cover', ''),
                original=metadata.get('original', 'true').lower() == 'true',
                original_url=metadata.get('original_url', ''),
                commentable=metadata.get('commentable', 'true').lower() == 'true'
            )
            
            # 调用publish方法发布文章
            return self.publish(article)
            
        except Exception as e:
            self.log_error(f"处理文档时出错: {e}", exc_info=True)
            return False
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        上传图片到知乎图床
        
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
            if not self._get_xsrf_token():
                self.log_error("未获取到XSRF Token，无法上传图片")
                return None
            
            # 上传图片
            upload_url = f'{self.BASE_URL}/api/v4/uploaded_images'
            
            with open(image_path, 'rb') as f:
                files = {
                    'image': (os.path.basename(image_path), f, 'image/jpeg')
                }
                
                headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-Xsrftoken': self._get_xsrf_token(),
                }
                
                response = self.session.post(upload_url, files=files, headers=headers)
                result = response.json()
                
                if 'url' in result:
                    image_url = result['url']
                    self.log_info(f"图片上传成功: {image_url}")
                    return image_url
                else:
                    self.log_error(f"图片上传失败: {result.get('error', {}).get('message', '未知错误')}")
                    return None
                    
        except Exception as e:
            self.log_error(f"上传图片时出错: {e}", exc_info=True)
            return None
    
    def publish(self, article) -> bool:
        """
        发布文章到知乎
        
        Args:
            article: Article对象，包含文章内容
            
        Returns:
            bool: 发布是否成功
        """
        self.log_info(f"开始发布到知乎: {article.title}")
        
        try:
            # 1. 确保已登录
            if not self._get_xsrf_token():
                if not self._login():
                    self.log_error("登录失败，无法发布文章")
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
                'excerpt': article.summary or article.content[:100],
                'image_url': cover_image_url,
                'is_original': article.original,
                'comment_permission': 'all' if article.commentable else 'no_comment',
                'can_comment': {
                    'status': article.commentable
                },
                'content_type': 'article',
                'source': 'desktop',
                'origin_url': article.original_url if article.original_url else '',
                'is_labeled': False,
                'include_header': False,
                'is_fold': False,
                'is_upload_rich_info': False,
                'is_new_pm_section': False,
                'type': 'article',
                'token': self._get_xsrf_token(),
            }
            
            # 5. 发布文章
            publish_url = f'{self.API_BASE_URL}/articles/drafts'
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'X-Xsrftoken': self._get_xsrf_token(),
            }
            
            response = self.session.post(
                publish_url,
                json=publish_data,
                headers=headers
            )
            
            result = response.json()
            
            if 'id' in result:
                article_id = result['id']
                article_url = f'https://zhuanlan.zhihu.com/p/{article_id}'
                self.log_success(f"文章发布成功! 文章ID: {article_id}")
                self.log_info(f"文章链接: {article_url}")
                
                # 6. 如果指定了专栏，添加到专栏
                if article.column:
                    self._add_to_column(article_id, article.column)
                
                # 7. 如果有关注话题，添加到话题
                if article.topics:
                    self._add_to_topics(article_id, article.topics)
                
                return True
            else:
                error_msg = result.get('error', {}).get('message', '未知错误')
                self.log_error(f"文章发布失败: {error_msg}")
                return False
                
        except Exception as e:
            self.log_error(f"发布文章时发生错误: {e}", exc_info=True)
            return False
    
    def _add_to_column(self, article_id: str, column_name: str) -> bool:
        """将文章添加到专栏"""
        try:
            # 1. 搜索专栏
            search_url = f'{self.API_BASE_URL}/search/columns'
            params = {
                'q': column_name,
                'limit': 1,
                'offset': 0,
            }
            
            headers = {
                'X-Requested-With': 'XMLHttpRequest',
                'X-Xsrftoken': self._get_xsrf_token(),
            }
            
            response = self.session.get(search_url, params=params, headers=headers)
            result = response.json()
            
            if 'data' in result and result['data']:
                column = result['data'][0]
                column_id = column['id']
                
                # 2. 添加到专栏
                add_url = f'{self.API_BASE_URL}/columns/{column_id}/posts'
                data = {
                    'title': 'Add to column',
                    'comment_text': '',
                    'post_id': article_id,
                }
                
                response = self.session.post(add_url, json=data, headers=headers)
                
                if response.status_code == 201:
                    self.log_success(f"文章已添加到专栏: {column_name}")
                    return True
                else:
                    self.log_error(f"添加文章到专栏失败: {response.text}")
                    return False
            else:
                self.log_warning(f"未找到专栏: {column_name}")
                return False
                
        except Exception as e:
            self.log_error(f"添加文章到专栏时出错: {e}", exc_info=True)
            return False
    
    def _add_to_topics(self, article_id: str, topic_names: List[str]) -> bool:
        """将文章添加到话题"""
        try:
            success = True
            
            for topic_name in topic_names:
                # 1. 搜索话题
                search_url = f'{self.API_BASE_URL}/topics/search'
                params = {
                    'q': topic_name,
                    'limit': 1,
                    'offset': 0,
                }
                
                headers = {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-Xsrftoken': self._get_xsrf_token(),
                }
                
                response = self.session.get(search_url, params=params, headers=headers)
                result = response.json()
                
                if 'data' in result and result['data']:
                    topic = result['data'][0]
                    topic_id = topic['id']
                    
                    # 2. 添加到话题
                    add_url = f'{self.API_BASE_URL}/articles/{article_id}/topics'
                    data = {
                        'topic_id': topic_id,
                    }
                    
                    response = self.session.post(add_url, json=data, headers=headers)
                    
                    if response.status_code == 201:
                        self.log_success(f"文章已添加到话题: {topic_name}")
                    else:
                        self.log_error(f"添加文章到话题失败: {response.text}")
                        success = False
                else:
                    self.log_warning(f"未找到话题: {topic_name}")
                    success = False
            
            return success
                    
        except Exception as e:
            self.log_error(f"添加文章到话题时出错: {e}", exc_info=True)
            return False
