import os
import time
import json
import requests
import re
from datetime import datetime, timedelta
from PIL import Image
from markdown import Markdown
from bs4 import BeautifulSoup
from premailer import Premailer
import urllib.parse
from typing import Optional, List, Tuple

from .base import BasePublisher

class WeChatPublisher(BasePublisher):
    """处理与微信公众号API交互、文档处理和发布的类。"""

    platform_name = 'wechat'

    def __init__(self, account_name: str, platform_config: dict, common_config: 'Config'):
        super().__init__(account_name, platform_config, common_config)
        self.app_id = self.platform_config.get('app_id')
        self.app_secret = self.platform_config.get('app_secret')
        if not self.app_id or not self.app_secret:
            raise ValueError(f"微信公众号 '{account_name}' 的配置缺少 'app_id' 或 'app_secret'")
        self.default_author = self.platform_config.get('author', '')
        self.access_token: Optional[str] = None
        self.token_expires_at: int = 0
        self.session = requests.Session()
        self.markdown_converter = Markdown(extensions=['meta', 'extra', 'sane_lists', 'tables', 'fenced_code'])

    def _get_access_token(self) -> Optional[str]:
        """获取或刷新微信公众号的access_token。"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            if 'access_token' in data:
                self.access_token = data['access_token']
                # 提前60秒过期，防止边缘情况
                self.token_expires_at = time.time() + data.get('expires_in', 7200) - 60
                self.log_info("成功获取 access_token。")
                return self.access_token
            else:
                self.log_error(f"获取 access_token 失败: {data.get('errmsg', '未知错误')}")
                return None
        except requests.RequestException as e:
            self.log_error(f"请求 access_token 时发生网络错误: {e}")
            return None

    def upload_image(self, image_path: str) -> Optional[str]:
        """上传本地图片到微信服务器，作为文章内容图片。"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image"
        try:
            with open(image_path, 'rb') as f:
                files = {'media': (os.path.basename(image_path), f)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                if 'url' in data:
                    self.log_success(f"图片上传成功: {os.path.basename(image_path)}")
                    return data['url']
                else:
                    self.log_error(f"上传图片失败: {data.get('errmsg', '未知错误')}")
                    return None
        except FileNotFoundError:
            self.log_error(f"图片文件未找到: {image_path}")
            return None
        except requests.RequestException as e:
            self.log_error(f"上传图片时发生网络错误: {e}")
            return None

    def _upload_thumb_image(self, image_path: str) -> Optional[str]:
        """上传图片作为封面图（临时素材），返回media_id。"""
        token = self._get_access_token()
        if not token:
            return None

        url = f"https://api.weixin.qq.com/cgi-bin/media/upload?access_token={token}&type=image"
        try:
            with open(image_path, 'rb') as f:
                files = {'media': (os.path.basename(image_path), f)}
                response = self.session.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                if 'media_id' in data:
                    self.log_success(f"封面图上传成功: {os.path.basename(image_path)}")
                    return data['media_id']
                else:
                    self.log_error(f"上传封面图失败: {data.get('errmsg', '未知错误')}")
                    return None
        except Exception as e:
            self.log_error(f"上传封面图时发生异常: {e}", exc_info=True)
            return None

    def publish(self, content_path: str, **kwargs) -> bool:
        """处理和发布单个Markdown文档的完整流程。"""
        self.log_info(f"开始处理文件: {os.path.basename(content_path)}")

        try:
            # 1. 读取和解析Markdown
            html_content, metadata = self.process_markdown(content_path)
            title = metadata.get('title', os.path.basename(content_path).split('.')[0])
            author = metadata.get('author', self.default_author)
            digest = metadata.get('digest', '')

            # 2. 处理HTML中的图片
            base_dir = os.path.dirname(content_path)
            html_content, local_images = self._process_html_images(html_content, base_dir)

            # 3. 上传封面图
            cover_image_path = metadata.get('cover')
            thumb_media_id = None
            if cover_image_path:
                full_cover_path = os.path.join(base_dir, cover_image_path)
                if os.path.exists(full_cover_path):
                    thumb_media_id = self._upload_thumb_image(full_cover_path)
                else:
                    self.log_warning(f"指定的封面图片不存在: {full_cover_path}")
            
            if not thumb_media_id and local_images:
                thumb_media_id = self._upload_thumb_image(local_images[0])

            if not thumb_media_id:
                self.log_warning("无法确定封面图，将不设置封面。")
                # 这里可以根据配置选择是否继续
                # return False

            # 4. 样式化和创建草稿
            final_html = self._wrap_html_with_style(html_content, title)
            draft_id = self._create_draft(title, final_html, thumb_media_id, author, digest)

            if draft_id:
                self.log_success(f"成功创建草稿: '{title}' (ID: {draft_id})")
                return True
            else:
                self.log_error(f"创建草稿失败: '{title}'")
                return False

        except Exception as e:
            self.log_error(f"处理文件时发生未知错误: {e}", exc_info=True)
            return False

    def _process_html_images(self, html: str, base_dir: str) -> Tuple[str, List[str]]:
        """处理HTML中的图片，上传本地图片并替换链接，返回处理后的HTML和本地图片列表。"""
        soup = BeautifulSoup(html, 'html.parser')
        local_image_paths = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src or src.startswith(('http://', 'https://', 'data:')):
                continue

            image_path = os.path.join(base_dir, src)
            if os.path.exists(image_path):
                local_image_paths.append(image_path)
                self.log_info(f"准备上传本地图片: {src}")
                wechat_url = self.upload_image(image_path)
                if wechat_url:
                    img['src'] = wechat_url
                else:
                    self.log_warning(f"上传图片失败，HTML中的引用将保持原样: {src}")
            else:
                self.log_warning(f"本地图片未找到，跳过: {image_path}")
        
        return str(soup), local_image_paths

    def _wrap_html_with_style(self, body_html: str, title: str) -> str:
        """将HTML内容包裹在带有基本样式的完整HTML结构中。"""
        # ... (样式代码保持不变，此处省略以节省空间)
        style = """
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"; margin: 0; padding: 20px; color: #333; line-height: 1.6; }
            .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.05); border-radius: 8px; }
            h1, h2, h3, h4, h5, h6 { color: #1a1a1a; margin-top: 1.5em; margin-bottom: 0.5em; }
            p { margin: 0 0 1em 0; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            img { max-width: 100%; height: auto; border-radius: 4px; margin: 10px 0; }
            pre { background: #f5f5f5; padding: 15px; border-radius: 4px; overflow-x: auto; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; }
            code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; background: #f5f5f5; padding: 2px 4px; border-radius: 3px; }
            blockquote { border-left: 4px solid #ccc; padding-left: 10px; color: #666; margin-left: 0; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
        """
        full_html = f"""<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"><title>{title}</title>{style}</head><body><div class=\"container\">{body_html}</div></body></html>"""
        
        # 使用premailer内联CSS
        try:
            inlined_html = Premailer(full_html).transform()
            return inlined_html
        except Exception as e:
            self.log_warning(f"CSS内联失败，将使用原始HTML: {e}")
            return full_html

    def _create_draft(self, title: str, content: str, thumb_media_id: str, author: str, digest: str) -> bool:
        """在微信公众号中创建一篇草稿。"""
        token = self._get_access_token()
        if not token:
            return False

        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
        article = {
            'title': title,
            'author': author,
            'digest': digest,
            'content': content,
            'content_source_url': '',
            'thumb_media_id': thumb_media_id,
            'need_open_comment': 1,
            'only_fans_can_comment': 0
        }
        payload = {'articles': [article]}
        try:
            response = self.session.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
            response.raise_for_status()
            data = response.json()
            if 'media_id' in data:
                self.log_success(f"草稿创建成功: '{title}' (Media ID: {data['media_id']})")
                return True
            else:
                self.log_error(f"创建草稿失败: {data.get('errmsg', '未知错误')}")
                return False
        except requests.RequestException as e:
            self.log_error(f"创建草稿时发生网络错误: {e}")
            return False
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
                        self.log_warning(f"上传内联图片后未能获取微信URL: {local_path}")
                except Exception as e:
                    self.log_error(f"上传内联图片时发生异常: {local_path}, {e}", exc_info=True)
            elif not is_temp: # 如果是本地文件路径但文件不存在
                 self.log_warning(f"在HTML中引用的本地图片不存在: {src}")

        self.log_info(f"[_upload_and_replace_images] 最终生成的图片路径列表: {local_image_paths}")
        return str(soup), local_image_paths
    # END FIX:
    # END FIX:
    # END FIX:

    # FIX:
    # FIX:
    def _upload_cover_image(self, metadata, local_image_paths):
        self.log_info(f"[_upload_cover_image] 接收到的图片列表: {local_image_paths}")
        cover_path_in_meta = metadata.get('cover', [''])[0]
        if cover_path_in_meta:
            self.log_info(f"检测到元数据中指定的封面: {cover_path_in_meta}")
            base_path = os.path.dirname(self.current_processing_file)
            local_path, is_temp = self._get_local_image_path(cover_path_in_meta, base_path)
            if local_path and os.path.exists(local_path):
                try:
                    thumb_id = self.upload_temporary_thumb(local_path)
                    if thumb_id: return thumb_id
                except Exception as e:
                    self.log_error(f"上传元数据中指定的封面图片失败: {e}")
        
        if local_image_paths:
            first_image_path, _ = local_image_paths[0]
            self.log_info(f"[_upload_cover_image] 尝试使用文章首图作为封面: {first_image_path}")
            
            path_exists = os.path.exists(first_image_path)
            self.log_info(f"[_upload_cover_image] 检查路径是否存在 '{first_image_path}': {path_exists}")

            if path_exists:
                try:
                    thumb_id = self.upload_temporary_thumb(first_image_path)
                    if thumb_id:
                        self.log_info(f"成功上传文章首图作为封面: {first_image_path}")
                        return thumb_id
                    else:
                        self.log_warning(f"[_upload_cover_image] 上传函数返回了空值 for {first_image_path}")
                except Exception as e:
                    self.log_error(f"上传文章首图作为封面时发生异常: {e}", exc_info=True)
            else:
                self.log_warning(f"[_upload_cover_image] 文章首图路径不存在，无法上传。")
        else:
            self.log_info("[_upload_cover_image] 没有可用的本地图片作为封面。")

        self.log_warning("未能找到或上传有效的封面图片。")
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
            self.log_warning(f"style.css 未找到，将不应用内联样式。")
            return f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title></head><body><article>{html_body}</article></body></html>'

    def _get_local_image_path(self, src, base_path):
        self.log_info(f"[_get_local_image_path] 正在处理图片 src: {src}")
        if src.startswith(('http://', 'https')):
            try:
                # FIX: 添加 verify=False 解决SSL证书问题，并增强日志
                response = self.session.get(src, stream=True, timeout=10, verify=False)
                response.raise_for_status()
                self.log_info(f"[_get_local_image_path] 成功下载图片: {src}")
                
                import tempfile
                from urllib.parse import urlparse
                ext = os.path.splitext(urlparse(src).path)[1] or '.jpg'
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                temp_file.close()
                with open(temp_file.name, 'wb') as f:
                    for chunk in response.iter_content(8192): f.write(chunk)
                
                self.log_info(f"[_get_local_image_path] 临时文件已创建: {temp_file.name}")
                return temp_file.name, True
            except requests.exceptions.RequestException as e:
                self.log_error(f"[_get_local_image_path] 下载网络图片失败: {src}, 错误: {e}", exc_info=True)
                return None, False
            # END FIX:
        else:
            abs_path = os.path.abspath(os.path.join(base_path, *src.split('/')))
            if os.path.exists(abs_path):
                return abs_path, False
            else:
                self.log_warning(f"本地图片文件不存在: {abs_path}")
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
                self.log_info(f"成功获取 access_token")
                return True
            else:
                self.log_error(f"获取access_token失败: {data.get('errmsg', '未知错误')}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_error(f"请求access_token时出错: {e}")
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
                self.log_info(f"[_upload_media] API 响应状态码: {response.status_code} for {image_path}")
                data = response.json()
                self.log_info(f"[_upload_media] API 响应内容: {data}")
                response.raise_for_status()
                
                if 'errcode' in data and data['errcode'] != 0:
                    self.log_error(f"微信API错误: {data}")
                    return None
                if return_key in data:
                    self.log_info(f"[_upload_media] 成功从响应中提取到 '{return_key}'.")
                    return data[return_key]
                else:
                    self.log_error(f"API响应中缺少键 '{return_key}': {data}")
                    return None
        except FileNotFoundError:
            self.log_error(f"上传媒体失败：文件未找到: {image_path}")
            return None
        except PermissionError:
            self.log_error(f"上传媒体失败：文件权限错误，可能被占用: {image_path}")
            return None
        except requests.exceptions.RequestException as e:
            self.log_error(f"上传媒体文件时发生网络错误: {e}")
            return None

    def _compress_image_if_needed(self, image_path, max_size_kb):
        try:
            if os.path.getsize(image_path) <= max_size_kb * 1024: return image_path, False
            import tempfile
            img = Image.open(image_path).convert('RGB')
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img.save(temp_file.name, 'jpeg', quality=85, optimize=True)
            self.log_info(f"图片 {os.path.basename(image_path)} 已压缩至 {os.path.getsize(temp_file.name) / 1024:.2f}KB")
            return temp_file.name, True
        except Exception as e:
            self.log_error(f"压缩图片时出错: {e}")
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
                except OSError as e: self.log_error(f"清理压缩临时文件失败: {e}")

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
                self.log_info(f"成功创建草稿 '{title}', media_id: {result['media_id']}")
                return result['media_id']
            else:
                raise Exception(f"创建草稿失败: {result}")
        except Exception as e:
            self.log_error(f"创建草稿时发生严重错误: {e}", exc_info=True)
            return None
