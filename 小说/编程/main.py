import configparser
import time
import os
import requests
import json
import markdown
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from bs4 import BeautifulSoup
import hashlib
import mimetypes
import logging
from pathlib import Path
import base64
from typing import Optional, Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_publisher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 全局配置
DEFAULT_COVER_IMAGE_PATH = "default_cover.jpg"
COVER_IMAGES_DIR = "f:\公众号写作\编程\temp_images"
USE_PERMANENT_MEDIA = True
MAX_RETRIES = 3
RETRY_DELAY = 5  # 重试延迟秒数

# 微信API相关配置
API_BASE_URL = "https://api.weixin.qq.com/cgi-bin"
TOKEN_URL = f"{API_BASE_URL}/token"
DRAFT_URL = f"{API_BASE_URL}/draft/add"
MEDIA_URL = f"{API_BASE_URL}/material/add_material"
TEMP_MEDIA_URL = f"{API_BASE_URL}/media/upload"
IMAGE_URL = f"{API_BASE_URL}/media/uploadimg"

# --- 全局配置 ---
DEFAULT_COVER_IMAGE_PATH = "default_cover.jpg" # 默认封面图片路径，请确保此文件存在于脚本同目录下或提供绝对路径
COVER_IMAGES_DIR = "f:\\公众号写作\\编程\\temp_images" # 封面图片目录路径

# --- 全局设置 ---
# 是否使用永久素材（如果设置为False，将使用临时上传的图片）
USE_PERMANENT_MEDIA = True  # 改为True，启用永久素材

# 公众号素材库中的永久素材media_id
# 这些是已经上传到公众号素材库中的图片，可以直接使用
# 获取方法：
# 1. 获取access_token: https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=APPID&secret=APPSECRET
# 2. 获取素材列表: https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=ACCESS_TOKEN
#    请求参数: {"type":"image", "offset":0, "count":20}
#    返回的JSON数据中会包含对应素材的media_id等信息
# 请将获取到的实际media_id替换以下占位符
PERMANENT_MEDIA_IDS = [
    "r2SuJ--pe9hF_U34Ly0J_Gnfu0A3JcEW2sJjpR9EcK2FxIZRWyBXO37XXkQQRpOk",  # 示例的永久素材media_id，需要替换为您实际的media_id
    "r2SuJ--pe9hF_U34Ly0J_CqFWTjPqbEeJJm9BhB9dD-DLuxCPjAGF4wVY9QQsU1s",  # 示例的永久素材media_id，需要替换为您实际的media_id
    "r2SuJ--pe9hF_U34Ly0J_BfCZUmJEsU8Ii9UOVi68e_jFSrwTJDJdszw8TObD1nt"   # 示例的永久素材media_id，需要替换为您实际的media_id
]

# 确保默认封面图片存在
if not os.path.exists(DEFAULT_COVER_IMAGE_PATH):
    # 如果默认封面图片不存在，创建一个空白的默认封面图片文件
    print(f"警告：默认封面图片 {DEFAULT_COVER_IMAGE_PATH} 不存在，请确保提供有效的默认封面图片")

# 确保封面图片目录存在
if not os.path.exists(COVER_IMAGES_DIR):
    try:
        os.makedirs(COVER_IMAGES_DIR)
        print(f"已创建封面图片目录: {COVER_IMAGES_DIR}")
    except Exception as e:
        print(f"创建封面图片目录失败: {e}")
        # 使用脚本所在目录作为备用
        COVER_IMAGES_DIR = os.path.dirname(os.path.abspath(__file__))
        print(f"将使用脚本所在目录作为封面图片目录: {COVER_IMAGES_DIR}")

