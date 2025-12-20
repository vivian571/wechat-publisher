#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信公众号文章自动发布工具
功能：
1. 监控指定目录的Markdown文件变化
2. 自动将Markdown转换为适合公众号的HTML格式
3. 上传到微信公众号草稿箱
4. 支持图片自动处理和上传
"""

import os
import sys
import time
import json
import random
import string
import logging
import requests
import aiohttp
import asyncio
import configparser
import mimetypes
import markdown
import re
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from bs4 import BeautifulSoup
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("wechat_publisher.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- 全局配置 ---
DEFAULT_COVER_IMAGE_PATH = "default_cover.jpg"  # 默认封面图片路径
COVER_IMAGES_DIR = "f:\\公众号写作\\编程\\temp_images"  # 封面图片目录路径
USE_PERMANENT_MEDIA = True  # 是否使用永久素材
PERMANENT_MEDIA_IDS = [
    "r2SuJ--pe9hF_U34Ly0J_Gnfu0A3JcEW2sJjpR9EcK2FxIZRWyBXO37XXkQQRpOk",
    "r2SuJ--pe9hF_U34Ly0J_CqFWTjPqbEeJJm9BhB9dD-DLuxCPjAGF4wVY9QQsU1s",
    "r2SuJ--pe9hF_U34Ly0J_BfCZUmJEsU8Ii9UOVi68e_jFSrwTJDJdszw8TObD1nt"
]

# 确保封面图片目录存在
if not os.path.exists(COVER_IMAGES_DIR):
    try:
        os.makedirs(COVER_IMAGES_DIR)
        logger.info(f"已创建封面图片目录: {COVER_IMAGES_DIR}")
    except Exception as e:
        logger.error(f"创建封面图片目录失败: {e}")
        COVER_IMAGES_DIR = os.path.dirname(os.path.abspath(__file__))
        logger.info(f"将使用脚本所在目录作为封面图片目录: {COVER_IMAGES_DIR}")

# --- 封面图片选择 ---
def get_random_cover_image():
    """从封面图片目录中随机选择一张图片作为封面"""
    if not os.path.exists(COVER_IMAGES_DIR) or not os.path.isdir(COVER_IMAGES_DIR):
        logger.warning(f"封面图片目录 {COVER_IMAGES_DIR} 不存在或不是有效目录，将使用默认封面图片")
        return DEFAULT_COVER_IMAGE_PATH
    
    # 获取目录中所有图片文件
    image_files = [f for f in os.listdir(COVER_IMAGES_DIR) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    if not image_files:
        logger.warning(f"封面图片目录 {COVER_IMAGES_DIR} 中没有图片文件，将使用默认封面图片")
        return DEFAULT_COVER_IMAGE_PATH
    
    # 随机选择一张图片
    random_image = random.choice(image_files)
    random_image_path = os.path.join(COVER_IMAGES_DIR, random_image)
    logger.info(f"已随机选择封面图片: {random_image_path}")
    return random_image_path

def check_title_length(title, platform='wechat'):
    """检查标题长度是否符合平台要求
    Args:
        title: 要检查的标题
        platform: 平台名称，默认为'wechat'
    Returns:
        bool: 是否符合要求
    """
    # 使用UTF-8编码计算字节长度
    title_bytes = title.encode('utf-8')
    byte_length = len(title_bytes)
    
    # 各平台的限制
    limits = {
        'wechat': 64,  # 微信公众平台限制
        'other': 128   # 其他平台通用限制
    }
    
    max_length = limits.get(platform, limits['other'])
    if byte_length > max_length:
        logger.warning(f"标题长度超出{platform}平台限制（{byte_length}/{max_length}字节）")
        return False
    return True

def get_valid_title(title, platform='wechat'):
    """获取符合平台要求的标题
    Args:
        title: 原始标题
        platform: 平台名称
    Returns:
        str: 符合要求的标题
    """
    if check_title_length(title, platform):
        return title
        
    # 如果超出长度，尝试截断
    while title:
        # 每次截断一个字符
        title = title[:-1]
        if check_title_length(title, platform):
            return title
    
    return ""

def sanitize_filename(filename):
    """清理文件名，去除特殊字符"""
    # 去除非法字符
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleaned_filename = ''.join(c for c in filename if c in valid_chars)
    # 如果文件名为空，使用默认名称
    if not cleaned_filename:
        cleaned_filename = 'image'
    return cleaned_filename

def upload_permanent_media(self, image_path):
    """上传新的永久图片素材"""
    try:
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
        
        # 使用requests直接上传
        with open(image_path, 'rb') as f:
            # 清理文件名
            safe_filename = sanitize_filename(os.path.basename(image_path))
            files = {
                'media': (safe_filename, f, 'image/jpeg')
            }
            
            logger.info(f"正在上传永久图片素材: {image_path}")
            response = requests.post(url, files=files)
            response.raise_for_status()
            result = response.json()
            
            if 'media_id' in result:
                logger.info(f"永久图片素材上传成功: {result['media_id']}")
                return result['media_id']
            else:
                logger.error(f"上传永久图片素材失败: {result.get('errmsg', '未知错误')}")
                return None
    except Exception as e:
        logger.error(f"上传永久图片素材时发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def get_permanent_media_ids_from_api():
    """从微信公众号API获取永久图片素材列表"""
    try:
        # 加载配置
        config = load_config()
        app_id = config.get('WeChat', 'APP_ID', fallback=None)
        app_secret = config.get('WeChat', 'APP_SECRET', fallback=None)
        
        if not app_id or not app_secret:
            logger.error("错误：获取永久素材列表时未找到APP_ID或APP_SECRET")
            return []
            
        # 创建临时WeChatMP实例来获取access_token
        wechat_api = WeChatMP(app_id, app_secret)
        token = wechat_api._get_access_token()
        if not token:
            logger.error("获取access_token失败，无法获取永久素材列表")
            return []
        
        # 调用获取素材总数接口
        count_url = f"https://api.weixin.qq.com/cgi-bin/material/get_materialcount?access_token={token}"
        count_response = requests.get(count_url)
        count_data = count_response.json()
        
        if 'image_count' not in count_data:
            logger.error(f"获取素材总数失败: {count_data.get('errmsg', '未知错误')}")
            return []
            
        image_count = count_data['image_count']
        logger.info(f"当前公众号共有 {image_count} 个永久图片素材")
        
        # 调用批量获取素材列表接口
        url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={token}"
        post_data = {
            "type": "image",
            "offset": 0,
            "count": min(20, image_count)  # 最多获取20个素材
        }
        
        logger.info("正在从微信公众号获取永久图片素材列表...")
        response = requests.post(url, json=post_data)
        response.raise_for_status()
        data = response.json()
        
        if 'item' in data and isinstance(data['item'], list):
            # 只获取有效的图片素材ID
            media_ids = []
            for item in data['item']:
                if 'media_id' in item:
                    media_id = item['media_id']
                    # 验证素材是否可用
                    verify_url = f"https://api.weixin.qq.com/cgi-bin/material/get_material?access_token={token}"
                    verify_response = requests.post(verify_url, json={"media_id": media_id})
                    if verify_response.status_code == 200:
                        media_ids.append(media_id)
                        logger.info(f"验证永久素材可用: {media_id}")
                    else:
                        logger.warning(f"永久素材不可用: {media_id}")
            
            logger.info(f"成功获取并验证 {len(media_ids)} 个有效的永久图片素材ID")
            return media_ids
        else:
            logger.error(f"获取永久素材列表失败: {data.get('errmsg', '未知错误')}")
            return []
    except Exception as e:
        logger.error(f"获取永久素材列表时发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []

def get_permanent_media_id():
    """从微信公众号获取永久素材media_id"""
    try:
        # 加载配置
        config = load_config()
        app_id = config.get('WeChat', 'APP_ID', fallback=None)
        app_secret = config.get('WeChat', 'APP_SECRET', fallback=None)
        
        if not app_id or not app_secret:
            logger.error("错误：获取永久素材时未找到APP_ID或APP_SECRET")
            return None
            
        # 创建临时WeChatMP实例
        wechat_api = WeChatMP(app_id, app_secret)
        
        # 使用预定义的永久素材ID
        permanent_media_ids = [
            "r2SuJ--pe9hF_U34Ly0J_DFvLUeMwFNgAV-pR2F2VlHO9JMMOCfBd9WIUNStkYT4"
        ]
        
        # 使用指定的永久素材ID
        if permanent_media_ids:
            selected_id = permanent_media_ids[0]
            logger.info(f"使用指定的永久素材media_id: {selected_id}")
            return selected_id
        
        logger.warning("未找到可用的永久素材，将使用临时素材")
        return None
        
    except Exception as e:
        logger.error(f"获取永久素材时发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# --- 配置加载 ---
def load_config(config_file='config.ini'):
    """加载配置文件"""
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件 {config_file} 未找到！请创建并配置。")
    config.read(config_file, encoding='utf-8')
    return config

# --- 微信公众号 API 操作 ---
class WeChatMP:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0
        self.session = requests.Session()
        self.retry_delay = 5  # 重试延迟时间（秒）
        self.max_retries = 3  # 最大重试次数

    def _get_access_token(self):
        """获取或刷新 Access Token，使用微信官方推荐的稳定版API"""
        now = time.time()
        if self.access_token and now < self.token_expires_at:
            return self.access_token

        # 使用微信推荐的稳定版接口获取token
        url = f"https://api.weixin.qq.com/cgi-bin/stable_token"
        post_data = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            logger.info("正在尝试使用稳定版API获取Access Token...")
            response = self.session.post(url, json=post_data)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                # 提前 10 分钟过期，避免边界问题
                self.token_expires_at = now + data.get('expires_in', 7200) - 600 
                logger.info(f"稳定版Access Token获取成功，有效期: {data.get('expires_in', 7200)}秒")
                return self.access_token
            else:
                errmsg = data.get('errmsg', '未知错误')
                error_code = data.get('errcode', 'unknown')
                logger.error(f"获取稳定版Access Token失败 [错误码:{error_code}]: {errmsg}")
                
                # 如果稳定版API失败，尝试使用旧版API
                logger.info("尝试使用传统方式获取Access Token...")
                fallback_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
                fallback_response = self.session.get(fallback_url)
                fallback_data = fallback_response.json()
                
                if 'access_token' in fallback_data:
                    self.access_token = fallback_data['access_token']
                    self.token_expires_at = now + fallback_data.get('expires_in', 7200) - 300
                    logger.info("传统方式Access Token获取成功")
                    return self.access_token
                    
                # 两种方式都失败
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"请求 Access Token 时发生网络错误: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"解析 Access Token 响应失败: {response.text}")
            return None

    def upload_temp_media(self, file_path, media_type='image'):
        """上传临时素材（图片）"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type={media_type}"
        try:
            # 自动检测 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'  # 默认类型

            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f, mime_type)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                if 'media_id' in data:
                    logger.info(f"临时素材上传成功: media_id={data['media_id']}")
                    return data['media_id']
                else:
                    logger.error(f"上传临时素材失败: {data.get('errmsg', '未知错误')}")
                    return None
        except FileNotFoundError:
            logger.error(f"错误：素材文件未找到 {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"上传临时素材时发生网络错误: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"解析上传临时素材响应失败: {response.text}")
            return None

    def upload_permanent_media(self, file_path, media_type='image'):
        """上传永久素材（图片）"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type={media_type}"
        try:
            # 自动检测 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'  # 默认类型

            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f, mime_type)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                if 'media_id' in data and 'url' in data:
                    logger.info(f"永久素材上传成功: media_id={data['media_id']}, url={data['url']}")
                    return data['media_id']  # 返回media_id供草稿箱使用
                else:
                    logger.error(f"上传永久素材失败: {data.get('errmsg', '未知错误')}")
                    return None
        except FileNotFoundError:
            logger.error(f"错误：素材文件未找到 {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"上传永久素材时发生网络错误: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"解析上传永久素材响应失败: {response.text}")
            return None

    def truncate_title(self, title, max_bytes=64):
        """截断标题使其字节数不超过指定值"""
        encoded = title.encode('utf-8')
        if len(encoded) <= max_bytes:
            return title
        
        # 二分查找最大可用长度
        left, right = 1, len(title)
        while left <= right:
            mid = (left + right) // 2
            if len(title[:mid].encode('utf-8')) <= max_bytes:
                left = mid + 1
            else:
                right = mid - 1
        



        
        return title[:right]

    def upload_draft(self, title, content, author="AI助手", thumb_media_id=None):
        """上传草稿"""
        try:
            token = self._get_access_token()
            if not token:
                return False

            url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
            
            # 确保标题长度不超过限制
            safe_title = self.truncate_title(title, max_bytes=64)
            logger.info(f"原始标题: {title}")
            logger.info(f"处理后的标题: {safe_title}")
            
            articles = [{
                "title": safe_title,
                "author": author,
                "digest": "",
                "content": content,
                "content_source_url": "",
                "thumb_media_id": thumb_media_id if thumb_media_id else "",
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }]
            
            post_data = {
                "articles": articles
            }
            
            logger.info(f"草稿上传请求: {post_data}")
            response = requests.post(url, json=post_data)
            result = response.json()
            logger.info(f"草稿上传响应: {result}")
            
            if 'errcode' in result and result['errcode'] != 0:
                logger.error(f"上传草稿失败 [错误码:{result['errcode']}]: {result.get('errmsg', '未知错误')} hint: {result.get('hint', '无提示')}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"上传草稿时发生错误: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"上传图片时发生网络错误: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"解析上传图片响应失败: {response.text}")

    def upload_image(self, file_path):
        """上传图片到微信服务器，返回可在正文中使用的URL"""
        token = self._get_access_token()
        if not token:
            return None
    
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        try:
            # 自动检测 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'  # 默认类型
    
            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f, mime_type)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                if 'url' in data:
                    logger.info(f"图片上传成功: url={data['url']}")
                    return data['url']
                else:
                    logger.error(f"上传图片失败: {data.get('errmsg', '未知错误')}")
                    return None
        except FileNotFoundError:
            logger.error(f"错误：图片文件未找到 {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"上传图片时发生网络错误: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"解析上传图片响应失败: {response.text}")
            return None
    
    def _ensure_title_length(self, title, max_bytes=40):
        """确保标题长度不超过指定字节数（微信公众号标题限制）"""
        # 计算字符串的字节长度
        def get_byte_length(s):
            return len(s.encode('utf-8'))
        
        # 如果标题字节长度已经在限制范围内，直接返回
        if get_byte_length(title) <= max_bytes:
            return title
            
        # 否则，逐字符截断直到满足字节限制
        result = ""
        for char in title:
            if get_byte_length(result + char) > max_bytes:
                break
            result += char
                
        # 如果截断后的标题以标点符号结尾，去掉结尾的标点符号
        if result and result[-1] in '，。！？、；：""''（）【】《》,.!?;:\'\"()[]<>':
            result = result[:-1]
                
        return result.strip()
    
    def upload_draft(self, title, content, author="AI助手", thumb_media_id=None):
        """上传草稿到微信公众号草稿箱"""
        token = self._get_access_token()
        if not token:
            return None
    
        # 确保标题长度符合微信要求
        title = self._ensure_title_length(title)
        
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        
        # 准备请求数据
        post_data = {
            "articles": [{
                "title": title,
                "author": author,
                "content": content,
                "digest": "",  # 摘要，可以留空
                "content_source_url": "",  # 原文链接，可以留空
                "need_open_comment": 0,  # 是否打开评论，0不打开
                "only_fans_can_comment": 0  # 是否粉丝才可评论，0所有人可评论
            }]
        }
        
        # 如果有封面图片，添加到请求数据中
        if thumb_media_id:
            post_data["articles"][0]["thumb_media_id"] = thumb_media_id
            logger.info(f"使用封面图片 media_id: {thumb_media_id}")
        
        try:
            # 添加请求前的日志记录
            logger.info(f"正在发送草稿上传请求，URL: {url}")
            logger.info(f"请求数据: {json.dumps(post_data, ensure_ascii=False)}")
            
            response = self.session.post(url, json=post_data)
            response.raise_for_status()
            data = response.json()
            
            # 添加响应的详细日志记录
            logger.info(f"草稿上传响应: {json.dumps(data, ensure_ascii=False)}")
            
            if 'media_id' in data:
                logger.info(f"草稿上传成功: media_id={data['media_id']}")
                return data['media_id']
            else:
                error_code = data.get('errcode', 'unknown')
                error_msg = data.get('errmsg', '未知错误')
                logger.error(f"上传草稿失败 [错误码:{error_code}]: {error_msg} hint: {data.get('hint', '无提示')}")
                
                # 针对特定错误码提供更详细的错误处理
                if error_code == 40007:
                    logger.error("错误原因: media_id无效或已过期，可能是临时素材未完全生效或已过期")
                    logger.error("建议: 1. 增加等待时间 2. 使用永久素材 3. 检查素材是否符合微信要求")
                
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"上传草稿时发生网络错误: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"解析上传草稿响应失败: {response.text}")
            return None
    
# --- Markdown 处理 ---
def markdown_to_html(md_content, base_path, wechat_mp_instance):
    """
    将Markdown内容转换为适合微信公众号的HTML内容
    
    参数:
        md_content: Markdown格式的内容
        base_path: Markdown文件所在的目录路径，用于解析相对路径的图片
        wechat_mp_instance: 微信公众号API实例，用于上传图片
        
    返回:
        转换后的HTML内容，图片已上传到微信服务器并替换为微信图片URL
    """
    # 使用Python-Markdown转换Markdown为HTML
    html_content = markdown.markdown(
        md_content,
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.tables',
            'markdown.extensions.toc'
        ]
    )
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
        
    # 处理图片标签，上传图片到微信服务器并替换URL
    for img in soup.find_all('img'):
        src = img.get('src', '')
        
        # 跳过已经是微信图片URL的图片
        if src.startswith('http://mmbiz.qpic.cn/') or src.startswith('https://mmbiz.qpic.cn/'):
            logger.info(f"跳过已经是微信图片的URL: {src}")
            continue
            
        # 处理相对路径
        if not src.startswith(('http://', 'https://')):
            src = os.path.join(base_path, src)
            
        # 如果是本地文件，上传到微信服务器
        if os.path.exists(src):
            try:
                # 上传图片到微信服务器
                wx_url = wechat_mp_instance.upload_image(src)
                if wx_url:
                    logger.info(f"图片已上传到微信服务器: {src} -> {wx_url}")
                    img['src'] = wx_url
                else:
                    logger.error(f"图片上传失败: {src}")
            except Exception as e:
                logger.error(f"处理图片时出错: {src}, 错误: {e}")
        else:
            logger.warning(f"图片文件不存在: {src}")
    
    # 添加微信公众号样式
    styled_html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; line-height: 1.7; color: #333;">
        {str(soup)}
    </div>
    """
    
    return styled_html
    
