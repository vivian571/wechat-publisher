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
            except SystemExit:
                logging.error("Pexels API 由于网络错误或其他问题导致内部调用 exit()，已阻止程序退出。", extra={'account_name': self.account_name})
            except Exception as e:
                logging.error(f"使用 Pexels API 搜索图片时出错: {e}", extra={'account_name': self.account_name})
        
        # 如果 Pexels 失败或不可用，回退到 Unsplash
        if not image_url:
            logging.info("Pexels 未找到图片或API密钥无效，尝试使用 Unsplash。", extra={'account_name': self.account_name})
            image_url = self._get_image_from_keyword(keywords)

        if image_url:
            try:
                # 使用直连 session 下载图片（避免代理问题）
                direct_session = requests.Session()
                direct_session.trust_env = False
                response = direct_session.get(image_url, stream=True, timeout=20)
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
        """根据关键词从多个图片源获取图片URL（Pexels优先，Unsplash备用）。"""
        if not keyword:
            keyword = 'technology'  # 默认关键词
        
        # 方法1：优先尝试使用 Pexels API
        pexels_url = self._get_pexels_image(keyword)
        if pexels_url:
            return pexels_url
        
        # 方法2：备用方案，使用 Unsplash 官方 API
        unsplash_url = self._get_unsplash_image(keyword)
        if unsplash_url:
            return unsplash_url
        
        logging.warning(f"所有图片源都未能为关键词 '{keyword}' 找到图片", extra={'account_name': self.account_name})
        return None
    
    def _get_pexels_image(self, keyword):
        """使用 Pexels API 搜索图片（使用直连，不通过代理）。"""
        api_key = os.getenv('PEXELS_API_KEY')
        if not api_key:
            logging.debug("未配置 PEXELS_API_KEY，跳过 Pexels API", extra={'account_name': self.account_name})
            return None
        
        try:
            # Pexels API: 搜索图片（使用直连 session，不通过代理）
            api_url = "https://api.pexels.com/v1/search"
            headers = {
                'Authorization': api_key,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            params = {
                'query': keyword,
                'per_page': 1,
                'orientation': 'landscape'
            }
            
            # 创建一个不使用代理的 session
            direct_session = requests.Session()
            direct_session.trust_env = False  # 不使用环境变量中的代理
            
            response = direct_session.get(api_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            if data.get('photos') and len(data['photos']) > 0:
                image_url = data['photos'][0]['src']['large']
                logging.info(f"通过 Pexels API 为关键词 '{keyword}' 找到图片: {image_url}", extra={'account_name': self.account_name})
                return image_url
            else:
                logging.warning(f"Pexels API 未找到关键词 '{keyword}' 的图片", extra={'account_name': self.account_name})
                return None
                
        except requests.RequestException as e:
            logging.error(f"Pexels API 请求失败: {e}", extra={'account_name': self.account_name})
            return None
        except (KeyError, IndexError, ValueError) as e:
            logging.error(f"解析 Pexels API 响应失败: {e}", extra={'account_name': self.account_name})
            return None
    
    def _get_unsplash_image(self, keyword):
        """使用 Unsplash 官方 API 获取图片。"""
        access_key = os.getenv('UNSPLASH_ACCESS_KEY')
        if not access_key:
            logging.debug("未配置 UNSPLASH_ACCESS_KEY，跳过 Unsplash API", extra={'account_name': self.account_name})
            return None
        
        try:
            # Unsplash API: 搜索图片
            api_url = "https://api.unsplash.com/search/photos"
            headers = {
                'Authorization': f'Client-ID {access_key}',
                'Accept-Version': 'v1'
            }
            params = {
                'query': keyword,
                'per_page': 1,
                'orientation': 'landscape'
            }
            
            response = self.image_session.get(api_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                image_url = data['results'][0]['urls']['regular']
                logging.info(f"通过 Unsplash API 为关键词 '{keyword}' 找到图片: {image_url}", extra={'account_name': self.account_name})
                return image_url
            else:
                logging.warning(f"Unsplash API 未找到关键词 '{keyword}' 的图片", extra={'account_name': self.account_name})
                return None
                
        except requests.RequestException as e:
            logging.error(f"Unsplash API 请求失败: {e}", extra={'account_name': self.account_name})
            return None
        except (KeyError, IndexError, ValueError) as e:
            logging.error(f"解析 Unsplash API 响应失败: {e}", extra={'account_name': self.account_name})
            return None


    def _check_image_url_valid(self, url):
        """检查给定的图片URL是否有效。"""
        # unsplash:// 协议需要被处理,返回False触发替换
        if url.startswith('unsplash://'):
            return False
        
        # 本地文件路径不通过requests检查
        if not url.startswith(('http://', 'https://')):
            # 假设非http/https的都是本地路径或data URI，暂不检查有效性
            return True
        try:
            response = self.image_session.head(url, timeout=5, allow_redirects=True)
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
        self.token_expires_at = None
        
        # 创建两个 session：一个用于微信 API（禁用代理），一个用于图片下载（使用代理）
        self.session = requests.Session()
        # 设置标准的 User-Agent，模拟浏览器访问
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # 禁用代理,确保微信API请求使用真实IP而非代理IP
        self.session.proxies = {'http': None, 'https': None}
        self.session.trust_env = False  # 忽略环境变量中的代理设置
        
        # 创建专门用于下载图片的 session（使用代理）
        self.image_session = requests.Session()
        self.image_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # 显式设置代理（优先使用环境变量，否则使用常见代理端口）
        proxy_url = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
        if not proxy_url:
            # 尝试常见的代理端口
            for port in [7890, 10809, 1080, 3067,3066]:
                try:
                    test_proxy = f'http://127.0.0.1:{port}'
                    test_response = requests.get('http://www.google.com', 
                                                proxies={'http': test_proxy, 'https': test_proxy}, 
                                                timeout=2)
                    if test_response.status_code == 200:
                        proxy_url = test_proxy
                        logging.info(f"自动检测到可用代理: {proxy_url}", extra={'account_name': self.account_name})
                        break
                except:
                    continue
        
        if proxy_url:
            self.image_session.proxies = {'http': proxy_url, 'https': proxy_url}
            logging.info(f"图片下载将使用代理: {proxy_url}", extra={'account_name': self.account_name})
        else:
            logging.warning("未检测到可用代理，图片下载将使用直连", extra={'account_name': self.account_name})
        # 为日志记录器添加一个特定于此实例的过滤器
        self.logger = logging.getLogger()
        self.log_extra = {'account_name': self.account_name}

        # 初始化已发布文章日志
        self.published_log_file = 'published_articles.log'
        self.published_articles = self._load_published_articles()

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

    def _load_published_articles(self):
        """加载已发布的文章列表。"""
        if not os.path.exists(self.published_log_file):
            return set()
        try:
            with open(self.published_log_file, 'r', encoding='utf-8') as f:
                return {line.strip() for line in f if line.strip()}
        except IOError as e:
            logging.error(f"读取已发布文章日志 '{self.published_log_file}' 时出错: {e}", extra=self.log_extra)
            return set()

    def _add_to_published_log(self, title):
        """将文章标题添加到已发布日志中。"""
        try:
            with open(self.published_log_file, 'a', encoding='utf-8') as f:
                f.write(title + '\n')
            self.published_articles.add(title)
            logging.info(f"文章 '{title}' 已添加到发布日志中。", extra=self.log_extra)
        except IOError as e:
            logging.error(f"写入已发布文章日志 '{self.published_log_file}' 时出错: {e}", extra=self.log_extra)

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

            # 检查文章是否已经发布过
            if title in self.published_articles:
                logging.info(f"文章 '{title}' 已经发布过，本次将跳过。", extra=self.log_extra)
                return
            logging.info(f"[DEBUG] 文章未发布过，继续处理: {title}", extra={'account_name': self.account_name})

            html_after_images, local_image_paths = self._upload_and_replace_images(html_body, os.path.dirname(file_path))
            
            # =================================================================
            # 微信公众号列表修复：将 HTML 列表转换为普通段落
            # =================================================================
            html_after_images = self._convert_lists_to_paragraphs(html_after_images)

            thumb_media_id = self._upload_cover_image(metadata, local_image_paths, title)
            logging.info(f"[DEBUG] 封面图片media_id: {thumb_media_id}", extra={'account_name': self.account_name})

            if not thumb_media_id:
                logging.error(f"⚠️  封面图片上传失败！", extra={'account_name': self.account_name})
                logging.error(f"⚠️  可能原因：", extra={'account_name': self.account_name})
                logging.error(f"   1. IP白名单配置问题（最常见）", extra={'account_name': self.account_name})
                logging.error(f"   2. access_token 获取失败", extra={'account_name': self.account_name})
                logging.error(f"   3. 网络连接问题", extra={'account_name': self.account_name})
                logging.error(f"⚠️  文章 '{title}' 无法创建为草稿（微信要求必须有封面）", extra={'account_name': self.account_name})
                logging.error(f"⚠️  建议：修复 IP 白名单问题后重新运行", extra={'account_name': self.account_name})
                return

            logging.info(f"[DEBUG] 即将调用 _wrap_html_with_style", extra={'account_name': self.account_name})
            final_html = self._wrap_html_with_style(html_after_images, title)
            logging.info(f"[DEBUG] _wrap_html_with_style 返回内容长度: {len(final_html)}", extra={'account_name': self.account_name})
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

    def _convert_lists_to_paragraphs(self, html_content):
        """
        将 HTML 列表（ol/ul）转换为微信公众号友好的段落格式。
        
        微信公众号编辑器对 HTML 列表支持很差，会导致：
        - 有序列表序号和内容分开显示
        - 无序列表出现空白圆点
        
        解决方案：将列表项转换为普通段落，保留序号/符号
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 处理有序列表 <ol>
        for ol in soup.find_all('ol'):
            items = ol.find_all('li', recursive=False)
            new_elements = []
            for i, li in enumerate(items, 1):
                # 创建一个新的 <p> 标签，内容为 "序号. 内容"
                p = soup.new_tag('p')
                # 获取 li 的内容（保留内部 HTML）
                li_content = ''.join(str(child) for child in li.children)
                p.append(BeautifulSoup(f"<strong>{i}.</strong> {li_content}", 'html.parser'))
                new_elements.append(p)
            
            # 用新的段落替换 ol
            for elem in new_elements:
                ol.insert_before(elem)
            ol.decompose()
        
        # 处理无序列表 <ul>
        for ul in soup.find_all('ul'):
            items = ul.find_all('li', recursive=False)
            new_elements = []
            for li in items:
                p = soup.new_tag('p')
                li_content = ''.join(str(child) for child in li.children)
                # 使用实心圆点符号
                p.append(BeautifulSoup(f"● {li_content}", 'html.parser'))
                new_elements.append(p)
            
            for elem in new_elements:
                ul.insert_before(elem)
            ul.decompose()
        
        return str(soup)

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
        upload_success_count = 0
        
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
                        upload_success_count += 1
                        logging.info(f"✓ 成功上传内联图片到微信服务器: {os.path.basename(local_path)}", extra={'account_name': self.account_name})
                    else:
                        logging.warning(f"✗ 上传内联图片失败，将保留原始路径: {local_path}", extra={'account_name': self.account_name})
                except Exception as e:
                    # 降级处理：上传失败不影响草稿保存
                    logging.warning(f"✗ 上传内联图片时发生异常（将继续处理）: {os.path.basename(local_path)}, {e}", extra={'account_name': self.account_name})
            elif not is_temp: # 如果是本地文件路径但文件不存在
                 logging.warning(f"在HTML中引用的本地图片不存在: {src}", extra={'account_name': self.account_name})

        logging.info(f"[_upload_and_replace_images] 图片处理完成: 共 {len(local_image_paths)} 张，成功上传 {upload_success_count} 张", extra={'account_name': self.account_name})
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
        如果上传失败，返回 None 但不阻止草稿创建。
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
                    logging.info(f"✓ 封面图片上传成功，Media ID: {thumb_media_id}", extra={'account_name': self.account_name})
                    return thumb_media_id
                else:
                    logging.warning(f"✗ 封面图片上传失败，但已保存本地路径: {cover_image_path}", extra={'account_name': self.account_name})
                    return None
            except Exception as e:
                logging.error(f"✗ 上传封面图片时发生异常: {e}", extra={'account_name': self.account_name})
                return None
            finally:
                # 如果创建了临时文件，在这里清理它
                if temp_image_to_clean and os.path.exists(temp_image_to_clean):
                    os.remove(temp_image_to_clean)
                    logging.info(f"已清理临时封面文件: {temp_image_to_clean}", extra={'account_name': self.account_name})
        
        logging.warning("未能找到或上传有效的封面图片。", extra={'account_name': self.account_name})
        return None
    # END FIX:
    # END FIX:

    def _generate_md2_image(self, markdown_content, title):
        """
        使用本地md2服务生成公众号图片
        替代原有的md2 API调用（API密钥无效）
        """
        try:
            # 本地服务地址
            api_url = "http://localhost:8081/convert"
            
            payload = {
                "markdown": markdown_content,
                "theme": "default"
            }
            
            logging.info(f"正在调用本地md2服务生成图片...", extra={'account_name': self.account_name})
            response = self.image_session.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if result.get('code') == 200 and result.get('data', {}).get('image'):
                # 获取base64图片数据
                image_data = result['data']['image']
                
                # 解码base64数据
                if 'base64,' in image_data:
                    import base64
                    base64_content = image_data.split('base64,')[1]
                    image_bytes = base64.b64decode(base64_content)
                    
                    # 保存为临时文件
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                    temp_file.write(image_bytes)
                    temp_file.close()
                    
                    logging.info(f"✓ 本地md2图片生成成功: {temp_file.name}", extra={'account_name': self.account_name})
                    return temp_file.name
                else:
                    logging.error(f"图片数据格式错误", extra={'account_name': self.account_name})
                    return None
            else:
                logging.error(f"本地md2服务返回错误: {result}", extra={'account_name': self.account_name})
                return None
                
        except requests.exceptions.ConnectionError:
            logging.warning("本地md2服务未启动，将使用CSS样式", extra={'account_name': self.account_name})
            return None
        except Exception as e:
            logging.error(f"调用本地md2服务失败: {e}", extra={'account_name': self.account_name})
            return None

    def _wrap_html_with_style(self, html_body, title):
        """
        为 HTML 内容添加样式。
        优先使用md2生成的图片，其次使用账号专属样式，最后回退到默认样式
        """
        logging.info(f"[DEBUG] 开始_wrap_html_with_style，标题: {title}，内容长度: {len(html_body)}", extra={'account_name': self.account_name})
        # 首先尝试使用md2生成图片
        md2_image_url = self._generate_md2_image(html_body, title)
        logging.info(f"[DEBUG] md2生成结果: {md2_image_url}", extra={'account_name': self.account_name})
        if md2_image_url:
            try:
                # 本地服务直接返回文件路径，无需下载
                logging.info(f"✓ 本地md2图片处理成功: {md2_image_url}", extra={'account_name': self.account_name})
                
                # 读取图片文件并转换为base64
                with open(md2_image_url, 'rb') as img_file:
                    img_data = img_file.read()
                    base64_data = base64.b64encode(img_data).decode('utf-8')
                
                # 清理临时文件
                try:
                    os.unlink(md2_image_url)
                except:
                    pass
                
                # 返回包含md2图片的HTML
                img_html = f'<img src="data:image/png;base64,{base64_data}" alt="{title}" style="max-width:100%;height:auto;display:block;margin:0 auto;" />'
                return f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title></head><body>{img_html}</body></html>'
                
            except Exception as e:
                logging.warning(f"本地md2图片处理失败，将使用CSS样式: {e}", extra={'account_name': self.account_name})
        
        # 回退到原有的CSS样式处理
        base_dir = os.path.dirname(__file__)
        
        # 优先查找账号专属样式
        account_css_path = os.path.join(base_dir, 'styles', f'style_{self.account_name}.css')
        default_css_path = os.path.join(base_dir, 'style.css')
        
        css_path = account_css_path if os.path.exists(account_css_path) else default_css_path
        
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            if css_path == account_css_path:
                logging.info(f"✓ 使用账号专属样式: {os.path.basename(css_path)}", extra={'account_name': self.account_name})
            else:
                logging.info(f"使用默认样式: style.css", extra={'account_name': self.account_name})
            
            full_html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title><style>{css_content}</style></head><body><article class="markdown-body">{html_body}</article></body></html>'
            premailer_instance = Premailer(full_html, remove_classes=True)
            return premailer_instance.transform()
        except FileNotFoundError:
            logging.warning(f"样式文件未找到，将不应用内联样式。", extra={'account_name': self.account_name})
            return f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title></head><body><article>{html_body}</article></body></html>'

    def _get_local_image_path(self, src, base_path):
        logging.info(f"[_get_local_image_path] 正在处理图片 src: {src}", extra={'account_name': self.account_name})
        
        # 处理 unsplash:// 自定义协议
        if src.startswith('unsplash://'):
            keywords = src.replace('unsplash://', '').strip()
            logging.info(f"[_get_local_image_path] 检测到 Unsplash 协议,关键词: {keywords}", extra={'account_name': self.account_name})
            
            # 调用 Unsplash API 获取真实图片URL
            real_url = self._get_unsplash_image(keywords)
            if not real_url:
                # 如果 Unsplash 失败,尝试 Pexels
                real_url = self._get_pexels_image(keywords)
            
            if real_url:
                logging.info(f"[_get_local_image_path] 成功将 unsplash:// 转换为: {real_url}", extra={'account_name': self.account_name})
                src = real_url  # 替换为真实URL,继续下载流程
            else:
                logging.error(f"[_get_local_image_path] 无法为 unsplash:// 协议获取图片: {keywords}", extra={'account_name': self.account_name})
                return None, False
        
        if src.startswith(('http://', 'https')):
            # 增加重试机制
            max_retries = 3
            # 尝试列表：如果是海外图片源，先试代理；如果失败或没代理，试直连
            sessions_to_try = [self.image_session, self.session] 
            
            for session in sessions_to_try:
                for attempt in range(max_retries):
                    try:
                        # 增加超时时间，禁用 SSL 验证
                        response = session.get(src, stream=True, timeout=20, verify=False)
                        response.raise_for_status()
                        logging.info(f"[_get_local_image_path] 成功通过 {'代理' if session == self.image_session else '直连'} 下载图片: {src}", extra={'account_name': self.account_name})
                        
                        ext = '.jpg'
                        if 'image/png' in response.headers.get('Content-Type', ''): ext = '.png'
                        elif 'image/gif' in response.headers.get('Content-Type', ''): ext = '.gif'
                        
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                        temp_file.close()
                        with open(temp_file.name, 'wb') as f:
                            for chunk in response.iter_content(8192): f.write(chunk)
                        
                        return temp_file.name, True
                    except Exception as e:
                        if attempt < max_retries - 1:
                            logging.warning(f"[_get_local_image_path] 下载失败(尝试 {attempt+1}/{max_retries}), 切换/重试中: {e}", extra={'account_name': self.account_name})
                            time.sleep(1)
                        else:
                            logging.warning(f"[_get_local_image_path] 当前模式下载失败: {e}", extra={'account_name': self.account_name})
            
            logging.error(f"[_get_local_image_path] 所有下载模式均失败: {src}", extra={'account_name': self.account_name})
            return None, False
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
                error_msg = data.get('errmsg', '未知错误')
                error_code = data.get('errcode', 'N/A')
                logging.error(f"获取access_token失败: {error_msg} rid: {data.get('rid', 'N/A')}", extra={'account_name': self.account_name})
                logging.error(f"错误详情 - 错误码: {error_code}, 完整响应: {data}", extra={'account_name': self.account_name})
                
                # 如果是IP白名单问题,给出明确的解决建议
                if 'not in whitelist' in error_msg or error_code == 40164:
                    # 尝试从错误信息中提取IP地址
                    ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', error_msg)
                    detected_ip = ip_match.group(1) if ip_match else "未能自动提取"
                    
                    logging.error("\n" + "="*60, extra={'account_name': self.account_name})
                    logging.error(f"❌ 微信API拒绝了访问请求", extra={'account_name': self.account_name})
                    logging.error(f"原因: IP白名单限制 (错误码: {error_code})", extra={'account_name': self.account_name})
                    logging.error(f"您的当前公网IP: {detected_ip}", extra={'account_name': self.account_name})
                    logging.error(f"解决方案: 1.登录微信公众平台 2.进入[设置与开发]-[基本配置]-[IP白名单] 3.添加上述IP地址", extra={'account_name': self.account_name})
                    logging.error("="*60 + "\n", extra={'account_name': self.account_name})
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


    def _truncate_by_bytes(self, text, max_bytes, encoding='utf-8'):
        """
        按字节数截断字符串，确保不会在多字节字符中间截断。
        
        Args:
            text: 要截断的文本
            max_bytes: 最大字节数
            encoding: 编码方式，默认 utf-8
            
        Returns:
            截断后的字符串
        """
        if not text:
            return text
            
        encoded = text.encode(encoding)
        if len(encoded) <= max_bytes:
            return text
        
        # 如果需要截断，预留省略号的空间（不添加省略号，直接截断）
        # 微信公众号不需要省略号，直接截断即可
        truncated = text
        while len(truncated.encode(encoding)) > max_bytes:
            truncated = truncated[:-1]
        
        return truncated

    def create_draft(self, title, content, thumb_media_id, author, digest, need_original=False, auto_publish=False):
        """
        创建草稿。
        
        Args:
            title: 文章标题
            content: 文章内容
            thumb_media_id: 封面图片的 media_id
            author: 作者
            digest: 摘要
            need_original: 是否声明原创（默认 True）
            auto_publish: 是否自动发表（默认 True）
        """
        self.ensure_token_valid()
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
        
        # 微信公众号字段限制（按字符数，不是字节数）：
        # - 标题：最多 64 个字符
        # - 作者：最多 8 个字符
        # - 摘要：最多 120 个字符
        safe_title = title[:64] if title else ''
        safe_author = author[:8] if author else ''
        safe_digest = digest[:120] if digest else ''
        
        # 调试日志
        logging.info(f"[create_draft] 原标题: '{title}' ({len(title)} 字符)", extra={'account_name': self.account_name})
        logging.info(f"[create_draft] 截断后: '{safe_title}' ({len(safe_title)} 字符)", extra={'account_name': self.account_name})
        
        article = {
            'title': safe_title,
            'author': safe_author,
            'digest': safe_digest,
            'content': content,
            'content_source_url': '',
            'thumb_media_id': thumb_media_id,
            'need_open_comment': 1,
            'only_fans_can_comment': 0
        }
        data = {'articles': [article]}
        try:
            # 使用原来的方式：手动 JSON 编码，确保中文正确处理
            response = self.session.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), timeout=30)
            response.raise_for_status()
            result = response.json()
            if 'media_id' in result:
                media_id = result['media_id']
                logging.info(f"✓ 成功创建草稿 '{safe_title}', media_id: {media_id}", extra={'account_name': self.account_name})
                self._add_to_published_log(title)  # 记录已发布的文章
                
                # 如果需要自动发表
                if auto_publish:
                    publish_result = self.submit_for_freepublish(media_id, need_original=need_original)
                    if publish_result:
                        logging.info(f"✓ 文章 '{safe_title}' 已成功提交发布！", extra={'account_name': self.account_name})
                    else:
                        logging.warning(f"⚠️ 草稿创建成功，但自动发布失败。请手动发布。", extra={'account_name': self.account_name})
                
                return media_id
            else:
                raise Exception(f"创建草稿失败: {result}")
        except Exception as e:
            logging.error(f"创建草稿时发生严重错误: {e}", exc_info=True, extra={'account_name': self.account_name})
            return None

    def submit_for_freepublish(self, media_id, need_original=True):
        """
        提交草稿进行发布（群发）。
        
        Args:
            media_id: 草稿的 media_id
            need_original: 是否声明原创
            
        Returns:
            publish_id 或 None
        """
        self.ensure_token_valid()
        url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={self.access_token}"
        
        data = {'media_id': media_id}
        
        try:
            response = self.session.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if result.get('errcode', 0) == 0 and 'publish_id' in result:
                publish_id = result['publish_id']
                logging.info(f"✓ 成功提交发布，publish_id: {publish_id}", extra={'account_name': self.account_name})
                
                # 如果需要声明原创，调用原创声明接口
                if need_original:
                    self._declare_original(media_id)
                
                return publish_id
            else:
                logging.error(f"提交发布失败: {result}", extra={'account_name': self.account_name})
                return None
                
        except Exception as e:
            logging.error(f"提交发布时发生错误: {e}", exc_info=True, extra={'account_name': self.account_name})
            return None

    def _declare_original(self, media_id):
        """
        声明文章为原创。
        
        注意：微信公众号的原创声明需要在发布后进行，且账号需要有原创权限。
        如果账号没有原创权限，此操作会失败但不影响发布。
        """
        self.ensure_token_valid()
        
        try:
            # 获取发布状态
            url = f"https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token={self.access_token}"
            data = {'media_id': media_id}
            response = self.session.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'), timeout=30)
            result = response.json()
            
            if result.get('errcode', 0) == 0:
                logging.info(f"原创声明：已获取发布状态，等待审核...", extra={'account_name': self.account_name})
            else:
                logging.warning(f"获取发布状态失败（可能账号无原创权限）: {result}", extra={'account_name': self.account_name})
                
        except Exception as e:
            logging.warning(f"原创声明时发生错误（可能账号无原创权限）: {e}", extra={'account_name': self.account_name})

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
            logging.info(f"[DEBUG] 文件修改事件: {event.src_path}", extra={'account_name': 'System'})
            self._handle_event(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.md', '.markdown')):
            logging.info(f"[DEBUG] 文件创建事件: {event.src_path}", extra={'account_name': 'System'})
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