# --- 封面图片选择 ---
def get_random_cover_image():
    """从封面图片目录中随机选择一张图片作为封面"""
    if not os.path.exists(COVER_IMAGES_DIR) or not os.path.isdir(COVER_IMAGES_DIR):
        print(f"警告：封面图片目录 {COVER_IMAGES_DIR} 不存在或不是有效目录，将使用默认封面图片")
        return DEFAULT_COVER_IMAGE_PATH
    
    # 获取目录中所有图片文件
    image_files = [f for f in os.listdir(COVER_IMAGES_DIR) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    
    if not image_files:
        print(f"警告：封面图片目录 {COVER_IMAGES_DIR} 中没有图片文件，将使用默认封面图片")
        return DEFAULT_COVER_IMAGE_PATH
    
    # 随机选择一张图片
    import random
    random_image = random.choice(image_files)
    random_image_path = os.path.join(COVER_IMAGES_DIR, random_image)
    print(f"已随机选择封面图片: {random_image_path}")
    return random_image_path

def get_permanent_media_id():
    """从预定义的永久素材media_id列表中随机选择一个"""
    # 如果全局设置不使用永久素材，直接返回None
    if not USE_PERMANENT_MEDIA:
        print("全局设置为不使用永久素材，将使用临时上传的图片")
        return None
        
    # 检查是否有配置永久素材media_id
    if not PERMANENT_MEDIA_IDS or all(id.startswith("MEDIA_ID_") for id in PERMANENT_MEDIA_IDS):
        print("警告：没有配置有效的永久素材media_id，将使用临时上传的图片")
        return None
        
    import random
    media_id = random.choice(PERMANENT_MEDIA_IDS)
    print(f"使用公众号素材库中的永久素材: media_id={media_id}")
    return media_id

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
    def __init__(self, app_id: str, app_secret: str):
        """初始化微信公众号API客户端
        
        Args:
            app_id (str): 微信公众号的APPID
            app_secret (str): 微信公众号的APPSECRET
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        logger.info(f"WeChatMP 初始化完成，AppID: {app_id}")

    def _get_access_token(self) -> Optional[str]:
        """获取或刷新Access Token
        
        使用微信推荐的稳定版接口获取token，如果失败则回退到传统方式。
        
        Returns:
            Optional[str]: 有效的Access Token，如果获取失败返回None
        """
        now = time.time()
        if self.access_token and now < self.token_expires_at:
            logger.info(f"使用缓存的access_token，过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_expires_at))}")
            return self.access_token

        logger.info("正在获取新的access_token...")
        # 使用微信推荐的稳定版接口获取token
        url = "https://api.weixin.qq.com/cgi-bin/stable/token"
        post_data = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            logger.info("正在尝试使用稳定版API获取Access Token...")
            response = self.session.post(url, json=post_data)
            response.raise_for_status()
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
        except json.JSONDecodeError as e:
            logger.error(f"解析 Access Token 响应失败: {e}")
            return None

    def upload_permanent_media(self, file_path: str, media_type: str = 'image') -> Optional[str]:
        """上传永久素材（图片）
        
        与普通的upload_media不同，这个方法返回media_id而非URL，用于草稿箱上传
        
        Args:
            file_path (str): 要上传的文件路径
            media_type (str, optional): 素材类型，默认为'image'
            
        Returns:
            Optional[str]: 成功返回media_id，失败返回None
        """
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
                    errmsg = data.get('errmsg', '未知错误')
                    logger.error(f"上传永久素材失败: {errmsg}")
                    return None
        except FileNotFoundError as e:
            logger.error(f"错误：素材文件未找到 {file_path}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"上传永久素材时发生网络错误: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析上传永久素材响应失败: {e}")
            return None
            
    def upload_media(self, file_path: str, media_type: str = 'image') -> Optional[str]:
        """上传永久素材（兼容性方法，内部调用upload_permanent_media）
        
        Args:
            file_path (str): 要上传的文件路径
            media_type (str, optional): 素材类型，默认为'image'
            
        Returns:
            Optional[str]: 成功返回media_id，失败返回None
        """
        return self.upload_permanent_media(file_path, media_type)

    def upload_temp_media(self, file_path: str, media_type: str = 'image') -> Optional[str]:
        """上传临时素材
        
        Args:
            file_path (str): 要上传的文件路径
            media_type (str, optional): 素材类型，默认为'image'
            
        Returns:
            Optional[str]: 成功返回media_id，失败返回None
        """
        token = self._get_access_token()
        if not token:
            return None

        url = f"{TEMP_MEDIA_URL}?access_token={token}&type={media_type}"
        
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

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
        except Exception as e:
            logger.error(f"上传临时素材时发生错误: {e}")
            return None

    def upload_image_for_article(self, file_path: str) -> Optional[str]:
        """上传图文消息内的图片
        
        Args:
            file_path (str): 要上传的图片路径
            
        Returns:
            Optional[str]: 成功返回图片URL，失败返回None
        """
        token = self._get_access_token()
        if not token:
            return None

        url = f"{IMAGE_URL}?access_token={token}"
        
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f, mime_type)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                
                if 'url' in data:
                    logger.info(f"图文消息图片上传成功: url={data['url']}")
                    return data['url']
                else:
                    logger.error(f"上传图文消息图片失败: {data.get('errmsg', '未知错误')}")
                    return None
        except Exception as e:
            logger.error(f"上传图文消息图片时发生错误: {e}")
            return None

    def upload_draft(self, title: str, content: str, author: str = "", 
                    thumb_media_id: Optional[str] = None, 
                    digest: str = "", content_source_url: str = "") -> Optional[str]:
        """上传草稿到微信公众号
        
        Args:
            title (str): 文章标题
            content (str): 文章内容
            author (str, optional): 作者. Defaults to "".
            thumb_media_id (Optional[str], optional): 封面图片的media_id. Defaults to None.
            digest (str, optional): 摘要. Defaults to "".
            content_source_url (str, optional): 原文链接. Defaults to "".
            
        Returns:
            Optional[str]: 成功返回草稿的media_id，失败返回None
        """
        token = self._get_access_token()
        if not token:
            logger.error("无法获取有效的Access Token，无法上传草稿")
            return None

        # 检查标题长度并处理
        original_title = title
        title = self._ensure_title_length(title, max_bytes=40)
        if original_title != title:
            logger.info(f"标题已截断: 原标题={original_title}, 新标题={title}")

        url = f"{DRAFT_URL}?access_token={token}"
        
        try:
            article = {
                "title": title,
                "author": author,
                "content": content,
                "digest": digest,
                "content_source_url": content_source_url,
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }

            if thumb_media_id:
                article["thumb_media_id"] = thumb_media_id

            data = {"articles": [article]}
            response = self.session.post(url, json=data)
            response.raise_for_status()
            result = response.json()

            if result.get('errcode') == 0:
                media_id = result.get('media_id')
                logger.info(f"草稿上传成功，media_id: {media_id}")
                return media_id
            else:
                error_code = result.get('errcode')
                error_msg = result.get('errmsg')
                hint = result.get('hint', '')
                rid = result.get('rid', '')
                logger.error(f"上传草稿失败 [错误码:{error_code}]: {error_msg} hint: [{hint}] rid: {rid}")
                
                if error_code == 45003:  # title size out of limit
                    logger.error(f"标题长度超出限制: 当前标题长度={len(title.encode('utf-8'))}字节")
                elif error_code == 40007:  # invalid media_id
                    logger.error("封面图片media_id无效，可能是因为：")
                    logger.error("1. 素材已过期（临时素材有效期为3天）")
                    logger.error("2. 素材上传失败或未成功获取media_id")
                    logger.error("3. 使用了错误的media_id格式")
                    logger.error("4. 微信服务器尚未完全处理该素材")
                    logger.error("5. 图片大小超过限制（建议小于2MB）")
                    logger.error("6. 图片尺寸不符合要求（建议900x500像素）")
                    logger.error(f"当前使用的media_id: {thumb_media_id}")
                
                return None
        except Exception as e:
            logger.error(f"上传草稿时发生错误: {e}")
            return None

    def _ensure_title_length(self, title: str, max_bytes: int = 40, ellipsis: str = '...') -> str:
        """确保标题长度不超过指定字节数
        
        Args:
            title (str): 原始标题
            max_bytes (int, optional): 最大字节数限制. Defaults to 40.
            ellipsis (str, optional): 截断后添加的省略号. Defaults to '...'.
            
        Returns:
            str: 处理后的标题
        """
        if len(title.encode('utf-8')) <= max_bytes:
            return title

        # 计算截断位置
        bytes_count = 0
        for i, char in enumerate(title):
            bytes_count += len(char.encode('utf-8'))
            if bytes_count > max_bytes - len(ellipsis.encode('utf-8')):
                return title[:i] + ellipsis
        return title + ellipsis

    # _get_access_token 方法已经在前面定义，这里删除重复的定义
    def upload_image_for_article(self, file_path: str) -> Optional[str]:
        """上传图文消息内的图片
        
        Args:
            file_path (str): 要上传的图片路径
            
        Returns:
            Optional[str]: 成功返回图片URL，失败返回None
        """
        token = self._get_access_token()
        if not token:
            logger.error("无法获取有效的Access Token，无法上传图片")
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"图片文件不存在: {file_path}")
                return None
                
            # 自动检测 MIME 类型
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f, mime_type)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                
                if 'url' in data:
                    logger.info(f"图文消息图片上传成功: url={data['url']}")
                    return data['url']
                else:
                    error_msg = data.get('errmsg', '未知错误')
                    error_code = data.get('errcode', 'unknown')
                    logger.error(f"上传图文消息图片失败 [错误码:{error_code}]: {error_msg}")
                    return None
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"上传图文消息图片时发生网络错误: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"解析上传图片响应失败: {e}")
            return None
        except Exception as e:
            logger.error(f"上传图文消息图片时发生未知错误: {e}")
            return None

    def upload_draft(self, title, content, author="", thumb_media_id=None, digest="", content_source_url=""):
        """上传草稿到微信公众号
        
        注意: thumb_media_id 必须是已上传到微信服务器的永久素材media_id
        临时素材media_id不能用于草稿箱, 需要先通过素材管理接口上传为永久素材
        
        Args:
            title (str): 文章标题
            content (str): 文章内容
            author (str, optional): 作者. 默认为空字符串
            thumb_media_id (str, optional): 封面图片的media_id, 必须是有效的已上传到微信的素材ID
            digest (str, optional): 摘要. 默认为空字符串
            content_source_url (str, optional): 原文链接. 默认为空字符串
            
        Returns:
            str or None: 成功返回草稿的media_id, 失败返回None
        """
        # 获取最新的access_token
        access_token = self._get_access_token()
        if not access_token:
            print("无法获取有效的Access Token，无法上传草稿")
            return None
        
        # 检查标题长度并处理 - 直接使用更保守的字节限制，确保一次成功
        # 微信公众号API限制标题最大长度为64字节（约32个汉字）
        # 由于中文字符在UTF-8编码下占3个字节，英文占1个字节，需要特别处理
        original_title = title
        # 使用更保守的限制（40字节），确保一次通过
        title = self._ensure_title_length(title, max_bytes=40)
        if original_title != title:
            print(f"上传前检查：标题超出微信限制，已截断为：{title}（{len(title.encode('utf-8'))}字节）")
        
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
        
        # 准备请求数据
        article = {
            "title": title,
            "author": author,
            "content": content,
            "digest": digest,
            "content_source_url": content_source_url,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }
        
        # 只有当传入有效的thumb_media_id时才添加到请求中
        if thumb_media_id:
            article["thumb_media_id"] = thumb_media_id
            print(f"使用封面图片media_id: {thumb_media_id}")
        else:
            print("注意：没有指定封面图片，微信API可能返回错误")
        
        # 创建请求数据
        data = {"articles": [article]}

        try:
            # 打印请求详情，帮助调试
            print(f"正在上传草稿到微信公众号...")
            
            # 发送请求 - 移除重试逻辑，确保一次成功
            response = requests.post(url, json=data)
            result = response.json()
            
            if result.get('errcode') == 0:
                media_id = result.get('media_id')
                print(f"草稿上传成功，media_id: {media_id}")
                return media_id
            else:
                error_code = result.get('errcode')
                error_msg = result.get('errmsg')
                hint = result.get('hint', '')
                rid = result.get('rid', '')
                print(f"上传草稿失败 [错误码:{error_code}]: {error_msg} hint: [{hint}] rid: {rid}")
                
                # 提供详细的错误解释
                if error_code == 45003:  # title size out of limit
                    print("错误原因：文章标题长度超出限制，微信公众号标题最大支持64字节（约32个汉字）")
                    print(f"当前标题长度: {len(title.encode('utf-8'))}字节")
                    print("请检查_ensure_title_length函数的max_bytes参数，可能需要设置更小的值")
                elif error_code == 40007:  # invalid media_id
                    print("错误原因：封面图片media_id无效，可能是因为：")
                    print("1. 素材已过期（临时素材有效期为3天）")
                    print("2. 素材上传失败或未成功获取media_id")
                    print("3. 使用了错误的media_id格式")
                    print("4. 微信服务器尚未完全处理该素材")
                    print("5. 图片大小超过限制（建议小于2MB）")
                    print("6. 图片尺寸不符合要求（建议900x500像素）")
                    print("7. APPID和APPSECRET配置错误，导致没有权限访问该素材")
                    print(f"当前使用的media_id: {thumb_media_id}")
                
                return None
        except Exception as e:
            print(f"上传草稿时发生错误: {e}")
            return None
    def _ensure_title_length(self, title, max_bytes=40, ellipsis='...'):
        """确保标题长度不超过微信公众号API限制
        
        参数:
            title: 原始标题
            max_bytes: 最大字节数限制，默认40字节（更保守设置，微信限制为64字节）
            ellipsis: 截断后添加的省略号
            
        返回:
            处理后的标题，确保字节长度不超过max_bytes
        """
        # 计算省略号的字节长度
        ellipsis_bytes = len(ellipsis.encode('utf-8'))
        # 计算标题的字节长度
        title_bytes = title.encode('utf-8')
        
        # 如果标题字节长度已经在限制范围内，直接返回
        if len(title_bytes) <= max_bytes:
            return title
            
        # 计算安全的截断位置，避免截断中文字符
        safe_length = 0
        safe_index = 0
        # 预留省略号的字节空间
        effective_max = max_bytes - ellipsis_bytes
        
        for i, char in enumerate(title):
            char_bytes = char.encode('utf-8')
            # 如果添加当前字符会超出限制，就在这里截断
            if safe_length + len(char_bytes) > effective_max:
                break
            safe_length += len(char_bytes)
            safe_index = i + 1
        
        # 截断标题并添加省略号
        truncated_title = title[:safe_index] + ellipsis
        print(f"标题已截断：{truncated_title}（{len(truncated_title.encode('utf-8'))}字节）")
        return truncated_title

    def upload_image_for_article(self, file_path):
        """上传图文消息内的图片，返回图片 URL"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        try:
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                mime_type = 'application/octet-stream'

            with open(file_path, 'rb') as f:
                files = {'media': (os.path.basename(file_path), f, mime_type)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                if 'url' in data:
                    print(f"图文消息图片上传成功: url={data['url']}")
                    return data['url']
                else:
                    print(f"上传图文消息图片失败: {data.get('errmsg', '未知错误')}")
                    return None
        except FileNotFoundError:
            print(f"错误：图片文件未找到 {file_path}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"上传图文消息图片时发生网络错误: {e}")
            return None



def markdown_to_html(md_content: str, base_path: str, wechat_mp) -> str:
    """将Markdown内容转换为适合微信公众号的HTML内容
    
    Args:
        md_content: Markdown格式的内容
        base_path: Markdown文件所在的目录路径，用于解析相对路径的图片
        wechat_mp: 微信公众号API实例，用于上传图片
        
    Returns:
        str: 转换后的HTML内容，图片已上传到微信服务器并替换为微信图片URL
    """
    # 使用markdown库将Markdown转换为HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # 使用BeautifulSoup解析HTML，便于处理图片
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 处理图片标签
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src')
        if not src:
            continue
            
        # 处理相对路径
        if not src.startswith(('http://', 'https://', '/')): 
            img_path = os.path.join(base_path, src)
            if os.path.exists(img_path):
                # 上传图片到微信服务器
                wx_url = wechat_mp.upload_image_for_article(img_path)
                if wx_url:
                    img['src'] = wx_url
                    logger.info(f"图片已上传到微信服务器: {src} -> {wx_url}")
                else:
                    logger.warning(f"图片上传失败: {img_path}")
            else:
                logger.warning(f"图片文件不存在: {img_path}")
        elif src.startswith(('http://', 'https://')):
            # 对于网络图片，可以选择下载后上传到微信服务器
            # 这里简化处理，直接保留原URL
            logger.info(f"使用网络图片: {src}")
    
    # 返回处理后的HTML内容
    return str(soup)

class MarkdownHandler(FileSystemEventHandler):
    def __init__(self, wechat_mp_instance, base_path):
        self.wechat_mp = wechat_mp_instance
        self.base_path = base_path
        self.processed_files = set()  # 记录已处理的文件哈希，防止重复处理
        
        # 确保base_path存在
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path, exist_ok=True)
            logger.info(f"创建目录: {self.base_path}")
            
        logger.info(f"MarkdownHandler 初始化完成，监控目录: {self.base_path}")

    def process_file(self, file_path):
        """处理单个 Markdown 文件"""
        # 检查文件扩展名
        if not file_path.lower().endswith('.md'):
            return
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题和作者
            title = os.path.basename(file_path).replace('.md', '')
            author = "AI编程助手"  # 默认作者
            
            # 查找YAML front matter中的标题和作者
            yaml_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
            if yaml_match:
                yaml_content = yaml_match.group(1)
                title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1)
                
                author_match = re.search(r'author:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
                if author_match:
                    author = author_match.group(1)
                
                # 移除YAML front matter
                content = content[yaml_match.end():]
                
            # 限制标题长度，微信公众号要求标题不超过64字节，这里我们使用更保守的40字节限制
            # 使用_ensure_title_length方法处理标题长度，确保一致性
            original_title = title
            title = self.wechat_mp._ensure_title_length(title, max_bytes=40)
            if original_title != title:
                print(f"标题长度超出限制，已自动截断:\n原标题: {original_title}\n新标题: {title}")
                
            print(f"文章标题: {title}")
            print(f"作者: {author}")
            
            # 计算文件内容的哈希值，用于检测重复处理
            file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # 如果文件哈希已处理过，则跳过
            if file_hash in self.processed_files:
                return
                
            # 处理Markdown内容
            html_content = markdown_to_html(content, os.path.dirname(file_path), self.wechat_mp)
            
            # 上传文章到微信公众号草稿箱
            max_retries = 3
            retry_count = 0
            success = False
            
            while retry_count < max_retries:
                retry_count += 1
                
                # 先上传封面图片作为永久素材获取media_id
                print(f"正在上传永久素材作为封面图片，尝试第 {retry_count}/{max_retries} 次...")
                # 随机选择一张图片作为封面
                cover_image_path = get_random_cover_image()
                if not cover_image_path:
                    print("无法获取封面图片，将尝试下一次重试")
                    time.sleep(5)
                    continue
                    
                # 使用新的方法上传永久素材，获取media_id
                thumb_media_id = self.wechat_mp.upload_permanent_media(cover_image_path, 'image')
                if not thumb_media_id:
                    print("上传封面图片失败，将尝试下一次重试")
                    time.sleep(5)
                    continue
                
                # 永久素材已处理完毕，无需等待，直接使用
                print(f"正在使用永久素材封面上传草稿，尝试第 {retry_count}/{max_retries} 次...")
                media_id = self.wechat_mp.upload_draft(title, html_content, author, thumb_media_id)
                
                if media_id:
                    self.processed_files.add(file_hash) # 标记为已处理
                    print(f"文件 {os.path.basename(file_path)} 上传成功，草稿media_id: {media_id}")
                    return True
                
                if media_id:
                    self.processed_files.add(file_hash) # 标记为已处理
                    print(f"文件 {os.path.basename(file_path)} 上传成功（无封面），草稿media_id: {media_id}")
                    return True
                else:
                    print(f"上传草稿失败，正在重试...")
                    if retry_count < max_retries:
                        print(f"上传失败，正在进行第 {retry_count + 1} 次尝试...")
                    time.sleep(5)  # 等待5秒后重试
            
            print(f"文件 {os.path.basename(file_path)} 上传失败，已达到最大重试次数 {max_retries}。")
            return False
            
        except Exception as e:
            print(f"处理文件 {file_path} 时发生错误: {e}")
            return False

    def on_created(self, event):
        """文件或目录被创建时调用"""
        if not event.is_directory:
            self.process_file(event.src_path)

    def on_modified(self, event):
        """文件或目录被修改时调用"""

# Markdown转换为HTML
def markdown_to_html(md_content: str, base_path: str, wechat_mp: WeChatMP) -> str:
    # 使用markdown库将Markdown转换为HTML
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # 使用BeautifulSoup解析HTML，便于处理图片
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 处理图片标签
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src')
        if not src:
            continue
            
        # 处理相对路径
        if not src.startswith(('http://', 'https://', '/')): 
            img_path = os.path.join(base_path, src)
            if os.path.exists(img_path):
                # 上传图片到微信服务器
                wx_url = wechat_mp.upload_image_for_article(img_path)
                if wx_url:
                    img['src'] = wx_url
                    logger.info(f"图片已上传到微信服务器: {src} -> {wx_url}")
                else:
                    logger.warning(f"图片上传失败: {img_path}")
            else:
                logger.warning(f"图片文件不存在: {img_path}")
        elif src.startswith(('http://', 'https://')):
            # 对于网络图片，可以选择下载后上传到微信服务器
            # 这里简化处理，直接保留原URL
            logger.info(f"使用网络图片: {src}")
    
    # 返回处理后的HTML内容
    return str(soup)

# 获取随机封面图片
def get_random_cover_image() -> Optional[str]:
    # 这里需要实现具体的封面图片获取逻辑
    pass

# 获取预定义的永久素材media_id
def get_permanent_media_id() -> Optional[str]:
    # 这里需要实现具体的永久素材media_id获取逻辑
    pass

# 处理单个Markdown文件并发布到微信公众号草稿箱
def publish_single_markdown(md_path: str, author: str = "AI助手") -> bool:
    """处理单个Markdown文件并发布到微信公众号草稿箱
    
    Args:
        md_path (str): Markdown文件路径
        author (str, optional): 作者. Defaults to "AI助手".
        
    Returns:
        bool: 发布是否成功
    """
    if not os.path.exists(md_path):
        logger.error(f"文件不存在: {md_path}")
        return False
        
    if not md_path.lower().endswith('.md'):
        logger.error(f"不是Markdown文件: {md_path}")
        return False
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

        # 4. 转换 Markdown 为 HTML 并处理图片
        base_path = os.path.dirname(md_path)
        html_content = markdown_to_html(md_content, base_path, wechat_api)
        
        # 5. 处理封面图片
        thumb_media_id = None
        
        # 优先使用预定义的永久素材
        if USE_PERMANENT_MEDIA and PERMANENT_MEDIA_IDS:
            thumb_media_id = get_permanent_media_id()
            logger.info(f"使用预定义的永久素材media_id: {thumb_media_id}")
        
        # 如果没有永久素材，上传临时素材
        if not thumb_media_id:
            cover_image_path = get_random_cover_image()
            if cover_image_path and cover_image_path != DEFAULT_COVER_IMAGE_PATH:
                # 上传临时素材作为封面
                thumb_media_id = wechat_api.upload_temp_media(cover_image_path, media_type='image')
                if thumb_media_id:
                    logger.info(f"临时素材上传成功: media_id={thumb_media_id}")
                else:
                    logger.error(f"封面图片上传失败: {cover_image_path}")
            else:
                logger.warning("未找到有效的封面图片，将尝试使用默认图片")
                # 如果默认图片存在，上传默认图片
                if os.path.exists(DEFAULT_COVER_IMAGE_PATH):
                    thumb_media_id = wechat_api.upload_temp_media(DEFAULT_COVER_IMAGE_PATH, media_type='image')
                    if thumb_media_id:
                        logger.info(f"默认封面图片上传成功: media_id={thumb_media_id}")
                    else:
                        logger.error("默认封面图片上传失败，将不使用封面")
                else:
                    logger.error(f"默认封面图片不存在: {DEFAULT_COVER_IMAGE_PATH}")

        # 6. 上传草稿
        success = False
        retry_count = 0
        
        while retry_count < MAX_RETRIES and not success:
            try:
                success = wechat_api.upload_draft(title, html_content, author, thumb_media_id)
                if success:
                    logger.info(f"《{title}》已成功上传到公众号草稿箱！")
                    return True
                else:
                    retry_count += 1
                    if retry_count < MAX_RETRIES:
                        logger.info(f"上传失败，正在进行第 {retry_count + 1} 次尝试...")
                        time.sleep(RETRY_DELAY)  # 等待后重试
                    else:
                        logger.error(f"上传失败，已达到最大重试次数 {MAX_RETRIES}")
                        return False
            except Exception as e:
                logger.error(f"上传草稿时发生错误: {e}")
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)
                else:
                    logger.error(f"上传失败，已达到最大重试次数 {MAX_RETRIES}")
                    return False
        
        return False
    except Exception as e:
        logger.error(f"处理文件 {md_path} 时出错: {e}")
        return False

# 将指定 Markdown 文件或目录中的所有Markdown文件发布到微信公众号草稿箱
def publish_markdown_to_wechat(md_path: str, author: str = "AI助手") -> bool:
    """将指定 Markdown 文件或目录中的所有Markdown文件发布到微信公众号草稿箱
    
    Args:
        md_path (str): Markdown文件路径或目录路径
        author (str, optional): 作者. Defaults to "AI助手".
        
    Returns:
        bool: 是否有文件成功发布
    """
    success = False
    
    # 如果是目录，处理目录中的所有Markdown文件
    # 检查路径是文件还是目录
    if os.path.isdir(md_path):
        print(f"检测到目录路径: {md_path}，将处理目录中的所有Markdown文件")
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
                    print(f"处理文件 {filename} 时出错: {e}")
        
        if total_md_files > 0:
            print(f"目录处理完成: 共发现 {total_md_files} 个Markdown文件，成功上传 {success_count} 个")
        else:
            print(f"目录 {md_path} 中未找到任何Markdown文件")
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

        if not app_id or app_id == 'YOUR_APP_ID' or not app_secret or app_secret == 'YOUR_APP_SECRET':
            print("错误：请在 config.ini 文件中配置有效的 APP_ID 和 APP_SECRET！")
            return
            
        # 确保监控目录存在
        if not monitor_folder:
            print("错误：请在配置文件中设置 MONITOR_FOLDER 监控目录！")
            return
            
        if not os.path.exists(monitor_folder):
            try:
                os.makedirs(monitor_folder)
                print(f"监控目录 '{monitor_folder}' 不存在，已自动创建")
            except Exception as e:
                print(f"无法创建监控目录 '{monitor_folder}': {e}")
                print(f"请检查配置文件中的 MONITOR_FOLDER 路径是否正确")
                return
        elif not os.path.isdir(monitor_folder):
            print(f"错误：监控路径 '{monitor_folder}' 不是一个有效的目录！")
            print(f"请检查配置文件中的 MONITOR_FOLDER 设置")
            return
            
        monitor_folder_abs = os.path.abspath(monitor_folder)
        print(f"开始监控文件夹: {monitor_folder_abs}")

        # 初始化微信 API 实例
        wechat_mp = WeChatMP(app_id, app_secret)

        # 初始化文件系统事件处理器
        event_handler = MarkdownHandler(wechat_mp, monitor_folder_abs)
        
        # 扫描初始文件 (可选，如果需要处理启动时已存在的文件)
        print("正在扫描初始文件...")
        for filename in os.listdir(monitor_folder_abs):
            if filename.lower().endswith('.md'):
                file_path = os.path.join(monitor_folder_abs, filename)
                event_handler.process_file(file_path)
        print("初始文件扫描完成。")

        # 初始化并启动观察者
        observer = Observer()
        observer.schedule(event_handler, monitor_folder_abs, recursive=True)  # 递归监控所有子目录
        observer.start()
        print(f"文件监控已启动，每 {check_interval} 秒检查一次文件变化")
        print("按 Ctrl+C 停止监控。")

        try:
            while True:
                time.sleep(check_interval) # 使用配置的检查间隔，但 watchdog 是实时触发的
        except KeyboardInterrupt:
            observer.stop()
            print("\n监控已停止。")
        observer.join()

    except FileNotFoundError as e:
        print(e)
    except configparser.NoSectionError as e:
        print(f"配置文件错误：缺少 Section [{e.section}]")
    except configparser.NoOptionError as e:
        print(f"配置文件错误：Section [{e.section}] 缺少 Option '{e.option}'")
    except Exception as e:
        print(f"发生未预料的错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()