# --- 文件监控处理 ---
class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, wechat_mp_instance, base_path):
        self.wechat_mp = wechat_mp_instance
        self.base_path = base_path
        self.processed_files = set()  # 记录已处理的文件哈希，防止重复处理
            
    def process_file(self, file_path):
        """处理单个 Markdown 文件"""
        # 检查文件是否为Markdown
        if not file_path.lower().endswith('.md'):
            return False
            
        try:
            # 计算文件哈希值，用于判断文件是否已处理
            with open(file_path, 'rb') as f:
                file_content = f.read()
                file_hash = hashlib.md5(file_content).hexdigest()
                
            # 如果文件已处理且哈希值未变，跳过
            if file_hash in self.processed_files:
                logger.info(f"文件 {os.path.basename(file_path)} 已处理，跳过")
                return True
                
            # 读取Markdown内容
            md_content = file_content.decode('utf-8')
            
            # 提取标题（首行 # 标题）
            lines = md_content.splitlines()
            title = "Draft"  # 使用简单的标题
            
            # 处理标题长度，确保符合微信公众号API限制
            logger.info(f"使用标题: {title}")
            logger.info(f"标题字节长度: {len(title.encode('utf-8'))}")

            original_title = title
            title = self.wechat_mp._ensure_title_length(title, max_bytes=40)
            if original_title != title:
                logger.warning(f"标题长度超出限制，已自动截断:\n原标题: {original_title}\n新标题: {title}")
                
            # 转换 Markdown 为 HTML 并处理图片
            base_path = os.path.dirname(file_path)
            html_content = markdown_to_html(md_content, base_path, self.wechat_mp)
            
            # 添加重试机制
            max_retries = 3
            retry_count = 0
            
            # 检查是否使用永久素材作为封面
            permanent_media_id = get_permanent_media_id()
            
            while retry_count < max_retries:
                retry_count += 1
                
                # 如果使用永久素材
                if permanent_media_id:
                    logger.info(f"正在使用永久素材封面上传草稿，尝试第 {retry_count}/{max_retries} 次...")
                    # 添加短暂延迟，确保网络稳定
                    time.sleep(2)
                    media_id = self.wechat_mp.upload_draft(title, html_content, "AI助手", permanent_media_id)
                    
                    if media_id:
                        self.processed_files.add(file_hash)  # 标记为已处理
                        logger.info(f"文件 {os.path.basename(file_path)} 上传成功，草稿media_id: {media_id}")
                        return True
                    else:
                        logger.error(f"使用永久素材上传草稿失败，正在尝试使用临时素材...")
                        # 永久素材失败后，不再重试永久素材，直接尝试临时素材
                        permanent_media_id = None
                
                # 如果不使用永久素材或永久素材上传失败，尝试使用临时素材
                cover_image_path = get_random_cover_image()
                logger.info(f"正在上传临时素材: {cover_image_path}")
                thumb_media_id = self.wechat_mp.upload_temp_media(cover_image_path, media_type='image')
                
                if not thumb_media_id:
                    logger.error(f"错误：封面图片 {cover_image_path} 上传失败，正在重试...")
                    time.sleep(2)  # 等待2秒后重试
                    continue  # 跳过当前循环，重新尝试上传封面图片
                
                # 添加延迟，确保media_id在微信服务器上完全生效
                logger.info(f"等待15秒，确保临时素材media_id在微信服务器上生效...")
                time.sleep(15)  # 等待15秒，确保media_id生效
                
                logger.info(f"正在使用临时素材封面上传草稿，尝试第 {retry_count}/{max_retries} 次...")
                media_id = self.wechat_mp.upload_draft(title, html_content, "AI助手", thumb_media_id)
                
                if media_id:
                    self.processed_files.add(file_hash)  # 标记为已处理
                    logger.info(f"文件 {os.path.basename(file_path)} 上传成功，草稿media_id: {media_id}")
                    return True
                else:
                    logger.error(f"上传草稿失败，正在重试...")
                    if retry_count < max_retries:
                        logger.info(f"上传失败，正在进行第 {retry_count + 1} 次尝试...")
                    time.sleep(5)  # 等待5秒后重试
            
            logger.error(f"文件 {os.path.basename(file_path)} 上传失败，已达到最大重试次数 {max_retries}。")
            return False
            
        except Exception as e:
            logger.error(f"处理文件 {file_path} 时发生错误: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
                
    def on_created(self, event):
        """文件或目录被创建时调用"""
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_modified(self, event):
        """文件或目录被修改时调用"""
        # 注意：保存文件时可能会触发多次 modified 事件
        # 通过哈希值判断避免重复处理
        if not event.is_directory:
            self.process_file(event.src_path)
    
def publish_single_markdown(md_path, author="AI助手"):
    """处理单个Markdown文件并发布到微信公众号草稿箱"""
    try:
        # 1. 读取 Markdown 内容
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        # 2. 提取标题（首行 # 标题）
        lines = md_content.splitlines()
        title = os.path.basename(md_path).replace('.md', '')  # 默认使用文件名作为标题
        for line in lines:
            if line.strip().startswith('#'):
                title = line.strip('#').strip()
                break
                
        # 3. 加载配置，初始化微信API
        config = load_config()
        app_id = config['WeChat']['APP_ID']
        app_secret = config['WeChat']['APP_SECRET']
        wechat_api = WeChatMP(app_id, app_secret)
        
        # 处理标题长度，确保符合微信公众号API限制
        original_title = title
        title = wechat_api._ensure_title_length(title, max_bytes=40)
        if original_title != title:
            logger.info(f"标题长度超出限制，已自动截断:\n原标题: {original_title}\n新标题: {title}")

        # 4. 转换 Markdown 为 HTML 并处理图片
        base_path = os.path.dirname(md_path)
        html_content = markdown_to_html(md_content, base_path, wechat_api)
        
        # 添加重试机制
        max_retries = 3
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            retry_count += 1
            
            # 5. 随机选择封面图片并上传草稿 - 每次尝试都重新上传临时素材
            cover_image_path = get_random_cover_image()
            thumb_media_id = wechat_api.upload_temp_media(cover_image_path, media_type='image')
            if not thumb_media_id:
                logger.error(f"错误：封面图片 {cover_image_path} 上传失败，正在重试...")
                time.sleep(2)  # 等待2秒后重试
                continue  # 跳过当前循环，重新尝试上传封面图片
            
            # 添加延迟，确保media_id在微信服务器上完全生效
            logger.info(f"等待15秒，确保临时素材media_id在微信服务器上生效...")
            time.sleep(15)  # 等待15秒，确保media_id生效
            
            success = wechat_api.upload_draft(title, html_content, author, thumb_media_id)
            if success:
                logger.info(f"《{title}》已成功上传到公众号草稿箱！")
            else:
                if retry_count < max_retries:
                    logger.info(f"上传失败，正在进行第 {retry_count+1} 次尝试...")
                    time.sleep(2)  # 等待2秒后重试
                else:
                    logger.error(f"上传失败，已达到最大重试次数 {max_retries}，请检查日志信息。")
        return success
    except Exception as e:
        logger.error(f"处理文件 {md_path} 时出错: {e}")
        return False
    
def publish_markdown_to_wechat(md_path, author="AI助手"):
    """将指定 Markdown 文件或目录中的所有Markdown文件发布到微信公众号草稿箱"""
    # 检查路径是文件还是目录
    if os.path.isdir(md_path):
        logger.info(f"检测到目录路径: {md_path}，将处理目录中的所有Markdown文件")
        # 遍历目录中的所有文件
        success_count = 0
        total_md_files = 0
        for filename in os.listdir(md_path):
            if filename.lower().endswith('.md'):
                total_md_files += 1
                file_path = os.path.join(md_path, filename)
                try:
                    if publish_single_markdown(file_path, author):
                        success_count += 1
                except Exception as e:
                    logger.error(f"处理文件 {filename} 时出错: {e}")
        
        if total_md_files > 0:
            logger.info(f"目录处理完成: 共发现 {total_md_files} 个Markdown文件，成功上传 {success_count} 个")
        else:
            logger.info(f"目录 {md_path} 中未找到任何Markdown文件")
        return success_count > 0
    else:
        # 单个文件处理
        return publish_single_markdown(md_path, author)
    
def main():
    """主函数"""
    try:
        # 加载配置
        config = load_config()
        app_id = config.get('WeChat', 'APP_ID', fallback=None)
        app_secret = config.get('WeChat', 'APP_SECRET', fallback=None)
        monitor_folder = config.get('Monitor', 'MONITOR_FOLDER', fallback=None)
        check_interval = config.getint('Monitor', 'CHECK_INTERVAL', fallback=60)
        
        if not app_id or not app_secret:
            logger.error("错误：请在配置文件中设置 APP_ID 和 APP_SECRET！")
            return
            
        if not monitor_folder:
            logger.error("错误：请在配置文件中设置 MONITOR_FOLDER 监控目录！")
            return
            
        if not os.path.exists(monitor_folder):
            try:
                os.makedirs(monitor_folder)
                logger.info(f"监控目录 '{monitor_folder}' 不存在，已自动创建")
            except Exception as e:
                logger.error(f"无法创建监控目录 '{monitor_folder}': {e}")
                logger.error(f"请检查配置文件中的 MONITOR_FOLDER 路径是否正确")
                return
        elif not os.path.isdir(monitor_folder):
            logger.error(f"错误：监控路径 '{monitor_folder}' 不是一个有效的目录！")
            logger.error(f"请检查配置文件中的 MONITOR_FOLDER 设置")
            return
            
        monitor_folder_abs = os.path.abspath(monitor_folder)
        logger.info(f"开始监控文件夹: {monitor_folder_abs}")

        # 初始化微信 API 实例
        wechat_mp = WeChatMP(app_id, app_secret)

        # 初始化文件系统事件处理器
        event_handler = MarkdownHandler(wechat_mp, monitor_folder_abs)
        
        # 扫描初始文件 (可选，如果需要处理启动时已存在的文件)
        logger.info("正在扫描初始文件...")
        for filename in os.listdir(monitor_folder_abs):
            if filename.lower().endswith('.md'):
                file_path = os.path.join(monitor_folder_abs, filename)
                event_handler.process_file(file_path)
        logger.info("初始文件扫描完成。")

        # 初始化并启动观察者
        observer = Observer()
        observer.schedule(event_handler, monitor_folder_abs, recursive=True)  # 递归监控所有子目录
        observer.start()
        logger.info(f"文件监控已启动，每 {check_interval} 秒检查一次文件变化")
        logger.info("按 Ctrl+C 停止监控。")

        try:
            while True:
                time.sleep(check_interval)  # 使用配置的检查间隔，但 watchdog 是实时触发的
        except KeyboardInterrupt:
            observer.stop()
            logger.info("\n监控已停止。")
        observer.join()

    except FileNotFoundError as e:
        logger.error(e)
    except configparser.NoSectionError as e:
        logger.error(f"配置文件错误：缺少 Section [{e.section}]")
    except configparser.NoOptionError as e:
        logger.error(f"配置文件错误：Section [{e.section}] 缺少 Option '{e.option}'")
    except Exception as e:
        logger.error(f"发生未预料的错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
if __name__ == "__main__":
    main()