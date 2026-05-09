import os
import time
import json
import yaml
import logging
import requests
import re
from datetime import datetime, timedelta
import tempfile
from pexels_api import API
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from concurrent.futures import ThreadPoolExecutor
from markdown import Markdown
from bs4 import BeautifulSoup
from premailer import Premailer
from dotenv import load_dotenv
import urllib.parse

# --- 1. 日志配置 ---
class AccountLogFilter(logging.Filter):
    """自定义日志过滤器，为日志记录添加公众号名称。"""
    def filter(self, record):
        if not hasattr(record, 'account_name'):
            record.account_name = 'System'
        return True

def setup_logging():
    """配置日志记录器。"""
    log_format = '%(asctime)s - %(levelname)s - [%(account_name)s] - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)
    logger = logging.getLogger()
    # 确保所有处理器都使用我们的自定义过滤器
    for handler in logger.handlers:
        handler.addFilter(AccountLogFilter())

setup_logging()

# --- 2. 配置加载 ---
def load_config():
    """加载 .env 和 config.yaml 文件。"""
    load_dotenv()
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error("错误: config.yaml 文件未找到。", extra={'account_name': 'System'})
        return None
    except yaml.YAMLError as e:
        logging.error(f"解析 config.yaml 时出错: {e}", extra={'account_name': 'System'})
        return None

# --- 3. 核心业务类 ---
class WeChatPublisher:
    """处理与单个微信公众号API交互、文档处理和发布的完整类。"""

    # --- 图片预处理模块 ---
    def _get_remote_image_as_temp_file(self, title):
        """根据文章标题搜索、下载并返回一个临时图片文件路径。"""
        pexels_api_key = os.getenv('PEXELS_API_KEY')
        keywords = self._get_keywords_from_text(title)

        image_url = None
        if pexels_api_key:
            try:
                api = API(pexels_api_key)
                api.search(keywords, page=1, results_per_page=1)
                photos = api.get_entries()
                if photos:
                    image_url = photos[0].original
                    logging.info(f"通过 Pexels API 为关键词 '{keywords}' 找到图片: {image_url}", extra={'account_name': self.account_name})
            except Exception as e:
                logging.error(f"使用 Pexels API 搜索图片时出错: {e}", extra={'account_name': self.account_name})
        
        # 如果 Pexels 失败或不可用，回退到 Unsplash
        if not image_url:
            logging.info("Pexels 未找到图片或API密钥无效，尝试使用 Unsplash。", extra={'account_name': self.account_name})
            image_url = self._get_image_from_keyword(keywords)

        if image_url:
            try:
                response = requests.get(image_url, stream=True, timeout=20)
                if response.status_code == 200:
                    # 创建一个带正确扩展名的临时文件
                    ext = '.jpg'  # 默认为 jpg
                    content_type = response.headers.get('content-type')
                    if content_type and 'jpeg' in content_type:
                        ext = '.jpg'
                    elif content_type and 'png' in content_type:
                        ext = '.png'
                    
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                    for chunk in response.iter_content(1024):
                        temp_file.write(chunk)
                    temp_file.close()
                    logging.info(f"图片已成功下载到临时文件: {temp_file.name}", extra={'account_name': self.account_name})
                    return temp_file.name
            except requests.RequestException as e:
                logging.error(f"下载图片 {image_url} 时出错: {e}", extra={'account_name': self.account_name})
        
        return None

    def _get_image_from_keyword(self, keyword):
        """根据关键词从Unsplash获取一张随机图片URL。"""
        if not keyword:
            keyword = 'technology'  # 默认关键词
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://source.unsplash.com/800x600/?{encoded_keyword}"
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                logging.info(f"为关键词 '{keyword}' 找到了图片: {response.url}", extra={'account_name': self.account_name})
                return response.url
        except requests.RequestException as e:
            logging.error(f"通过关键词 '{keyword}' 获取图片时出错: {e}", extra={'account_name': self.account_name})
        return None

    def _check_image_url_valid(self, url):
        """检查给定的图片URL是否有效。"""
        # 本地文件路径不通过requests检查
        if not url.startswith(('http://', 'https://')):
            # 假设非http/https的都是本地路径或data URI，暂不检查有效性
            return True
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            # 检查状态码和内容类型
            if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
                return True
            logging.warning(f"链接 {url} 返回状态码 {response.status_code} 或内容类型不匹配。", extra={'account_name': self.account_name})
            return False
        except requests.RequestException as e:
            logging.warning(f"检查链接 {url} 时发生网络错误: {e}", extra={'account_name': self.account_name})
            return False

    def _get_keywords_from_text(self, text):
        """从文本中提取一两个关键词。"""
        words = re.split(r'\s+|[\uff0c\u3002\uff1a\uff1b\uff1f\uff01\u201c\u201d\u300a\u300b]', text)
        words = [w for w in words if len(w) > 1 and not w.isdigit()]  # 过滤掉单个字符和纯数字
        if not words:
            return "article"
        return ','.join(sorted(words, key=len, reverse=True)[:2])

    def _preprocess_markdown_images(self, md_content, file_path):
        """在处理前，检查并修复Markdown中的图片。"""
        logging.info("开始对Markdown内容进行图片预处理...", extra={'account_name': self.account_name})
        original_content = md_content
        image_regex = re.compile(r'!\[(.*?)\]\((.*?)\)')
        images = image_regex.findall(md_content)

        if not images:
            logging.warning("未找到图片，将根据标题添加一张封面图。", extra={'account_name': self.account_name})
            # 尝试从YAML元数据中获取标题
            try:
                _, meta_part = md_content.split('---', 2)[1:3]
                meta = yaml.safe_load(meta_part)
                title = meta.get('title', '')
            except (ValueError, yaml.YAMLError):
                title = ''
            
            if not title:
                title_match = re.search(r'^#\s*(.*)', md_content, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else os.path.splitext(os.path.basename(file_path))[0]
            
            keywords = self._get_keywords_from_text(title)
            new_image_url = self._get_image_from_keyword(keywords)
            if new_image_url:
                image_md = f"\n![{title}]({new_image_url})\n"
                # 插入到标题下方
                if re.search(r'^#\s*.*', md_content, re.MULTILINE):
                     md_content = re.sub(r'(^#\s*.*(?:\n|\r\n))', f'\g<1>{image_md}', md_content, count=1)
                else: # 如果没有H1标题，就加在文件最前面
                     md_content = image_md + md_content
                logging.info(f"成功为文章 '{title}' 添加了封面图片。", extra={'account_name': self.account_name})
        else:
            logging.info(f"找到 {len(images)} 张图片，开始检查链接有效性...", extra={'account_name': self.account_name})
            for alt_text, url in images:
                if not self._check_image_url_valid(url):
                    logging.warning(f"发现无效链接: {url}", extra={'account_name': self.account_name})
                    keywords = self._get_keywords_from_text(alt_text or os.path.splitext(os.path.basename(file_path))[0])
                    new_url = self._get_image_from_keyword(keywords)
                    if new_url:
                        old_image_md = f"![{alt_text}]({url})"
                        new_image_md = f"![{alt_text}]({new_url})"
                        md_content = md_content.replace(old_image_md, new_image_md, 1)
                        logging.info(f"成功将失效链接替换为: {new_url}", extra={'account_name': self.account_name})
                else:
                    logging.info(f"链接有效: {url}", extra={'account_name': self.account_name})

        if md_content != original_content:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                logging.info(f"Markdown文件已成功更新: {os.path.basename(file_path)}", extra={'account_name': self.account_name})
            except Exception as e:
                logging.error(f"写回更新后的Markdown文件失败: {e}", extra={'account_name': self.account_name})
        
        return md_content
    def __init__(self, account_name, app_id, app_secret, default_author=''):
        self.account_name = account_name
        self.app_id = app_id
        self.app_secret = app_secret
        self.default_author = default_author
        self.access_token = None
        self.token_expires_at = 0
        self.session = requests.Session()
        # FIX: 启用一组丰富的Markdown扩展，确保图片、表格等都能被正确解析
        self.markdown_converter = Markdown(extensions=[
            'meta',          # 支持YAML元数据
            'extra',         # 包含表格、围栏代码块、缩写等
            'sane_lists',    # 优化列表行为
            'tables',        # 显式启用表格
            'fenced_code'    # 显式启用围栏代码块
        ])
        # END FIX:
        self.current_processing_file = None

    def process_document(self, file_path):
        """处理单个Markdown文档的完整流程。"""
        self.current_processing_file = file_path
        local_image_paths = [] # 确保在finally中可访问
        try:
            logging.info(f"开始处理文档: {os.path.basename(file_path)}", extra={'account_name': self.account_name})
            md_content = self._read_file(file_path)
            if not md_content:
                return

            # =================================================================
            # 1. 图片预处理：检查、修复并回写Markdown文件
            # =================================================================
            md_content = self._preprocess_markdown_images(md_content, file_path)

            # FIX: 使用正则表达式精确移除列表标记，同时保留加粗的 `**`
            if md_content:
                # FIX: 移除列表标记的同时，在行尾添加换行符，确保每个列表项都成为独立段落
                md_content = re.sub(r'^\*\s(.*)', r'\1\n', md_content, flags=re.MULTILINE)
            # END FIX

            self.markdown_converter.reset()
            html_body = self.markdown_converter.convert(md_content)
            metadata = self.markdown_converter.Meta
            
            title, author, digest = self._extract_metadata_and_title(metadata, html_body, file_path)

            html_after_images, local_image_paths = self._upload_and_replace_images(html_body, os.path.dirname(file_path))

            thumb_media_id = self._upload_cover_image(metadata, local_image_paths, title)

            if not thumb_media_id:
                logging.warning(f"因缺少有效封面图，文章 '{title}' 将不会被创建为草稿。", extra={'account_name': self.account_name})
                return

            final_html = self._wrap_html_with_style(html_after_images, title)
            self.create_draft(title, final_html, thumb_media_id, author, digest)

        except Exception as e:
            logging.error(f"处理文档 '{os.path.basename(file_path)}' 时发生严重错误: {e}", exc_info=True, extra={'account_name': self.account_name})
        finally:
            # FIX: 统一在此处清理所有临时文件
            for path, is_temp in local_image_paths:
                if is_temp and os.path.exists(path):
                    try:
                        os.unlink(path)
                    except OSError as e:
                        logging.error(f"清理临时文件失败: {path}, {e}", extra={'account_name': self.account_name})
            self.current_processing_file = None

    def _read_file(self, file_path):
        """读取文件内容。"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logging.error(f"文件未找到: {file_path}", extra={'account_name': self.account_name})
            return None

    def _extract_metadata_and_title(self, metadata, html_body, file_path):
        title = metadata.get('title', [''])[0]
        author = metadata.get('author', [self.default_author])[0]
        digest = metadata.get('digest', [''])[0]

        if not title:
            soup = BeautifulSoup(html_body, 'html.parser')
            h1 = soup.find('h1')
            if h1: title = h1.text.strip()
        if not title:
            title = os.path.splitext(os.path.basename(file_path))[0]
        return title, author, digest

    # FIX:
    # FIX:
    # FIX:
    def _upload_and_replace_images(self, html_body, base_path):
        soup = BeautifulSoup(html_body, 'html.parser')
        images = soup.find_all('img')
        local_image_paths = []
        for img in images:
            # FIX: 优先获取 data-src, 兼容微信公众号的懒加载图片
            src = img.get('data-src') or img.get('src')
            # END FIX
            if not src:
                continue

            local_path, is_temp = self._get_local_image_path(src, base_path)
            
            # 核心修复：只要本地路径有效且文件存在，就将其加入候选列表
            if local_path and os.path.exists(local_path):
                local_image_paths.append((local_path, is_temp))
                # 接下来，尝试上传并替换URL，但这步的成败不影响它成为封面候选
                try:
                    wechat_url = self.upload_inline_image(local_path)
                    if wechat_url:
                        img['src'] = wechat_url
                    else:
                        logging.warning(f"上传内联图片后未能获取微信URL: {local_path}", extra={'account_name': self.account_name})
                except Exception as e:
                    logging.error(f"上传内联图片时发生异常: {local_path}, {e}", exc_info=True, extra={'account_name': self.account_name})
            elif not is_temp: # 如果是本地文件路径但文件不存在
                 logging.warning(f"在HTML中引用的本地图片不存在: {src}", extra={'account_name': self.account_name})

        logging.info(f"[_upload_and_replace_images] 最终生成的图片路径列表: {local_image_paths}", extra={'account_name': self.account_name})
        return str(soup), local_image_paths
    # END FIX:
    # END FIX:
    # END FIX:

    # FIX:
    # FIX:
    def _upload_cover_image(self, metadata, local_image_paths, title):
        """
        上传封面图片。
        优先使用元数据中指定的封面，其次是文章中的第一张图，最后自动从网络搜索。
        """
        logging.info(f"[_upload_cover_image] 接收到的图片列表: {local_image_paths}", extra={'account_name': self.account_name})
        cover_image_path = None
        temp_image_to_clean = None

        # 1. 检查元数据中的 'cover' 字段
        cover_url = metadata.get('cover')
        if cover_url:
            # 元数据中的cover现在应该是一个字符串
            cover_url_str = cover_url[0] if isinstance(cover_url, list) and cover_url else str(cover_url)
            logging.info(f"在元数据中找到封面链接: {cover_url_str}", extra={'account_name': self.account_name})
            if cover_url_str.startswith(('http://', 'https://')):
                # 如果是URL，下载为临时文件
                temp_image_to_clean = self._get_remote_image_as_temp_file(title) # 复用下载逻辑
                cover_image_path = temp_image_to_clean
            else: # 假定是本地相对路径
                # 使用 self.current_processing_file 获取当前处理文件的目录
                base_path = os.path.dirname(self.current_processing_file)
                cover_image_path = os.path.join(base_path, cover_url_str)

        # 2. 如果没有指定封面，使用文章中的第一张本地图片
        if not cover_image_path and local_image_paths:
            logging.info("未在元数据中指定封面，将使用文章中的第一张图片。", extra={'account_name': self.account_name})
            # local_image_paths 是 (path, is_temp) 的元组列表
            cover_image_path = local_image_paths[0][0]

        # 3. 如果仍然没有图片，从网络搜索
        if not cover_image_path or not os.path.exists(cover_image_path):
            logging.warning("未找到有效本地图片，将根据标题搜索一张网络图片作为封面。", extra={'account_name': self.account_name})
            temp_image_to_clean = self._get_remote_image_as_temp_file(title)
            cover_image_path = temp_image_to_clean

        if cover_image_path and os.path.exists(cover_image_path):
            try:
                thumb_media_id = self.upload_temporary_thumb(cover_image_path)
                if thumb_media_id:
                    logging.info(f"封面图片上传成功，Media ID: {thumb_media_id}", extra={'account_name': self.account_name})
                    return thumb_media_id
            finally:
                # 如果创建了临时文件，在这里清理它
                if temp_image_to_clean and os.path.exists(temp_image_to_clean):
                    os.remove(temp_image_to_clean)
                    logging.info(f"已清理临时封面文件: {temp_image_to_clean}", extra={'account_name': self.account_name})
        
        logging.warning("未能找到或上传有效的封面图片。", extra={'account_name': self.account_name})
        return None

        logging.warning("未能找到或上传有效的封面图片。", extra={'account_name': self.account_name})
        return None
    # END FIX:
    # END FIX:

    def _wrap_html_with_style(self, html_body, title):
        css_path = os.path.join(os.path.dirname(__file__), 'style.css')
        try:
            with open(css_path, 'r', encoding='utf-8') as f: css_content = f.read()
            full_html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title><style>{css_content}</style></head><body><article class="markdown-body">{html_body}</article></body></html>'
            premailer_instance = Premailer(full_html, remove_classes=True)
            return premailer_instance.transform()
        except FileNotFoundError:
            logging.warning(f"style.css 未找到，将不应用内联样式。", extra={'account_name': self.account_name})
            return f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title></head><body><article>{html_body}</article></body></html>'

    def _get_local_image_path(self, src, base_path):
        logging.info(f"[_get_local_image_path] 正在处理图片 src: {src}", extra={'account_name': self.account_name})
        if src.startswith(('http://', 'https')):
            try:
                # FIX: 添加 verify=False 解决SSL证书问题，并增强日志
                response = self.session.get(src, stream=True, timeout=10, verify=False)
                response.raise_for_status()
                logging.info(f"[_get_local_image_path] 成功下载图片: {src}", extra={'account_name': self.account_name})
                
                import tempfile
                from urllib.parse import urlparse
                ext = os.path.splitext(urlparse(src).path)[1] or '.jpg'
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                temp_file.close()
                with open(temp_file.name, 'wb') as f:
                    for chunk in response.iter_content(8192): f.write(chunk)
                
                logging.info(f"[_get_local_image_path] 临时文件已创建: {temp_file.name}", extra={'account_name': self.account_name})
                return temp_file.name, True
            except requests.exceptions.RequestException as e:
                logging.error(f"[_get_local_image_path] 下载网络图片失败: {src}, 错误: {e}", exc_info=True, extra={'account_name': self.account_name})
                return None, False
            # END FIX:
        else:
            abs_path = os.path.abspath(os.path.join(base_path, *src.split('/')))
            if os.path.exists(abs_path):
                return abs_path, False
            else:
                logging.warning(f"本地图片文件不存在: {abs_path}", extra={'account_name': self.account_name})
                return None, False

    def get_access_token(self):
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "access_token" in data:
                self.access_token = data['access_token']
                self.token_expires_at = time.time() + data.get('expires_in', 7200) - 600
                logging.info(f"成功获取 access_token", extra={'account_name': self.account_name})
                return True
            else:
                logging.error(f"获取access_token失败: {data.get('errmsg', '未知错误')}", extra={'account_name': self.account_name})
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"请求access_token时出错: {e}", extra={'account_name': self.account_name})
            return False

    def ensure_token_valid(self):
        if not self.access_token or time.time() >= self.token_expires_at:
            if not self.get_access_token():
                raise Exception("无法获取或刷新 access_token")

    def _upload_media(self, image_path, url, return_key, media_type=None):
        self.ensure_token_valid()
        params = {'access_token': self.access_token}
        if media_type:
            params['type'] = media_type

        try:
            with open(image_path, 'rb') as f:
                files = {'media': (os.path.basename(image_path), f)}
                response = self.session.post(url, files=files, params=params, timeout=30)
                logging.info(f"[_upload_media] API 响应状态码: {response.status_code} for {image_path}", extra={'account_name': self.account_name})
                data = response.json()
                logging.info(f"[_upload_media] API 响应内容: {data}", extra={'account_name': self.account_name})
                response.raise_for_status()
                
                if 'errcode' in data and data['errcode'] != 0:
                    logging.error(f"微信API错误: {data}", extra={'account_name': self.account_name})
                    return None
                if return_key in data:
                    logging.info(f"[_upload_media] 成功从响应中提取到 '{return_key}'.", extra={'account_name': self.account_name})
                    return data[return_key]
                else:
                    logging.error(f"API响应中缺少键 '{return_key}': {data}", extra={'account_name': self.account_name})
                    return None
        except FileNotFoundError:
            logging.error(f"上传媒体失败：文件未找到: {image_path}", extra={'account_name': self.account_name})
            return None
        except PermissionError:
            logging.error(f"上传媒体失败：文件权限错误，可能被占用: {image_path}", extra={'account_name': self.account_name})
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"上传媒体文件时发生网络错误: {e}", extra={'account_name': self.account_name})
            return None

    def _compress_image_if_needed(self, image_path, max_size_kb):
        try:
            if os.path.getsize(image_path) <= max_size_kb * 1024: return image_path, False
            import tempfile
            img = Image.open(image_path).convert('RGB')
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'jpeg', quality=85, optimize=True)
            logging.info(f"图片 {os.path.basename(image_path)} 已压缩至 {os.path.getsize(temp_file.name) / 1024:.2f}KB", extra={'account_name': self.account_name})
            return temp_file.name, True
        except Exception as e:
            logging.error(f"压缩图片时出错: {e}", extra={'account_name': self.account_name})
            return image_path, False

    def upload_inline_image(self, image_path):
        url = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
        return self._upload_media(image_path, url, return_key='url')

    def upload_temporary_thumb(self, image_path):
        compressed_path, is_temp = self._compress_image_if_needed(image_path, max_size_kb=2048)
        try:
            url = "https://api.weixin.qq.com/cgi-bin/material/add_material"
            return self._upload_media(compressed_path, url, return_key='media_id', media_type='thumb')
        finally:
            if is_temp and os.path.exists(compressed_path):
                try: os.unlink(compressed_path)
                except OSError as e: logging.error(f"清理压缩临时文件失败: {e}", extra={'account_name': self.account_name})

    def create_draft(self, title, content, thumb_media_id, author, digest):
        self.ensure_token_valid()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
        article = {
            'title': title[:64], 'author': author[:8], 'digest': digest[:120], 'content': content,
            'content_source_url': '', 'thumb_media_id': thumb_media_id,
            'need_open_comment': 1, 'only_fans_can_comment': 0
        }
        data = {'articles': [article]}
        try:
            response = self.session.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), timeout=30)
            response.raise_for_status()
            result = response.json()
            if 'media_id' in result:
                logging.info(f"成功创建草稿 '{title}', media_id: {result['media_id']}", extra={'account_name': self.account_name})
                return result['media_id']
            else:
                raise Exception(f"创建草稿失败: {result}")
        except Exception as e:
            logging.error(f"创建草稿时发生严重错误: {e}", exc_info=True, extra={'account_name': self.account_name})
            return None

# --- 4. 文件监控 ---
class DocumentWatcher(FileSystemEventHandler):
    """监控文档变化，并将处理任务提交到线程池，包含文件锁去重逻辑。"""
    def __init__(self, publishers, watch_dir, executor):
        self.publishers = publishers
        self.watch_dir = os.path.abspath(watch_dir)
        self.executor = executor
        self.processing_files = set()

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.markdown')):
            self._handle_event(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.markdown')):
            self._handle_event(event.src_path)

    def _handle_event(self, file_path):
        if file_path in self.processing_files:
            logging.info(f"文件 {os.path.basename(file_path)} 正在处理中，跳过重复事件。", extra={'account_name': 'System'})
            return

        try:
            self.processing_files.add(file_path)

            relative_path = os.path.relpath(file_path, self.watch_dir)
            account_name = relative_path.split(os.sep)[0]

            if account_name not in self.publishers:
                logging.warning(f"文件 {file_path} 所属账户 '{account_name}' 未配置，已忽略。", extra={'account_name': 'System'})
                return

            publisher = self.publishers[account_name]
            logging.info(f"检测到公众号 '{account_name}' 的文件变更: {os.path.basename(file_path)}，已提交到后台处理...", extra={'account_name': 'System'})
            # 将耗时任务提交到线程池，并添加一个完成回调来移除文件锁
            future = self.executor.submit(publisher.process_document, file_path)
            future.add_done_callback(lambda f: self.task_done(file_path, f))

        except (IndexError, ValueError):
            logging.warning(f"文件 {file_path} 不在任何已知账户目录下，已忽略。", extra={'account_name': 'System'})
        except Exception as e:
            logging.error(f"提交文件 {file_path} 到处理队列时发生错误: {e}", exc_info=True, extra={'account_name': 'System'})
            # 如果提交失败，也需要解锁
            self.processing_files.remove(file_path)

    def task_done(self, file_path, future):
        """线程池任务完成时的回调函数。"""
        try:
            # 如果任务在执行期间抛出异常，在这里可以获取到
            future.result()
        except Exception as e:
            logging.error(f"后台处理文件 {os.path.basename(file_path)} 时发生严重错误: {e}", exc_info=True, extra={'account_name': 'System'})
        finally:
            # 无论成功还是失败，都从处理集合中移除文件，以便下次可以重新处理
            logging.info(f"文件 {os.path.basename(file_path)} 处理流程结束。", extra={'account_name': 'System'})
            if file_path in self.processing_files:
                self.processing_files.remove(file_path)

# --- 5. 程序入口 ---
def main():
    """主函数：加载配置，初始化并启动监控。"""
    config = load_config()
    if not config:
        return

    # 解析层级配置
    paths_config = config.get('paths', {})
    publish_config = config.get('publish', {})
    accounts_config = config.get('accounts', {})

    # 从环境变量或配置文件中获取监控目录，并进行替换
    watch_dir_template = paths_config.get('watch_dir', 'documents')
    # 手动替换 ${VAR} 格式的变量，以兼容 Windows
    import re
    match = re.match(r'\$\{(.+)\}', watch_dir_template)
    if match:
        var_name = match.group(1)
        var_value = os.getenv(var_name)
        if var_value:
            watch_dir = var_value
        else:
            logging.warning(f"在 .env 文件中未找到环境变量 '{var_name}'，将使用默认值。")
            watch_dir = 'documents' # Fallback
    else:
        watch_dir = watch_dir_template

    default_author = publish_config.get('default_author', '')

    publishers = {}
    # 遍历 accounts 字典
    for account_name, account_details in accounts_config.items():
        # 从环境变量构造并读取 AppID 和 AppSecret
        app_id = os.getenv(f'WECHAT_ACCOUNT_{account_name}_APP_ID')
        app_secret = os.getenv(f'WECHAT_ACCOUNT_{account_name}_APP_SECRET')

        if not app_id or not app_secret:
            logging.warning(f"公众号 '{account_name}' 缺少 AppID 或 AppSecret (在 .env 文件中检查 WECHAT_ACCOUNT_{account_name}_APP_ID/SECRET)，已跳过。", extra={'account_name': 'System'})
            continue
        
        # 获取作者，如果账户下没有定义，则使用全局默认作者
        author = account_details.get('author', default_author)
        publishers[account_name] = WeChatPublisher(account_name, app_id, app_secret, author)
        logging.info(f"成功初始化公众号: '{account_name}'", extra={'account_name': 'System'})

    if not publishers:
        logging.error("没有成功加载任何公众号配置，程序退出。", extra={'account_name': 'System'})
        return

    if not os.path.isdir(watch_dir):
        logging.error(f"监控目录 '{os.path.abspath(watch_dir)}' 不存在或不是一个目录。程序退出。", extra={'account_name': 'System'})
        return

    # 创建一个最大工作线程为3的线程池
    executor = ThreadPoolExecutor(max_workers=3)

    event_handler = DocumentWatcher(publishers, watch_dir, executor)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=True)
    observer.start()
    logging.info(f"开始监控目录: {os.path.abspath(watch_dir)} 下的所有子目录", extra={'account_name': 'System'})

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("收到退出信号，正在关闭监控和后台线程...", extra={'account_name': 'System'})
        observer.stop()
        executor.shutdown(wait=True) # 等待所有后台任务完成
        logging.info("监控和后台线程已安全关闭。", extra={'account_name': 'System'})
    observer.join()

if __name__ == '__main__':
    main()

if __name__ == "__main__":
    # 添加一个自定义的 Filter 来为日志注入 account_name
    class AccountLogFilter(logging.Filter):
        def filter(self, record):
            # 为日志记录提供一个默认值，以防它在 publisher 上下文之外被调用
            if not hasattr(record, 'account_name'):
                record.account_name = 'System'
            return True

    # 获取根 logger 并添加 filter
    root_logger = logging.getLogger()
    root_logger.addFilter(AccountLogFilter())

    main()
