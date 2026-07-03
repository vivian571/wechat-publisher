#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeChat Official Account Auto-Posting Script
使用 DrissionPage 自动发布内容到微信公众号后台
"""

import os
import sys
import time
import argparse
import argparse
from pathlib import Path

# 不再使用全局 TextIOWrapper 以免引起缓冲区死锁
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions

# 封面处理相关
try:
    from PIL import Image
    from cover_fixer import fix_wechat_cover, ensure_cover_ratio
    COVER_FIXER_AVAILABLE = True
except ImportError:
    COVER_FIXER_AVAILABLE = False
    print("⚠️  cover_fixer 模块未安装，封面自动裁剪功能不可用")


class WeChatAutoPoster:
    """微信公众号自动发布器"""
    
    def __init__(self, account_name: str, headless: bool = False):
        """
        初始化发布器
        
        Args:
            account_name: 账号名称（如：Account_A_CrossBorder）
            headless: 是否使用无头模式
        """
        self.account_name = account_name
        self.base_dir = Path(__file__).parent
        self.account_dir = self.base_dir / "accounts" / account_name
        
        # 检查账号目录是否存在
        if not self.account_dir.exists():
            raise ValueError(f"账号目录不存在: {self.account_dir}")
        
        # 检查是否有自定义封面图片
        self.cover_image_path = self._find_cover_image()
        
        # 初始化浏览器
        self.page = self._init_browser(headless)
        
    def _find_cover_image(self) -> str:
        """
        查找账号目录下的封面图片
        支持的文件名：cover.jpg, cover.png, cover_fixed.jpg 等
        如果没有找到，则返回 None（后续可能会生成）
        """
        cover_patterns = ['cover_fixed.*', 'cover_generated.*', 'cover.*', 'Cover.*', '封面.*']
        
        for pattern in cover_patterns:
            matches = list(self.account_dir.glob(pattern))
            for match in matches:
                if match.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    print(f"📷 找到封面图片: {match.name}")
                    return str(match)
        
        print("⚠️ 未找到封面图片，将在发布时自动生成")
        return None
    
    def _generate_cover_image(self, title: str) -> str:
        """
        使用 AI 生成封面图片
        
        Args:
            title: 文章标题
            
        Returns:
            生成的图片路径，失败返回 None
        """
        try:
            from image_generator import generate_cover_for_article
            
            print("\n🎨 正在生成封面图片...")
            cover_path = generate_cover_for_article(title, str(self.account_dir))
            
            if cover_path:
                self.cover_image_path = cover_path
                return cover_path
        except ImportError:
            print("⚠️ 图片生成模块未安装")
        except Exception as e:
            print(f"⚠️ 图片生成失败: {e}")
        
        return None
    
    def _preprocess_cover_image(self, image_path: str) -> str:
        """
        预处理封面图片，确保符合微信 2.35:1 比例要求
        
        Args:
            image_path: 原始图片路径
            
        Returns:
            处理后的图片路径
        """
        if not COVER_FIXER_AVAILABLE:
            print("⚠️  封面处理模块不可用，跳过预处理")
            return image_path
        
        try:
            print(f"\n🖼️  正在预处理封面图片: {image_path}")
            result = ensure_cover_ratio(image_path)
            return result if result else image_path
        except Exception as e:
            print(f"❌ 封面预处理失败: {e}")
            return image_path

    def _init_browser(self, headless: bool) -> ChromiumPage:
        """初始化浏览器"""
        co = ChromiumOptions()
        
        # 每个账号使用独立的用户数据目录，避免登录状态混淆
        user_data_dir = self.base_dir / ".browser_data" / self.account_name
        user_data_dir.mkdir(parents=True, exist_ok=True)
        co.set_user_data_path(str(user_data_dir))
        
        # 设置无头模式
        if headless:
            co.headless()
        
        # 设置代理（从环境变量读取）
        proxy = os.environ.get('HTTP_PROXY') or os.environ.get('HTTPS_PROXY')
        if proxy:
            print(f"🌐 正在配置浏览器代理: {proxy}")
            co.set_proxy(proxy)
        
        # 设置窗口大小

        
        # 创建浏览器页面
        page = ChromiumPage(co)
        
        print(f"✅ 浏览器已启动")
        return page
    
    def check_login(self) -> bool:
        """
        检查是否已登录
        
        Returns:
            True if logged in, False otherwise
        """
        # 导航到微信公众号后台
        print(f"🌐 正在打开微信公众号后台...")
        self.page.get("https://mp.weixin.qq.com/")
        
        # 等待页面加载
        time.sleep(3)
        
        # 检查是否存在登录二维码或已经登录
        # 如果页面包含 "账号信息" 或 "素材管理" 等元素，说明已登录
        try:
            # 尝试查找左侧菜单栏（登录后才有）
            menu = self.page.ele("css:.weui-desktop-menu__list", timeout=2)
            if menu:
                print(f"✅ 检测到已登录状态")
                return True
        except:
            pass
        
        # 检查是否有二维码
        try:
            qr_code = self.page.ele("css:.login__qrcode__wrp", timeout=2)
            if qr_code:
                print(f"⚠️  未登录，需要扫码")
                return False
        except:
            pass
        
        # 如果都没找到，可能是页面还在加载，再等待一下
        time.sleep(2)
        
        # 再次检查
        try:
            menu = self.page.ele("css:.weui-desktop-menu__list", timeout=2)
            if menu:
                print(f"✅ 检测到已登录状态")
                return True
        except:
            print(f"⚠️  未检测到登录状态")
            return False
    
    def wait_for_login(self, timeout: int = 300):
        """
        等待用户扫码登录 (加强版：双重检测)
        """
        print(f"📱 请拿出手机扫描屏幕上的二维码...")
        print(f"⏳ 最大等待时间: {timeout}秒")

        start_time = time.time()

        while time.time() - start_time < timeout:
            # 每隔 5 秒截一张图，用于展示二维码
            if int(time.time() - start_time) % 5 == 0:
                self.page.get_screenshot(path=str(self.base_dir / "login_qr.png"), full_page=False)
                print(f"📸 登录页面已截图: login_qr.png")

            # === 方法1：最稳的 URL 检测 ===
            # 只要网址里包含 'cgi-bin/home'，说明绝对进去了
            if "cgi-bin/home" in self.page.url:
                print(f"✅ 检测到后台主页 URL，登录成功！")
                # 给一点时间让页面元素加载完
                time.sleep(3)
                if (self.base_dir / "login_qr.png").exists():
                    os.remove(self.base_dir / "login_qr.png")
                return True

            # === 方法2：元素检测 (辅助) ===
            try:
                # 尝试找一下头像或者菜单
                if self.page.ele(".weui-desktop-account__info", timeout=0.5):
                    print(f"✅ 检测到账号信息元素，登录成功！")
                    return True
            except:
                pass

            # 还没成功，稍微等一下再检查
            time.sleep(1)
            
            # 显示倒计时 (每10秒提醒一次)
            elapsed = int(time.time() - start_time)
            if elapsed % 10 == 0 and elapsed > 0:
                print(f"⏳ 正在等待扫码... (已过 {elapsed} 秒)")

        raise TimeoutError(f"登录超时 ({timeout}秒)，请检查网络或重新运行")
        

    
    def load_text_content(self) -> tuple[str, str]:
        """
        加载文本内容 (按优先级: .md -> .html -> .txt)
        
        Returns:
            (title, content_body): 标题、正文内容 (若失败返回 None, None)
        """
        # 优先级列表
        # 1. 直接搜索目录下的所有 .md 文件 (排除系统提示词文件)
        md_files = [f for f in self.account_dir.glob("*.md") if "system_prompt" not in f.name]
        # 2. 固定命名的文件
        html_file = self.account_dir / "output.html"
        text_file = self.account_dir / "output.txt"
        
        target_file = None
        is_md = False
        
        if md_files:
            # 取最新的一个 md 文件
            target_file = sorted(md_files, key=os.path.getmtime, reverse=True)[0]
            is_md = True
            print(f"📄 找到 Markdown 内容: {target_file.name}")
        elif html_file.exists():
            target_file = html_file
            print(f"📄 找到 HTML 内容: {html_file.name}")
        elif text_file.exists():
            target_file = text_file
            print(f"📄 找到 TXT 内容: {text_file.name}")
            
        if not target_file:
            print(f"⚠️  账号 {self.account_name} 目录下未找到有效内容文件，准备跳过。")
            return None, None

        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                raw_content = f.read()
            
            if not raw_content.strip():
                print(f"⚠️  文件内容为空: {target_file.name}")
                return None, None

            # 处理 Markdown / TXT 的标题提取逻辑
            if is_md or target_file.suffix == '.txt':
                lines = raw_content.strip().split('\n')
                # 尝试从第一行获取标题 (去掉可能的 # 号)
                title = lines[0].replace('#', '').strip() if lines else "未命名文章"
                # 正文是除第一行之外的内容
                text_body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else raw_content
                self.is_html_content = False
                print(f"✅ 提取标题: {title}")
                return title, text_body
            
            # 处理 HTML 逻辑
            else:
                import re
                title_match = re.search(r'<h1[^>]*>(.+?)</h1>', raw_content, re.IGNORECASE)
                title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else "未命名文章"
                self.is_html_content = True
                print(f"✅ 提取标题: {title}")
                return title, raw_content
                
        except Exception as e:
            print(f"❌ 读取文件 {target_file.name} 失败: {e}")
            return None, None
    
    
    def create_new_draft(self):
        """创建新的图文草稿"""
        print(f"📝 正在创建新草稿...")
        
        # 获取当前URL中的token
        from urllib.parse import parse_qs, urlparse
        query = urlparse(self.page.url).query
        token = parse_qs(query).get('token', [''])[0]
        
        if not token:
            print(f"⚠️  未找到token，尝试通过点击界面操作...")
            # 备用方案：尝试点击"新的创作" -> "图文" (根据用户截图优化)
            try:
                # 尝试点击首页的"图文"或"文章"图标
                # 截图显示"新的创作"下有"文章"和"图文"
                # 先找“文章”按钮 (publish_btn)
                new_creation_btn = self.page.ele("text:文章", timeout=3)
                if not new_creation_btn:
                     # 没找到文章，再找图文
                    new_creation_btn = self.page.ele("text:图文", timeout=3)
                
                if new_creation_btn:
                    new_creation_btn.click()
                    print(f"✅ 已点击新建文章按钮")
                    time.sleep(3)
                    # 切换到新标签页（如果有）
                    # 编辑器通常会在新标签页打开
                    if len(self.page.context.pages) > 1:
                         self.page = self.page.context.pages[-1]
                    return
            except Exception as e:
                print(f"⚠️  点击新建按钮失败: {e}")
        
        else:
            print(f"✅ 获取到 token: {token}")
            # 修改 type=10 (图文) 为文章发布的相关参数
            # "文章"发布的 createType 通常不同
            # 经过测试，直接点击按钮其实更稳妥，因为 createType 参数可能变动
            # 这里改为先尝试点击 "文章" 按钮（如果有 token 也可以拼接 URL，但不仅 createType 变了，type 也没变）
            
            # 尝试直接访问 "文章" 编辑器 URL
            # type=10 是标准的图文消息编辑器
            editor_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&createType=0&token={token}&lang=zh_CN"
            
            print(f"🔗 尝试访问文章编辑器: {editor_url}")
            self.page.get(editor_url)
            time.sleep(5) 

        
        print(f"✅ 已尝试打开编辑器页面")
    
    def fill_content(self, title_text: str, content_text: str):
        """
        填充内容到编辑器 (纯文本模式)
        """
        print(f"✍️  正在填充内容...")
        
        # 1. 填写标题
        try:
            # 尝试新版和旧版标题 ID
            title_ele = self.page.ele('#title', timeout=3) or self.page.ele('#js_appmsg_title', timeout=1)
            if title_ele:
                title_ele.clear()
                title_ele.input(title_text)
                print(f"✅ 标题写入成功: {title_text}")
                
                # 新增：填写作者
                time.sleep(1)
                author_input = self.page.ele('#author', timeout=2)
                if author_input:
                    author_input.clear()
                    author_input.input("AI呈序")
                    print("✅ 作者已填写: AI呈序")
            else:
                print("⚠️ 未找到标题输入框，请检查页面是否完全加载")
        except Exception as e:
            print(f"⚠️ 标题填写出错: {e}")

        # 2. 填写正文
        try:
            print("⚡️ 正在尝试定位正文区域...")
            
            # 优先匹配截图中的核心类名
            selectors = [
                '.mock-iframe-body',
                '.mock-iframe-document',
                '#js_editor_area',
                '[contenteditable="true"]'
            ]
            
            target_ele = None
            for selector in selectors:
                ele = self.page.ele(selector, timeout=1)
                # 排除掉标题框（标题通常也是 contenteditable）
                if ele and ele.attr('id') != 'title' and ele.attr('id') != 'js_appmsg_title':
                    target_ele = ele
                    print(f"✅ 找到正文区域，使用选择器: {selector}")
                    break
            
            if target_ele:
                # 聚焦
                target_ele.click()
                
                # 使用纯文本方式填充（唯一可靠的方式）
                print("📝 使用纯文本方式填充正文...")
                
                # 获取纯文本内容
                if getattr(self, 'is_html_content', False):
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(content_text, 'html.parser')
                    for tag in soup(["script", "style"]):
                        tag.decompose()
                    raw_text = soup.get_text(separator='\n', strip=True)
                else:
                    raw_text = content_text
                
                # 去除多余空行，保留单个换行
                lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
                clean_text = '\n'.join(lines)  # 单个换行，不是双换行
                
                # 去掉所有 Markdown 符号（#, *, **, 等）
                import re
                # 严格清理：去除所有 # 和 * 符号（包括文中和行首）
                clean_text = clean_text.replace('*', '')
                clean_text = clean_text.replace('#', '')
                
                # 不再使用 innerHTML 注入（会破坏编辑器状态导致图片无法插入）
                # 改用剪贴板粘贴方式
                import subprocess
                
                # 将纯文本内容复制到剪贴板
                # Windows 系统使用 clip 命令
                process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
                process.communicate(input=clean_text.encode('utf-16-le'))
                
                # 聚焦编辑器并粘贴
                target_ele.click()
                time.sleep(0.5)
                
                from DrissionPage.common import Keys
                self.page.actions.key_down(Keys.CTRL).key_down('v').key_up('v').key_up(Keys.CTRL)
                time.sleep(1)
                
                print(f"🎉 正文内容填充成功！（{len(lines)} 行，使用剪贴板粘贴方式）")
                
                # 通过编辑器工具栏在正文头部插入图片
                time.sleep(1)
                self._insert_image_via_toolbar(title_text)
                
                # === 处理封面、原创、创作来源 ===
                self._handle_additional_settings(title_text)
                
            else:
                print("❌ 无法定位正文区域。")
                
        except Exception as e:
            print(f"❌ 填充正文时发生异常: {e}")
            
        print(f"✅ 填充操作结束")

    def _insert_image_via_toolbar(self, title: str = ""):
        """通过编辑器工具栏在正文头部插入封面图片"""
        print("\n🖼️ 正在通过工具栏插入头部图片...")
        
        # 如果没有封面图片，尝试生成
        if not self.cover_image_path:
            if title:
                self._generate_cover_image(title)
            if not self.cover_image_path:
                print("   ⚠️ 没有可用的封面图片，跳过图片插入")
                return
        
        try:
            # 先移动光标到正文开头
            from DrissionPage.common import Keys
            self.page.actions.key_down(Keys.CTRL).key_down(Keys.HOME).key_up(Keys.HOME).key_up(Keys.CTRL)
            time.sleep(0.5)
            
            # 步骤1: 点击工具栏的"图片"按钮（触发下拉菜单）
            print("   📍 步骤1: 点击图片按钮...")
            img_btn = self.page.ele('css:#js_editor_insertimage', timeout=3)  # 精确ID选择器
            if not img_btn:
                img_btn = self.page.ele('text:图片', timeout=2)
            if not img_btn:
                img_btn = self.page.ele('css:.edui-btn-image', timeout=2)
            
            if not img_btn:
                print("   ⚠️ 未找到图片工具栏按钮")
                return
            
            try:
                img_btn.click(by_js=True)
            except:
                self.page.run_js('arguments[0].click()', img_btn)
            print("   ✅ 已点击图片按钮")
            time.sleep(1)
            
            # 步骤2: 在下拉菜单中找到"本地上传"选项
            print("   📍 步骤2: 查找本地上传菜单项...")
            
            # 根据截图，结构是 li.tpl_dropdown_menu_item 包含 "本地上传" 文字和 input[type=file]
            local_upload_item = None
            
            # 方法1：直接找包含"本地上传"文字的 li 元素
            try:
                menu_items = self.page.eles('css:li.tpl_dropdown_menu_item', timeout=3)
                for item in menu_items:
                    text = item.text.strip() if item.text else ""
                    if '本地上传' in text:
                        local_upload_item = item
                        print(f"   ✅ 找到本地上传菜单项")
                        break
            except:
                pass
            
            # 方法2：直接通过文字查找
            if not local_upload_item:
                try:
                    local_upload_item = self.page.ele('text:本地上传', timeout=2)
                    if local_upload_item:
                        # 如果找到的是文本节点，获取其父元素 li
                        parent = local_upload_item.parent()
                        if parent and 'li' in str(parent.tag).lower():
                            local_upload_item = parent
                        print(f"   ✅ 通过文字找到本地上传")
                except:
                    pass
            
            if not local_upload_item:
                print("   ⚠️ 未找到本地上传菜单项，尝试直接查找文件输入...")
                # 回退到直接查找 input
                file_inputs = self.page.eles('css:input[type="file"]', timeout=3)
                if file_inputs:
                    local_upload_item = file_inputs[0].parent()
            
            # 步骤3: 在该菜单项内找到 input[type=file] 并注入文件
            print("   📍 步骤3: 注入图片文件...")
            
            file_input = None
            if local_upload_item:
                # 在本地上传菜单项内查找 file input
                try:
                    file_input = local_upload_item.ele('css:input[type="file"]', timeout=2)
                except:
                    pass
                
                if not file_input:
                    # 菜单项本身可能就是 input 的容器
                    try:
                        file_input = self.page.ele('css:.tpl_dropdown_menu input[type="file"]', timeout=2)
                    except:
                        pass
            
            # 最后的回退：找页面上任何可见的 file input
            if not file_input:
                try:
                    file_inputs = self.page.eles('css:input[type="file"]', timeout=2)
                    for inp in file_inputs:
                        # 检查是否可交互（不是 hidden）
                        file_input = inp
                        break
                except:
                    pass
            
            if not file_input:
                print("   ❌ 未找到文件上传入口")
                return
            
            # 注入文件
            file_input.input(self.cover_image_path)
            print(f"   ✅ 图片已注入: {self.cover_image_path}")
            
            # 等待上传完成
            print("   ⏳ 等待图片上传完成...")
            time.sleep(5)  # 简单等待5秒
            
            # 检查一次是否上传成功
            content_img = self.page.ele('css:.mock-iframe-body img[src*="mmbiz"]', timeout=1)
            if content_img:
                print(f"   ✅ 图片上传成功！")
            else:
                print(f"   ⚠️ 未能确认上传成功，但流程继续...")
            
            time.sleep(1)
                
        except Exception as e:
            print(f"   ⚠️ 插入图片失败: {e}")

    def _apply_wechat_style(self, line: str) -> str:
        """
        为文本行应用微信编辑器多彩样式
        根据内容类型返回带内联样式的 HTML
        """
        import html
        import re
        
        # 转义 HTML 特殊字符
        escaped_line = html.escape(line)
        
        # 标题样式（以 emoji 或数字开头的章节标题）
        if re.match(r'^[🤖🛠️🧠⚡💡━]+|^[一二三四五六七八九十]、', line):
            return f'<span style="color: #07c160; font-size: 18px; font-weight: bold;">{escaped_line}</span>'
        
        # 分隔线
        if '━━━━' in line:
            return f'<span style="color: #ccc; text-align: center; display: block;">{escaped_line}</span>'
        
        # 代码块标记
        if line.startswith('`') or line.startswith('curl') or line.startswith('ollama'):
            return f'<span style="background-color: #2d2d2d; color: #f8f8f2; padding: 2px 6px; border-radius: 4px; font-family: monospace;">{escaped_line}</span>'
        
        # 列表项（以数字.或-开头）
        if re.match(r'^[\d]+\.|^-\s', line):
            return f'<span style="color: #333; padding-left: 8px;">{escaped_line}</span>'
        
        # 强调文本（包含**的行）
        if '**' in line:
            # 将 **text** 转换为带样式的文本
            styled = re.sub(r'\*\*(.+?)\*\*', r'<span style="color: #e74c3c; font-weight: bold;">\1</span>', escaped_line)
            return styled
        
        # 引用（以👉或建议开头）
        if '👉' in line or '建议' in line:
            return f'<span style="color: #666; font-style: italic;">{escaped_line}</span>'
        
        # CTA 行动号召
        if '立刻行动' in line or '关注我' in line:
            return f'<span style="color: #07c160; font-weight: bold;">{escaped_line}</span>'
        
        # 普通文本
        return f'<span style="color: #333; line-height: 1.8;">{escaped_line}</span>'

    def _screenshot(self, step_name: str):
        """截图并保存"""
        if not hasattr(self, '_screenshot_dir'):
            import os
            from datetime import datetime
            self._screenshot_dir = f"debug_screenshots/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(self._screenshot_dir, exist_ok=True)
            self._screenshot_count = 0
            print(f"📸 截图目录: {self._screenshot_dir}")
        
        self._screenshot_count += 1
        filepath = f"{self._screenshot_dir}/{self._screenshot_count:02d}_{step_name}.png"
        try:
            self.page.get_screenshot(filepath)
            print(f"📸 [{self._screenshot_count}] 截图: {step_name}")
        except Exception as e:
            print(f"📸 截图失败: {e}")

    def _handle_additional_settings(self, title_text: str):
        """处理封面、原创和创作来源设置
        新逻辑：
        1. 正文已通过工具栏插入图片 → 从正文选择封面
        2. 如果正文没有图片且有本地封面 → 上传到图片库后选择
        """
        print("🛠️  正在处理文章设置（封面、原创、来源）...")
        
        # ==========================================
        # 🖼️ 封面设置：优先从正文选择，否则上传本地图片
        # ==========================================
        try:
            print("🖼️ 正在设置封面...")
            
            # 预处理本地封面图片（如果有）
            processed_cover = None
            if self.cover_image_path:
                processed_cover = self._preprocess_cover_image(self.cover_image_path)
                print(f"📁 本地封面图片: {processed_cover}")
            
            # 无论是否有本地封面，都尝试设置封面
            # _stage2_select_from_library 内部会判断：
            # - 正文有图片 → 从正文选择
            # - 正文无图片 → 使用本地图片上传
            self._stage2_select_from_library(processed_cover)

        except Exception as e:
            print(f"❌ 封面设置跳过: {e}")
            import traceback
            traceback.print_exc()
        
        # ==========================================
        # ✍️ 设置原创声明（增强版：更多等待和重试）
        # ==========================================
        try:
            # 等待页面稳定
            print("\n⏳ 等待页面稳定后设置原创声明...")
            time.sleep(3)
            self._set_original_declaration()
        except Exception as e:
            print(f"⚠️ 原创声明设置跳过: {e}")
        
        # ==========================================
        # 📝 设置创作来源为"不声明"
        # ==========================================
        try:
            self._set_creation_source_no_declare()
        except Exception as e:
            print(f"⚠️ 创作来源设置跳过: {e}")
    
    def _check_original_dialog(self) -> bool:
        """检查原创声明弹窗是否可见"""
        try:
            # 查找"声明类型"或"文字原创"等标志性文字
            if self.page.ele('text:声明类型', timeout=0.5):
                return True
            if self.page.ele('text:文字原创', timeout=0.5):
                return True
            # 直接查找复选框
            if self.page.ele('css:.weui-desktop-form__checkbox', timeout=0.5):
                return True
            return False
        except:
            return False

    def _set_original_declaration(self):
        """设置原创声明（简化版：直接点击"未声明"文字触发弹窗）"""
        print("\n✍️ 正在设置原创声明...")
        
        try:
            # 等待页面稳定
            time.sleep(2)
            
            # 滚动到原创区域
            try:
                original_box = self.page.ele('css:#js_original_box', timeout=3)
                if original_box:
                    original_box.scroll.to_see()
                    time.sleep(1)
            except:
                pass
            
            # 方法1：直接点击"未声明"文字（最可靠）
            trigger_ele = None
            trigger_selectors = [
                'text:未声明',
                'css:#js_original_box .setting-group__content',
                'css:.weui-desktop-link',
            ]
            
            for selector in trigger_selectors:
                try:
                    ele = self.page.ele(selector, timeout=2)
                    if ele and ele.states.is_displayed:
                        trigger_ele = ele
                        print(f"   找到触发元素: {selector}")
                        break
                except:
                    continue
            
            if trigger_ele:
                trigger_ele.click()
                print("   ✅ 点击触发原创弹窗")
                time.sleep(2)
            else:
                # 备用：双击原创区域
                try:
                    original_area = self.page.ele('css:#js_original_box', timeout=2)
                    if original_area:
                        original_area.double_click()
                        time.sleep(2)
                except:
                    print("   ⚠️ 未找到原创区域")
                    return False
            
            # 检查弹窗是否打开
            if not self._check_original_dialog():
                print("   ❌ 未能打开原创声明弹窗")
                return False
            
            print("   ✅ 原创弹窗已打开")
            time.sleep(1)
            
            # 2. 选择"文字原创"
            try:
                text_original = self.page.ele('text:文字原创', timeout=3)
                if text_original:
                    text_original.click()
                    print("   ✅ 选择'文字原创'")
                    time.sleep(1)
            except:
                pass
            
            # 3. 复选框处理 - 注释掉，因为打开弹窗时通常已经勾选
            # 如果点击会导致取消勾选，所以跳过这一步
            print("   ✅ 跳过复选框点击（通常已默认勾选）")
            # checkbox_clicked = False
            # try:
            #     print("   正在寻找复选框...")
            #     checked_icon = self.page.ele('css:i.weui-desktop-icon-checkbox_focus', timeout=2)
            #     if checked_icon and checked_icon.states.is_displayed:
            #         print("   ✅ 复选框已经勾选，无需再点击")
            #         checkbox_clicked = True
            #     else:
            #         checkbox_icon = self.page.ele('css:i.weui-desktop-icon-checkbox', timeout=3)
            #         if checkbox_icon and checkbox_icon.states.is_displayed:
            #             checkbox_icon.click(by_js=True)
            #             checkbox_clicked = True
            #             print("   ✅ 点击复选框小方框")
            #             time.sleep(2)
            # except Exception as e:
            #     print(f"   ⚠️ 勾选复选框遇到问题: {e}")
            
            # 4. 点击确定按钮 - 在原创声明弹窗内查找
            time.sleep(2)
            try:
                print("   正在寻找确定按钮...")
                
                # 方法1：先定位到原创声明弹窗容器，再在其中找确定按钮
                clicked = False
                dialog = self.page.ele('css:div.weui-desktop-dialog[style*="display"]', timeout=2) or \
                         self.page.ele('css:.weui-desktop-dialog__wrp', timeout=2)
                
                if dialog:
                    confirm_btn = dialog.ele('css:button.weui-desktop-btn_primary', timeout=2)
                    if confirm_btn and confirm_btn.text and '确定' in confirm_btn.text:
                        try:
                            confirm_btn.click(by_js=True)
                        except:
                            self.page.run_js('arguments[0].click()', confirm_btn)
                        clicked = True
                        print("   ✅ 在弹窗内找到并点击了确定按钮")
                
                # 方法2：回退到遍历所有按钮
                if not clicked:
                    all_btns = self.page.eles('css:button.weui-desktop-btn_primary', timeout=3)
                    print(f"   找到 {len(all_btns)} 个主要按钮")
                    
                    for idx, btn in enumerate(all_btns):
                        try:
                            btn_text = btn.text.strip() if btn.text else ""
                            print(f"   按钮 {idx+1}: '{btn_text}', 可见: {btn.states.is_displayed}")
                            
                            if btn_text == "确定" and btn.states.is_displayed:
                                try:
                                    btn.click(by_js=True)
                                except:
                                    self.page.run_js('arguments[0].click()', btn)
                                clicked = True
                                print(f"   ✅ 点击了按钮 {idx+1}")
                                break
                        except Exception as btn_err:
                            print(f"   按钮 {idx+1} 检查失败: {btn_err}")
                            continue
                
                if clicked:
                    time.sleep(2)
                    print("   🎉 原创声明设置完成！")
                    return True
                else:
                    print("   ⚠️ 未找到可点击的确定按钮")
            except Exception as e:
                print(f"   ⚠️ 点击确定按钮遇到问题: {e}")
            
            return False
                
        except Exception as e:
            print(f"   ⚠️ 原创声明设置失败: {e}")
            return False
    
    def _set_creation_source_no_declare(self):
        """设置创作来源为不声明"""
        print("\n📝 正在设置创作来源为'不声明'...")
        
        try:
            # 找到"创作来源"区域，点击展开选择
            # 先尝试找到"创作来源"文字
            source_label = self.page.ele('text:创作来源', timeout=3)
            if source_label:
                print("   找到创作来源标签")
                
                # 点击"不声明"选项
                # 查找所有包含"不声明"的元素
                no_declare = self.page.ele('text:不声明', timeout=3)
                if no_declare:
                    try:
                        no_declare.click(by_js=True)
                        print("   ✅ 已选择'不声明'")
                        time.sleep(1)
                        return True
                    except:
                        self.page.run_js('arguments[0].click()', no_declare)
                        print("   ✅ 已选择'不声明'（JS点击）")
                        time.sleep(1)
                        return True
                else:
                    # 可能已经是不声明状态
                    print("   ⚠️ 未找到'不声明'选项，可能已经是不声明状态")
            else:
                print("   ⚠️ 未找到创作来源标签")
                
        except Exception as e:
            print(f"   ⚠️ 设置创作来源失败: {e}")
        
        return False
    
    def _stage1_upload_to_library(self, image_path: str) -> bool:
        """
        阶段一：将图片上传到素材库
        这是"干净"的上传，不会触发封面处理的转圈问题
        """
        print("\n📦 === 阶段一：上传图片到素材库 ===")
        
        try:
            # 保存当前页面URL，稍后返回
            current_url = self.page.url
            
            # 1. 点击左侧菜单 "素材管理"
            print("🔍 查找素材管理菜单...")
            material_menu = self.page.ele('text:素材管理', timeout=5)
            if material_menu:
                material_menu.click(by_js=True)
                time.sleep(2)
                
                # 2. 点击 "图片"
                print("🔍 进入图片素材库...")
                img_menu = self.page.ele('text:图片', timeout=3)
                if img_menu:
                    img_menu.click(by_js=True)
                    time.sleep(3)
                    
                    # 3. 找到上传入口（隐藏的 input[type=file]）
                    print("📤 查找上传入口...")
                    file_input = self.page.ele('css:input[type="file"]', timeout=5)
                    
                    if file_input:
                        print(f"📤 上传图片: {image_path}")
                        file_input.input(image_path)
                        
                        # 4. 等待上传完成
                        print("⏳ 等待上传完成...")
                        time.sleep(8)  # 等待上传和处理
                        
                        print("✅ 阶段一完成：图片已上传到素材库！")
                        
                        # 返回编辑页面
                        print(f"🔙 返回编辑页面...")
                        self.page.get(current_url)
                        time.sleep(3)
                        
                        return True
                    else:
                        print("⚠️ 未找到上传入口")
                else:
                    print("⚠️ 未找到图片菜单")
            else:
                print("⚠️ 未找到素材管理菜单")
                
            return False
            
        except Exception as e:
            print(f"❌ 素材库上传失败: {e}")
            return False
    
    def _stage2_select_from_library(self, image_path: str = None) -> bool:
        """
        封面设置策略：从正文选择
        因为我们已经在正文中插入了图片，直接从正文选择最简单可靠
        """
        print("\n🖼️ === 封面设置（从正文选择） ===")
        
        # 步骤1: 点击封面区域打开弹窗
        print("📍 步骤1: 打开封面选择弹窗...")
        cover_btn = self.page.ele('text:选择封面', timeout=3) or \
                    self.page.ele('text:必须插入', timeout=2) or \
                    self.page.ele('text:拖拽或选择封面', timeout=2) or \
                    self.page.ele('css:.js_cover_area', timeout=2)
        
        if cover_btn:
            try:
                cover_btn.click(by_js=True)
            except:
                self.page.run_js('arguments[0].click()', cover_btn)
            print("   ✅ 弹窗已打开")
            time.sleep(2)
        else:
            print("   ❌ 未找到封面区域")
            return False
        
        # 步骤2: 点击"从正文选择"
        print("📍 步骤2: 点击'从正文选择'...")
        from_content_btn = self.page.ele('text:从正文选择', timeout=3)
        
        if from_content_btn:
            try:
                from_content_btn.click(by_js=True)
            except:
                self.page.run_js('arguments[0].click()', from_content_btn)
            print("   ✅ 已点击'从正文选择'")
            time.sleep(2)
        else:
            print("   ⚠️ 未找到'从正文选择'选项")
            # 尝试回退策略
            return self._fallback_cover_upload(image_path)
        
        # 步骤3: 选择第一张图片（即我们插入的封面图）
        print("📍 步骤3: 选择正文中的图片...")
        
        # 等待图片列表加载（轮询等待）
        img_item = None
        selectors = [
            'css:li.appmsg_content_img_item',  # 实际的图片列表项
            'css:.appmsg_content_img_item',    # 备用
            'css:span.appmsg_content_img',     # 图片 span
        ]
        
        # 轮询等待图片加载，最多10秒
        for wait_sec in range(10):
            for selector in selectors:
                try:
                    items = self.page.eles(selector, timeout=1)
                    if items:
                        img_item = items[0]  # 选择第一张
                        print(f"   ✅ 找到 {len(items)} 张图片，准备选择第一张")
                        break
                except:
                    continue
            if img_item:
                break
            print(f"      等待图片加载... ({wait_sec+1}s)")
            time.sleep(1)
        
        if img_item:
            # 点击图片项以选中
            try:
                img_item.click(by_js=True)
            except:
                self.page.run_js('arguments[0].click()', img_item)
            print("   ✅ 已点击图片项")
            time.sleep(1)
            
            # 验证是否选中（检查 selected 类）
            for check in range(5):
                try:
                    selected_item = self.page.ele('css:li.appmsg_content_img_item.selected', timeout=1)
                    if selected_item:
                        print("   ✅ 图片已选中（检测到 selected 类）")
                        break
                except:
                    pass
                time.sleep(0.5)
            else:
                print("   ⚠️ 未能确认选中状态，继续尝试下一步")
        else:
            # 回退：点击任何可见的图片
            print("   ⚠️ 未找到图片列表项，尝试点击图片 span...")
            any_img = self.page.ele('css:span.appmsg_content_img', timeout=2)
            if any_img:
                any_img.click(by_js=True)
                time.sleep(1)
            else:
                print("   ❌ 未找到任何可选择的图片")
                return False
        
        time.sleep(1)
        
        # 步骤4: 点击下一步按钮
        print("📍 步骤4: 点击'下一步'...")
        next_btn = self.page.ele('text:下一步', timeout=3)
        
        if next_btn and next_btn.states.is_displayed:
            try:
                next_btn.click(by_js=True)
            except:
                self.page.run_js('arguments[0].click()', next_btn)
            print("   ✅ 已点击'下一步'")
            time.sleep(2)
        else:
            # 尝试其他确认按钮
            confirm_selectors = ['text:确定', 'text:完成', 'text:使用']
            for selector in confirm_selectors:
                try:
                    btn = self.page.ele(selector, timeout=1)
                    if btn and btn.states.is_displayed:
                        btn.click(by_js=True)
                        print(f"   ✅ 已点击: {selector}")
                        time.sleep(2)
                        break
                except:
                    continue
        
        # 步骤5: 处理裁剪预览确认（只需点一次确认）
        print("📍 步骤5: 处理裁剪预览确认...")
        time.sleep(2)  # 等待裁剪预览页面加载
        
        # 查找并点击"确认"按钮（只需一次）
        confirm_clicked = False
        for attempt in range(3):  # 最多尝试3次找按钮
            try:
                # 方法1：使用按钮类选择器（更精确）
                primary_btns = self.page.eles('css:button.weui-desktop-btn_primary', timeout=2)
                for btn in primary_btns:
                    try:
                        btn_text = btn.text.strip() if btn.text else ""
                        if btn_text == '确认' and btn.states.is_displayed:
                            # 点击确认按钮
                            try:
                                btn.click()  # 物理点击
                            except:
                                btn.click(by_js=True)
                            confirm_clicked = True
                            print("   ✅ 已点击'确认'按钮")
                            time.sleep(2)
                            break
                    except:
                        continue
                
                if confirm_clicked:
                    break
                    
                # 方法2：直接找"确认"文字
                confirm_btn = self.page.ele('text:确认', timeout=1)
                if confirm_btn and confirm_btn.states.is_displayed:
                    confirm_btn.click()
                    confirm_clicked = True
                    print("   ✅ 已点击'确认'按钮")
                    time.sleep(2)
                    break
                    
                time.sleep(1)
            except:
                time.sleep(1)
        
        if not confirm_clicked:
            print("   ⚠️ 未找到裁剪确认按钮，可能已自动完成")
        
        print("🎉 封面设置完成！")
        return True
    
    def _fallback_cover_upload(self, image_path: str = None) -> bool:
        """回退策略：直接上传本地图片"""
        print("   📍 使用回退策略：本地上传...")
        upload_path = image_path or self.cover_image_path
        if not upload_path:
            print("   ❌ 没有可用的封面图片")
            return False
        
        # 查找文件上传入口
        file_inputs = self.page.eles('css:input[type="file"]', timeout=3)
        if file_inputs:
            try:
                file_inputs[0].input(upload_path)
                print(f"   ✅ 已注入封面文件")
                time.sleep(3)
                return True
            except Exception as e:
                print(f"   ❌ 注入失败: {e}")
        return False
    
    def _select_from_content_images(self, img_items) -> bool:
        """从正文中选择封面图片（已经在从正文选择标签页）"""
        print("\n📍 步骤3: 选择正文图片...")
        
        try:
            for item in img_items:
                if item.states.is_displayed:
                    try:
                        item.click(by_js=True)
                    except:
                        self.page.run_js('arguments[0].click()', item)
                    
                    time.sleep(1)
                    
                    # 检查是否选中成功
                    selected = self.page.ele('css:.appmsg_content_img_item.selected', timeout=1)
                    if selected:
                        print("   ✅ 图片已选中")
                    else:
                        print("   ✅ 已点击图片")
                    break
            
            # 点击确认按钮
            return self._click_cover_confirm_buttons()
            
        except Exception as e:
            print(f"   ❌ 从正文选择失败: {e}")
            return False
    
    def _select_from_image_library(self, image_path: str) -> bool:
        """从图片库选择封面（先上传再选择）"""
        print("\n📍 步骤3: 切换到图片库上传...")
        
        try:
            # 点击"从图片库选择"标签
            library_tab = self.page.ele('text:从图片库选择', timeout=3)
            if library_tab:
                try:
                    library_tab.click(by_js=True)
                except:
                    self.page.run_js('arguments[0].click()', library_tab)
                print("   ✅ 已切换到图片库")
                time.sleep(2)
            else:
                print("   ⚠️ 未找到图片库标签")
            
            # 点击"上传文件"按钮
            print("📍 步骤4: 点击上传文件按钮...")
            upload_btn = self.page.ele('text:上传文件', timeout=3)
            if not upload_btn:
                upload_btn = self.page.ele('css:.js_upload_btn', timeout=2)
            
            if upload_btn:
                try:
                    upload_btn.click(by_js=True)
                except:
                    self.page.run_js('arguments[0].click()', upload_btn)
                print("   ✅ 已点击上传按钮")
                time.sleep(1)
            
            # 查找上传入口并注入文件
            print("📍 步骤5: 上传图片文件...")
            file_inputs = self.page.eles('css:input[type="file"]', timeout=5)
            if file_inputs and image_path:
                print(f"   找到 {len(file_inputs)} 个上传入口")
                
                for file_input in file_inputs:
                    try:
                        file_input.input(image_path)
                        print(f"   ✅ 文件已注入")
                        
                        # 等待上传完成 - 增强版：轮询检测图片是否出现
                        print("   ⏳ 等待图片上传完成...")
                        upload_success = False
                        for wait_attempt in range(15):  # 最多等待15秒
                            time.sleep(1)
                            
                            # 检查是否有上传进度条消失（表示上传完成）
                            progress_bar = self.page.ele('css:.weui-desktop-progress', timeout=0.3)
                            if progress_bar:
                                print(f"      上传中... ({wait_attempt + 1}s)")
                                continue
                            
                            # 检查是否有图片项出现
                            img_items = self.page.eles('css:.js_image_item, .image_item, .weui-desktop-img-picker__item', timeout=0.5)
                            if img_items and len(img_items) > 0:
                                print(f"   ✅ 检测到 {len(img_items)} 张图片，上传成功！")
                                upload_success = True
                                break
                            
                            # 检查是否有错误提示
                            error_tip = self.page.ele('text:上传失败', timeout=0.3) or \
                                        self.page.ele('text:格式不支持', timeout=0.3)
                            if error_tip:
                                print(f"   ❌ 上传出错: {error_tip.text}")
                                break
                        
                        if not upload_success:
                            print("   ⚠️ 上传超时或未检测到图片，尝试继续...")
                        
                        break
                    except Exception as e:
                        print(f"   注入失败: {e}")
                        continue
            else:
                print("   ❌ 未找到上传入口或没有图片路径")
                return False
            
            # 等待图片出现在图片库中
            print("📍 步骤6: 等待图片上传完成...")
            time.sleep(3)
            
            # 选择刚上传的图片（通常是第一个）
            print("📍 步骤7: 选择上传的图片...")
            img_item = self.page.ele('css:.js_image_item', timeout=5)
            if not img_item:
                img_item = self.page.ele('css:.image_item', timeout=2)
            if not img_item:
                img_item = self.page.ele('css:.weui-desktop-img-picker__item', timeout=2)
            
            if img_item:
                try:
                    img_item.click(by_js=True)
                except:
                    self.page.run_js('arguments[0].click()', img_item)
                print("   ✅ 已选择图片")
                time.sleep(1)
            else:
                print("   ⚠️ 未找到可选图片，尝试直接确认...")
            
            # 点击确认按钮
            return self._click_cover_confirm_buttons()
            
        except Exception as e:
            print(f"   ❌ 图片库上传失败: {e}")
            return False
    
    def _click_cover_confirm_buttons(self) -> bool:
        """点击封面设置的确认按钮（可能需要多次）"""
        print("📍 确认选择...")
        
        for attempt in range(5):
            time.sleep(2)
            
            # 使用全局搜索所有按钮，然后过滤
            confirm_btn = None
            target_texts = ['下一步', '确认', '确定', '完成']
            exclude_texts = ['取消', '关闭', '退出登录', '我知道了', '上一步', '保存为草稿', '预览', '发表']
            
            # 方法1：直接搜索所有 button 元素
            try:
                all_buttons = self.page.eles('tag:button', timeout=2)
                for btn in all_buttons:
                    try:
                        if btn.states.is_displayed:
                            btn_text = btn.text.strip() if btn.text else ""
                            # 检查是否是目标按钮
                            if btn_text in target_texts and btn_text not in exclude_texts:
                                confirm_btn = btn
                                break
                    except:
                        continue
            except:
                pass
            
            # 方法2：通过 class 搜索
            if not confirm_btn:
                try:
                    primary_btns = self.page.eles('css:.weui-desktop-btn_primary', timeout=1)
                    for btn in primary_btns:
                        try:
                            if btn.states.is_displayed:
                                btn_text = btn.text.strip() if btn.text else ""
                                if btn_text in target_texts and btn_text not in exclude_texts:
                                    confirm_btn = btn
                                    break
                        except:
                            continue
                except:
                    pass
            
            if confirm_btn:
                btn_text = confirm_btn.text.strip() if confirm_btn.text else "按钮"
                try:
                    # 尝试多种点击方式
                    confirm_btn.click(by_js=True)
                except:
                    try:
                        self.page.run_js('arguments[0].click()', confirm_btn)
                    except:
                        try:
                            # 强制触发 click 事件
                            self.page.run_js('''
                                var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                                arguments[0].dispatchEvent(evt);
                            ''', confirm_btn)
                        except:
                            pass
                print(f"   第{attempt + 1}次: 点击【{btn_text}】")
                time.sleep(1.5)
            else:
                # 如果找不到按钮，可能已完成
                print(f"   第{attempt + 1}次: 未找到确认按钮，流程可能已完成")
                break
        
        print("🎉 封面设置完成！")
        return True
    
    def _upload_cover_via_dialog(self, image_path: str) -> bool:
        """通过弹窗直接上传封面图片（旧方法，保留兼容）"""
        if not image_path:
            print("   ❌ 没有可用的封面图片路径")
            return False
        
        print(f"   📁 将上传: {image_path}")
        
        try:
            # 步骤1: 点击封面区域，打开弹窗
            print("📍 步骤1: 点击封面区域...")
            
            cover_btn = self.page.ele('text:选择封面', timeout=3)
            if not cover_btn:
                cover_btn = self.page.ele('text:拖拽或选择封面', timeout=2)
            if not cover_btn:
                cover_btn = self.page.ele('css:.js_cover_area', timeout=2)
            
            if cover_btn:
                try:
                    cover_btn.click(by_js=True)
                except:
                    self.page.run_js('arguments[0].click()', cover_btn)
                print("   ✅ 已点击封面区域")
                time.sleep(2)
            else:
                print("   ❌ 未找到封面区域")
                return False
            
            # 步骤2: 查找并使用文件上传入口
            print("📍 步骤2: 上传图片...")
            
            file_inputs = self.page.eles('css:input[type="file"]', timeout=5)
            if not file_inputs:
                print("   ❌ 未找到上传入口")
                return False
            
            print(f"   找到 {len(file_inputs)} 个上传入口")
            
            for file_input in file_inputs:
                try:
                    file_input.input(image_path)
                    print("   ✅ 文件已注入")
                    time.sleep(3)
                    
                    # 步骤3: 点击确认按钮
                    print("📍 步骤3: 确认上传...")
                    
                    for attempt in range(5):
                        time.sleep(2)
                        confirm_btn = self.page.ele('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=2)
                        if confirm_btn:
                            btn_text = confirm_btn.text.strip() if confirm_btn.text else ""
                            if btn_text in ["下一步", "确定", "完成"]:
                                try:
                                    confirm_btn.click(by_js=True)
                                except:
                                    self.page.run_js('arguments[0].click()', confirm_btn)
                                print(f"   点击【{btn_text}】")
                        else:
                            break
                    
                    print("🎉 封面上传完成！")
                    return True
                    
                except Exception as e:
                    print(f"   上传尝试失败: {e}")
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ 封面上传失败: {e}")
            return False
    
    def _select_cover_from_content(self) -> bool:
        """从正文中选择封面（备用方案）"""
        print("\n🎯 === 封面设置：从正文选择 ===")
        
        DEBUG_MODE = False
        
        try:
            # ========================================
            # 步骤1: 点击封面区域，打开弹窗
            # ========================================
            print("📍 步骤1: 点击封面区域...")
            
            cover_btn = self.page.ele('text:选择封面', timeout=3)
            if not cover_btn:
                cover_btn = self.page.ele('text:拖拽或选择封面', timeout=2)
            if not cover_btn:
                cover_btn = self.page.ele('css:.js_cover_area', timeout=2)
            
            if cover_btn:
                try:
                    cover_btn.click(by_js=True)
                except:
                    self.page.run_js('arguments[0].click()', cover_btn)
                print("   ✅ 已点击封面区域")
                time.sleep(2)
            else:
                print("   ❌ 未找到封面区域")
                return False
            
            # ========================================
            # 步骤2: 点击"从正文选择"标签
            # ========================================
            print("📍 步骤2: 切换到'从正文选择'...")
            
            time.sleep(1)
            
            # 查找"从正文选择"选项卡
            from_content_tab = self.page.ele('text:从正文选择', timeout=3)
            if not from_content_tab:
                from_content_tab = self.page.ele('text=从正文选择', timeout=2)
            
            if from_content_tab:
                try:
                    from_content_tab.click(by_js=True)
                except:
                    self.page.run_js('arguments[0].click()', from_content_tab)
                print("   ✅ 已切换到'从正文选择'")
                time.sleep(2)
            else:
                print("   ⚠️ 未找到'从正文选择'选项卡，尝试直接选择图片...")
            
            # ========================================
            # 步骤3: 选择正文中的第一张图片
            # ========================================
            print("📍 步骤3: 选择正文图片...")
            
            time.sleep(1)
            
            img_selected = False
            
            # 使用正确的选择器：.appmsg_content_img_item
            # 选中后会变成 .appmsg_content_img_item.selected
            try:
                img_items = self.page.eles('css:.appmsg_content_img_item', timeout=3)
                
                if img_items and len(img_items) > 0:
                    print(f"   找到 {len(img_items)} 张正文图片")
                    
                    for item in img_items:
                        if item.states.is_displayed:
                            try:
                                item.click(by_js=True)
                            except:
                                self.page.run_js('arguments[0].click()', item)
                            
                            time.sleep(0.5)
                            
                            # 检查是否选中成功（class 变成 selected）
                            try:
                                selected = self.page.ele('css:.appmsg_content_img_item.selected', timeout=1)
                                if selected:
                                    print("   ✅ 图片已选中")
                                    img_selected = True
                                    break
                            except:
                                # 即使没检测到 selected class，也认为点击成功
                                print("   ✅ 已点击图片")
                                img_selected = True
                                break
                else:
                    print("   ⚠️ 正文中没有可用图片")
                    
            except Exception as e:
                print(f"   查找图片失败: {e}")
            
            # 如果正文没有图片，回退到本地上传
            if not img_selected:
                print("   🔄 回退到本地上传方式...")
                
                # 关闭当前弹窗
                try:
                    cancel_btn = self.page.ele('text:取消', timeout=2)
                    if cancel_btn:
                        cancel_btn.click(by_js=True)
                        time.sleep(1)
                except:
                    pass
                
                # 尝试本地上传
                return self._upload_cover_directly(image_path)
            
            # ========================================
            # 步骤4: 点击确认按钮
            # ========================================
            print("📍 步骤4: 确认选择...")
            
            for attempt in range(3):
                time.sleep(2)
                
                # 找确认按钮
                confirm_btn = None
                btns = self.page.eles('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=2)
                for btn in btns:
                    btn_text = btn.text.strip() if btn.text else ""
                    if btn_text in ["下一步", "确定", "完成"] and btn.states.is_displayed:
                        if btn_text not in ["退出登录", "换风格"]:
                            confirm_btn = btn
                            break
                
                if confirm_btn:
                    btn_text = confirm_btn.text.strip()
                    print(f"   第{attempt + 1}次: 点击【{btn_text}】...")
                    try:
                        confirm_btn.click()
                    except:
                        self.page.run_js('arguments[0].click()', confirm_btn)
                    time.sleep(2)
                else:
                    print(f"   第{attempt + 1}次: 未找到确认按钮")
                    break
            
            print("🎉 封面设置流程完成！")
            return True
            
        except Exception as e:
            print(f"❌ 封面设置失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _upload_cover_directly(self, image_path: str = None) -> bool:
        """
        直接上传封面图片（作为回退方案）
        当正文中没有图片时使用此方法
        """
        print("\n📤 === 使用本地上传方式设置封面 ===")
        
        upload_path = image_path or self.cover_image_path
        if not upload_path:
            print("   ❌ 没有可用的封面图片")
            return False
        
        print(f"   📁 将上传: {upload_path}")
        
        try:
            # 重新打开封面选择弹窗
            cover_btn = self.page.ele('text:选择封面', timeout=3) or \
                        self.page.ele('text:拖拽或选择封面', timeout=2) or \
                        self.page.ele('css:.js_cover_area', timeout=2)
            
            if cover_btn:
                try:
                    cover_btn.click(by_js=True)
                except:
                    self.page.run_js('arguments[0].click()', cover_btn)
                time.sleep(2)
            
            # 查找上传入口（隐藏的 input[type=file]）
            file_inputs = self.page.eles('css:input[type="file"]', timeout=5)
            print(f"   找到 {len(file_inputs) if file_inputs else 0} 个文件上传入口")
            
            for file_input in file_inputs if file_inputs else []:
                try:
                    file_input.input(upload_path)
                    print(f"   ✅ 文件已注入")
                    time.sleep(3)
                    
                    # 查找并点击确认按钮
                    for _ in range(3):
                        time.sleep(2)
                        confirm_btn = self.page.ele('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=2)
                        if confirm_btn:
                            btn_text = confirm_btn.text.strip() if confirm_btn.text else ""
                            if btn_text in ["下一步", "确定", "完成"]:
                                try:
                                    confirm_btn.click(by_js=True)
                                except:
                                    self.page.run_js('arguments[0].click()', confirm_btn)
                                print(f"   点击【{btn_text}】")
                                time.sleep(2)
                    
                    print("   🎉 本地上传封面完成")
                    return True
                    
                except Exception as e:
                    print(f"   上传失败: {e}")
                    continue
            
            print("   ❌ 本地上传方式也失败了")
            return False
            
        except Exception as e:
            print(f"   ❌ 本地上传失败: {e}")
            return False
    
    def _try_direct_upload(self):
        """尝试直接通过 input[type=file] 上传封面（旧方法，保留兼容）"""
        return self._upload_cover_directly()
    
    def _physical_click(self, element, description: str = "元素"):
        """
        物理坐标打击：使用真实鼠标移动和点击
        这种方式对浏览器来说和真人操作没有区别
        """
        try:
            # 方法1：直接使用 DrissionPage 的 actions（最推荐）
            try:
                # 先滚动到元素可见
                element.scroll.to_see()
                time.sleep(0.3)
                
                # 移动到元素并点击
                self.page.actions.move_to(element)
                time.sleep(0.2)
                self.page.actions.click()
                
                print(f"   ✅ 物理点击 {description} 完成")
                return True
            except Exception as e1:
                print(f"   actions方式失败: {e1}")
            
            # 方法2：使用元素的 click 方法但不用 JS
            try:
                element.click()
                print(f"   ✅ 直接click {description} 完成")
                return True
            except Exception as e2:
                print(f"   直接click失败: {e2}")
            
            # 方法3：最后回退到 JS
            self.page.run_js('arguments[0].click()', element)
            print(f"   ⚠️ 回退到JS点击 {description}")
            return True
            
        except Exception as e:
            print(f"   ❌ 物理点击 {description} 完全失败: {e}")
            return False
    
    def _click_confirm_physical(self, max_attempts: int = 5) -> bool:
        """
        使用物理点击方式点击确定按钮
        """
        print("🔫 物理打击模式：正在寻找确定按钮...")
        
        for attempt in range(max_attempts):
            print(f"   🎯 尝试 {attempt + 1}/{max_attempts}...")
            
            # 找到图片选择弹窗内的确定按钮
            target_btn = None
            try:
                dialogs = self.page.eles('css:.weui-desktop-dialog__wrp', timeout=2)
                for dialog in dialogs:
                    try:
                        if not dialog.states.is_displayed:
                            continue
                        
                        dialog_text = dialog.text if dialog.text else ""
                        if "已选择" in dialog_text or "选择图片" in dialog_text or "裁剪" in dialog_text:
                            btns = dialog.eles('css:.weui-desktop-btn_primary')
                            for btn in btns:
                                text = btn.text.strip() if btn.text else ""
                                if text in ["确定", "下一步", "完成"] and btn.states.is_displayed:
                                    if text not in ["退出登录", "换风格"]:
                                        target_btn = btn
                                        print(f"      ✅ 在弹窗内找到按钮: 【{text}】")
                                        break
                            if target_btn:
                                break
                    except:
                        continue
            except:
                pass
            
            # 备用：直接在 dialog__ft 里找
            if not target_btn:
                try:
                    btns = self.page.eles('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=1)
                    for btn in btns:
                        text = btn.text.strip() if btn.text else ""
                        if text == "确定" and btn.states.is_displayed:
                            target_btn = btn
                            print(f"      ✅ 备用方案找到: 【{text}】")
                            break
                except:
                    pass
            
            if target_btn:
                # 使用物理点击！
                if self._physical_click(target_btn, "确定按钮"):
                    time.sleep(2)
                    print("   💥 物理点击已执行！")
                    
                    # 继续处理下一个可能的确认
                    time.sleep(1)
                    # 递归查找下一个确认按钮（裁剪确认等）
                    next_btn = self.page.ele('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=3)
                    if next_btn and next_btn.text.strip() in ["确定", "完成"]:
                        print("   🔄 发现下一步确认按钮...")
                        self._physical_click(next_btn, "裁剪确认")
                        time.sleep(2)
                    
                    return True
            else:
                print("   ⚠️ 没有找到确定按钮")
            
            time.sleep(1)
        
        return False
    
    def _click_confirm_sniper(self, max_attempts: int = 5) -> bool:
        """
        狙击级点击：只点击【图片选择弹窗】内的【可见的】确定按钮。
        关键：先定位包含"已选择"的弹窗，再在该弹窗内找确定按钮。
        """
        print("🔭 狙击模式：正在寻找【图片选择弹窗】内的确定按钮...")
        
        for attempt in range(max_attempts):
            print(f"   🎯 尝试 {attempt + 1}/{max_attempts}...")
            
            target_btn = None
            
            # 策略1: 找到包含"已选择"的弹窗，然后在里面找确定按钮
            try:
                # 查找所有弹窗wrapper
                dialogs = self.page.eles('css:.weui-desktop-dialog__wrp', timeout=2)
                print(f"      找到 {len(dialogs) if dialogs else 0} 个弹窗")
                
                for dialog in dialogs:
                    # 检查这个弹窗是否包含"已选择"文字（图片选择弹窗的特征）
                    try:
                        if not dialog.states.is_displayed:
                            continue
                        
                        dialog_text = dialog.text if dialog.text else ""
                        if "已选择" in dialog_text or "选择图片" in dialog_text:
                            print(f"      ✅ 找到图片选择弹窗！")
                            
                            # 在这个弹窗内找确定按钮
                            btns = dialog.eles('css:.weui-desktop-btn_primary')
                            for btn in btns:
                                text = btn.text.strip() if btn.text else ""
                                is_visible = btn.states.is_displayed
                                
                                # 排除干扰按钮
                                if text in ["退出登录", "换风格", "前往实名"]:
                                    continue
                                    
                                if text in ["确定", "下一步", "完成"] and is_visible:
                                    print(f"      🎯 在图片弹窗内找到: 【{text}】")
                                    target_btn = btn
                                    break
                            
                            if target_btn:
                                break
                    except:
                        continue
            except Exception as e:
                print(f"      策略1出错: {e}")
            
            # 策略2: 如果策略1没成功，直接在页面最后一个弹窗底部找
            if not target_btn:
                try:
                    # 找弹窗底部的按钮，但排除干扰项
                    btns = self.page.eles('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=1)
                    for btn in btns:
                        text = btn.text.strip() if btn.text else ""
                        is_visible = btn.states.is_displayed
                        
                        # 排除干扰按钮
                        if text in ["退出登录", "换风格", "前往实名", "取消", "关闭"]:
                            continue
                        
                        if text == "确定" and is_visible:
                            print(f"      🎯 策略2找到: 【{text}】")
                            target_btn = btn
                            break
                except:
                    pass
            
            # 执行点击 - 使用物理点击！
            if target_btn:
                try:
                    # 使用物理点击代替 JS 点击
                    self._physical_click(target_btn, "确定按钮")
                    print("   💥 物理点击已执行！")
                    time.sleep(2)
                    
                    # 点击确定后，直接处理可能的裁剪确认步骤
                    print("   🔄 处理可能的裁剪确认...")
                    # 也用物理点击处理裁剪确认
                    self._click_confirm_physical(max_attempts=3)
                    
                    print("   ✅ 图片选择流程完成！")
                    return True
                    
                except Exception as e:
                    print(f"   ❌ 点击出错: {e}")
            else:
                print("   ⚠️ 没有找到确定按钮")
            
            time.sleep(1)
        
        print("❌ 狙击失败：多次尝试后仍未能点击确定按钮")
        return False
    
    def _wait_and_click_dialog_confirm(self, action_name: str, timeout: int = 20):
        """
        等待并点击弹窗内的确认按钮（关键修复！）
        只在 .weui-desktop-dialog 内查找，避免误点"退出登录"等按钮
        """
        print(f"⏳ 等待{action_name}弹窗确认按钮...")
        
        for i in range(timeout * 2):  # 每0.5秒检查一次
            target = None
            
            # 方法1: 精确查找弹窗内的确认按钮
            # 优先使用 dialog footer 内的 primary 按钮
            dialog_selectors = [
                'css:.weui-desktop-dialog__ft .weui-desktop-btn_primary',  # 弹窗footer内的主按钮
                'css:.weui-desktop-dialog .weui-desktop-btn_primary',      # 弹窗内的主按钮
                'css:.weui-desktop-dialog__ft button:last-child',          # 弹窗footer最后一个按钮（通常是确认）
            ]
            
            for selector in dialog_selectors:
                try:
                    btn = self.page.ele(selector, timeout=0.1)
                    if btn:
                        btn_text = btn.text if btn else ""
                        # 确保不是取消/关闭按钮
                        if btn_text and btn_text not in ['取消', '关闭', '退出', '登录', '退出登录']:
                            # 确保是确认类按钮
                            if btn_text in ['确认', '完成', '确定', '下一步'] or '确' in btn_text:
                                target = btn
                                print(f"✅ 在弹窗内找到按钮: {btn_text} (选择器: {selector})")
                                break
                except:
                    continue
            
            # 方法2: 如果方法1没找到，尝试更宽泛的搜索
            if not target:
                try:
                    # 查找所有弹窗
                    dialogs = self.page.eles('css:.weui-desktop-dialog__wrp', timeout=0.1)
                    for dialog in dialogs:
                        # 检查弹窗是否可见
                        if dialog.states.is_displayed:
                            # 在这个弹窗内查找主按钮
                            btns = dialog.eles('css:.weui-desktop-btn_primary')
                            for btn in btns:
                                btn_text = btn.text if btn else ""
                                if btn_text in ['确认', '完成', '确定', '下一步']:
                                    target = btn
                                    print(f"✅ 在可见弹窗内找到按钮: {btn_text}")
                                    break
                            if target:
                                break
                except:
                    pass
            
            if target:
                print(f"⚡ 在第 {i*0.5} 秒找到{action_name}确认按钮!")
                self.page.run_js('arguments[0].click()', target)
                print(f"🎉 {action_name}确认按钮已点击！")
                time.sleep(2)
                return True
            
            # 显示等待进度
            if i % 4 == 0:  # 每2秒显示一次
                print(f"⏳ 等待弹窗出现... ({i*0.5}/{timeout}秒)")
            
            time.sleep(0.5)
        
        print(f"⚠️ {timeout}秒内未找到{action_name}弹窗确认按钮")
        return False
    
    def _wait_and_click_confirm(self, action_name: str, timeout: int = 20):
        """等待并点击确认按钮的通用方法"""
        print(f"⏳ 等待{action_name}确认按钮...")
        
        for i in range(timeout * 2):  # 每0.5秒检查一次
            target = None
            all_primary_btns = self.page.eles('css:.weui-desktop-btn.weui-desktop-btn_primary', timeout=0.1)
            
            for btn in all_primary_btns:
                btn_text = btn.text if btn else ""
                # 排除干扰项
                if any(keyword in btn_text for keyword in ['退出', '登录', '取消', '关闭']):
                    continue
                # 只要纯"确认"或"完成"或"确定"或"下一步"
                if btn_text in ['确认', '完成', '确定', '下一步']:
                    target = btn
                    break
            
            if target:
                print(f"⚡ 在第 {i*0.5} 秒找到{action_name}确认按钮: {target.text}")
                self.page.run_js('arguments[0].click()', target)
                print(f"✅ {action_name}确认按钮已点击！")
                time.sleep(1)
                return True
            
            time.sleep(0.5)
        
        print(f"⚠️ {timeout}秒内未找到{action_name}确认按钮")
        return False
    
    def _try_select_cover_from_content(self):
        """从正文选择封面（备用方案）"""
        try:
            print("🔄 尝试从正文选择封面...")
            
            # 点击封面区域
            cover_area = self.page.ele('css:.js_cover_area', timeout=3) or \
                        self.page.ele('text:拖拽或选择封面', timeout=2)
            
            if cover_area:
                cover_area.click(by_js=True)
                time.sleep(1)
            
            # 查找"从正文选择"按钮
            select_btn = self.page.ele('text:从正文选择', timeout=3) or \
                        self.page.ele('css:.js_selectCoverFromContent', timeout=2)
            
            if select_btn:
                print("📸 点击'从正文选择'按钮...")
                select_btn.click(by_js=True)
                time.sleep(2)
                
                # 选择第一张图片
                img_item = self.page.ele('css:.appmsg_content_img_item', timeout=3) or \
                          self.page.ele('css:.weui-desktop-img-picker__item', timeout=2)
                
                if img_item:
                    print("🖼️ 选择第一张正文图片...")
                    img_item.click()
                    time.sleep(1)
                    
                    # 点击下一步/确认
                    self._wait_and_click_confirm("封面选择")
                else:
                    print("⚠️ 正文中没有找到可选的图片")
            else:
                print("⚠️ 未找到'从正文选择'按钮")
                
        except Exception as e:
            print(f"❌ 从正文选择封面失败: {e}")
        
        # ==========================================
        # 以下是注释掉的"从正文选择"逻辑（备用）
        # ==========================================
        # try:
        #     print("🖼️ 正在设置封面...")
        #
        #     # 1. 直接用 JS 点击那个隐藏的按钮
        #     # 你的截图显示它的 class 是 js_selectCoverFromContent
        #     # 我们不需要先 hover，直接用 JS 触发它的点击事件，它自己会弹出来的
        #     
        #     # 尝试定位这个按钮
        #     select_btn = self.page.ele('css:.js_selectCoverFromContent', timeout=3)
        #     
        #     if select_btn:
        #         print("⚡️ 找到【从正文选择】按钮，正在点击...")
        #         select_btn.click(by_js=True)
        #         
        #         # 2. 等待图片选择弹窗出现
        #         # 根据用户截图，图片项的类名是 appmsg_content_img_item
        #         print("📸 等待图片加载...")
        #         
        #         # 尝试多种选择器
        #         img_item = None
        #         img_selectors = [
        #             'css:.appmsg_content_img_item',          # 用户截图确认的类名
        #             'css:.appmsg_content_img_mask',          # 图片遮罩层（也是可点击的）
        #             'css:.weui-desktop-img-picker__item',    # 旧版类名
        #             'css:li[class*="img_item"]',             # 模糊匹配
        #         ]
        #         
        #         for selector in img_selectors:
        #             try:
        #                 if self.page.ele(selector, timeout=2):
        #                     img_item = self.page.ele(selector)
        #                     print(f"✅ 找到图片元素: {selector}")
        #                     break
        #             except:
        #                 pass
        #         
        #         if img_item:
        #             print("📸 选中第一张图...")
        #             img_item.click()
        #             time.sleep(1)
        #             
        #             # 点击下一步
        #             # 使用更灵活的查找方式，因为有时是"下一步"
        #             next_btn = self.page.ele('text:下一步', timeout=2)
        #             if next_btn:
        #                 next_btn.click()
        #                 time.sleep(1)
        #             
        #             # 点击完成 (核弹级强制点击)
        #             print("💣 启动核弹级点击方案...")
        #             try:
        #                 # 1. 等待弹窗容器出现
        #                 self.page.ele('css:.weui-desktop-dialog__wrp', timeout=5)
        #                 
        #                 # 2. 定位绿色主按钮 (精确制导)
        #                 # 直接找 dialog footer 下的 primary button
        #                 confirm_btn = self.page.ele('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=3)
        #                 
        #                 if confirm_btn:
        #                     print(f"🎯 锁定确认按钮: {confirm_btn.text}")
        #                     # 3. 强行执行 JS 点击
        #                     self.page.run_js('arguments[0].click()', confirm_btn)
        #                     print("💥 呈序反馈：已强行按下确认键。")
        #                 else:
        #                     print("⚠️ 未找到绿色确认按钮，尝试备用方案...")
        #                     # 备用：找任意名为“确认”/“完成”的按钮，但排除退出
        #                     btns = self.page.eles('text:确认') + self.page.eles('text:完成') + self.page.eles('text:确定')
        #                     for btn in btns:
        #                         if btn.states.is_displayed and '退出' not in btn.text:
        #                             self.page.run_js('arguments[0].click()', btn)
        #                             print(f"💥 备用点击执行: {btn.text}")
        #                             break
        #                             
        #                 # 4. 等待 Loading 消失
        #                 try:
        #                     self.page.wait.ele_hidden('css:.weui-loading', timeout=3)
        #                 except:
        #                     pass
        #                     
        #             except Exception as e:
        #                 print(f"❌ 核弹点击失败: {e}")
        #
        #             time.sleep(2) # 等待界面刷新
        #         else:
        #             print("⚠️ 弹窗打开了，但没找到图片元素？")
        #             # 兜底逻辑
        #             try:
        #                 self.page.run_js("document.querySelector('.weui-desktop-dialog__ft .weui-desktop-btn_primary').click()")
        #                 print("💥 兜底JS点击已执行")
        #             except:
        #                 pass
        #     else:
        #         # 备用方案：如果上面那招没灵，试着先点一下封面区域
        #         print("⚠️ 没直接找到按钮，尝试点击封面区域触发...")
        #         self.page.ele('css:.js_cover_area').click(by_js=True)
        #         time.sleep(1)
        #         self.page.ele('text:从正文选择').click(by_js=True)
        #
        # except Exception as e:
        #     print(f"❌ 封面设置跳过: {e}")
        #     import traceback
        #     traceback.print_exc()

        # 封面设置完成后暂停，让用户检查
        print("\n" + "="*60)
        print("🔍 [DEBUG] 封面设置流程已完成，请检查浏览器中的封面是否正确设置")
        print("⏰ [DEBUG] 暂停10秒，让您检查...")
        print("="*60 + "\n")
        time.sleep(10)

        # 2. 设置原创 & 完成对话框 (暂时禁用，先测试封面)
        # try:
        #     print("✍️  正在点击原创按钮...")
            # 找到主页面的“原创”按钮，先滚动再点
            # original_label = self.page.ele('text:原创', timeout=3)
            # if original_label:
                # self.page.run_js('arguments[0].scrollIntoView();', original_label)
                # time.sleep(0.5)
                # original_label.click(by_js=True)
                # print("✅ 已触发原创弹窗")
                # time.sleep(2)
                
#                 # --- 弹窗内部操作 ---
                # a. 填写作者 (弹窗内的)
                # author_in_dialog = self.page.ele('css:.claim__original-dialog input[placeholder*="作者"]', timeout=2) or \
                                   # self.page.ele('css:input[placeholder="请输入作者"]', timeout=1)
                # if author_in_dialog:
                    # author_in_dialog.clear()
                    # author_in_dialog.input("AI呈序")

#                 # b. 勾选协议
                # checkbox = self.page.ele('css:.claim__original-dialog .veui-desktop-icon-checkbox', timeout=3) or \
                           # self.page.ele('.veui-desktop-icon-checkbox', timeout=1)
                # if checkbox:
                    # checkbox.click(by_js=True)
                    # print("✅ 已勾选协议")
                    # time.sleep(0.5)
                
#                 
#                 
#                 # c. 点击确定 (关键步骤)
                # 尝试多种定位方式，确保能点到那个绿色的确定按钮
                # 注意：类名是 claim__original-dialog (双下划线)
                # confirm_btn = self.page.ele('css:.claim__original-dialog button.weui-desktop-btn_primary', timeout=2) or \
                              # self.page.ele('css:.weui-desktop-dialog__ft button.weui-desktop-btn_primary', timeout=1) or \
                              # self.page.ele('text=确定', timeout=1)
                
#                 # if confirm_btn:
                    # print(f"⚡️ 正在强制点亮'确定'按钮...")
                    # 先滚动，防止被遮挡
                    # self.page.run_js('arguments[0].scrollIntoView();', confirm_btn)
                    # 使用 JS 强制点击，确保即使按钮被认为“不可见”也能点中
                    # confirm_btn.click(by_js=True)
                    # print("🎉 原创声明已提交完毕！")
                # else:
                    # print("❌ 没找到原创对话框里的'确定'按钮")
        # except Exception as e:
            # print(f"⚠️ 原创设置流程异常: {e}")

        
            
        print("💡 文章辅助设置（封面/原创）已尝试触发，请在浏览器中进行最后的检查和微调")
            
        print(f"✅ 填充操作结束")
    
    def save_draft(self) -> bool:
        """
        自动保存草稿
        点击页面上的"保存草稿"或"存草稿"按钮
        """
        print("💾 正在自动保存草稿...")
        
        try:
            # 等待页面稳定
            time.sleep(2)
            
            # 尝试多种方式找到保存按钮
            save_btn = None
            
            # 方法1：通过文本查找
            btn_texts = ['保存为草稿', '保存草稿', '存草稿', '保存']
            for text in btn_texts:
                try:
                    btn = self.page.ele(f'text:{text}', timeout=2)
                    if btn and btn.states.is_displayed:
                        # 排除"保存并群发"等按钮
                        if '群发' not in (btn.text or '') and '发布' not in (btn.text or ''):
                            save_btn = btn
                            print(f"   ✅ 找到保存按钮: 【{btn.text}】")
                            break
                except:
                    continue
            
            # 方法2：通过 CSS 类名查找（微信后台常用）
            if not save_btn:
                try:
                    # 查找工具栏中的次要按钮（通常是保存草稿）
                    btns = self.page.eles('css:.weui-desktop-btn_default', timeout=2)
                    for btn in btns:
                        text = btn.text.strip() if btn.text else ""
                        if '草稿' in text or text == '保存':
                            save_btn = btn
                            print(f"   ✅ 通过CSS找到保存按钮: 【{text}】")
                            break
                except:
                    pass
            
            # 方法3：查找顶部工具栏的保存按钮
            if not save_btn:
                try:
                    toolbar = self.page.ele('css:.editor-toolbar', timeout=2) or \
                              self.page.ele('css:.appmsg_editor_toolbar', timeout=1)
                    if toolbar:
                        btns = toolbar.eles('tag:button')
                        for btn in btns:
                            text = btn.text.strip() if btn.text else ""
                            if '草稿' in text:
                                save_btn = btn
                                print(f"   ✅ 在工具栏找到保存按钮: 【{text}】")
                                break
                except:
                    pass
            
            if save_btn:
                # 点击保存按钮
                try:
                    save_btn.click()
                except:
                    try:
                        self.page.run_js('arguments[0].click()', save_btn)
                    except:
                        pass
                
                print("   💾 已点击保存按钮...")
                time.sleep(3)
                
                # 检查是否有确认弹窗
                try:
                    confirm_btn = self.page.ele('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=3)
                    if confirm_btn and confirm_btn.states.is_displayed:
                        confirm_text = confirm_btn.text.strip() if confirm_btn.text else ""
                        if confirm_text in ['确定', '确认', '保存']:
                            confirm_btn.click()
                            print(f"   ✅ 确认保存: 【{confirm_text}】")
                            time.sleep(2)
                except:
                    pass
                
                # 检查保存成功的提示
                try:
                    success_tip = self.page.ele('text:保存成功', timeout=3) or \
                                  self.page.ele('text:已保存', timeout=1)
                    if success_tip:
                        print("   🎉 草稿保存成功！")
                        return True
                except:
                    pass
                
                print("   ✅ 保存操作已执行（请在浏览器中确认）")
                return True
            else:
                print("   ⚠️ 未找到保存草稿按钮，请手动保存")
                return False
                
        except Exception as e:
            print(f"   ❌ 保存草稿失败: {e}")
            return False
    
    def post(self):
        """执行完整的发布流程"""
        try:
            # 1. 检查登录状态
            if not self.check_login():
                # 2. 等待扫码登录
                self.wait_for_login()
            
            # 3. 加载内容
            title, content_body = self.load_text_content()
            
            if not title or not content_body:
                print(f"⏭️  账号 {self.account_name} 无发布内容，已跳过。")
                return
            
            # 4. 创建新草稿
            self.create_new_draft()
            
            # 5. 填充内容
            self.fill_content(title, content_body)
            
            # 6. 自动保存草稿
            self.save_draft()
            
            # 7. 点击发表
            self.publish_article()
            
            print(f"\n{'='*60}")
            print(f"✨ 自动发布流程完成！")
            print(f"📝 文章标题: {title}")
            print(f"🚀 文章已发表！")
            print(f"{'='*60}\n")
            
            # 给用户3秒时间查看结果，然后自动退出
            print(f"💡 浏览器将保持打开状态，3秒后程序自动退出...")
            time.sleep(3)
            print(f"👋 程序已完成，退出中...")
                
        except Exception as e:
            print(f"\n❌ 发布失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def publish_article(self) -> bool:
        """点击发表按钮发布文章"""
        print("\n🚀 正在点击发表...")
        
        try:
            time.sleep(2)
            
            # 查找发表按钮 - 搜索所有按钮
            publish_btn = None
            
            # 方法1：搜索所有按钮
            try:
                all_buttons = self.page.eles('tag:button', timeout=3)
                for btn in all_buttons:
                    try:
                        if btn.states.is_displayed:
                            btn_text = btn.text.strip() if btn.text else ""
                            if btn_text == "发表":
                                publish_btn = btn
                                print(f"   ✅ 找到发表按钮: 【{btn_text}】")
                                break
                    except:
                        continue
            except:
                pass
            
            # 方法2：通过 class 搜索
            if not publish_btn:
                try:
                    primary_btns = self.page.eles('css:.weui-desktop-btn_primary', timeout=2)
                    for btn in primary_btns:
                        try:
                            if btn.states.is_displayed:
                                btn_text = btn.text.strip() if btn.text else ""
                                if btn_text == "发表":
                                    publish_btn = btn
                                    print(f"   ✅ 通过class找到发表按钮: 【{btn_text}】")
                                    break
                        except:
                            continue
                except:
                    pass
            
            if publish_btn:
                try:
                    publish_btn.click(by_js=True)
                except:
                    try:
                        self.page.run_js('arguments[0].click()', publish_btn)
                    except:
                        self.page.run_js('''
                            var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                            arguments[0].dispatchEvent(evt);
                        ''', publish_btn)
                
                print("   📤 已点击发表按钮...")
                time.sleep(3)
                
                # 处理发表确认弹窗（可能有多个）
                print("   📍 处理发表确认弹窗...")
                
                for attempt in range(5):
                    # 用户修正：在第2次找弹窗按钮前（attempt=1），再次点击一次主界面的发表按钮
                    if attempt == 1:
                        print("   🔄 第2次尝试前，再次点击主界面'发表'按钮...")
                        try:
                            # 重新查找发表按钮（防止页面刷新元素失效）
                            primary_btns = self.page.eles('css:.weui-desktop-btn_primary', timeout=2)
                            for btn in primary_btns:
                                if btn.states.is_displayed and btn.text.strip() == "发表":
                                    btn.click(by_js=True)
                                    print("   ✅ 再次点击'发表'成功")
                                    time.sleep(2)
                                    break
                        except Exception as e:
                            print(f"   ⚠️ 再次点击'发表'失败: {e}")

                    time.sleep(2)
                    
                    # 查找弹窗内的按钮 - 优先查找 dialog 内的按钮
                    target_btn = None
                    
                    # 优先查找"无需声明并发表"
                    try:
                        no_declare_btn = self.page.ele('text:无需声明并发表', timeout=2)
                        if no_declare_btn and no_declare_btn.states.is_displayed:
                            target_btn = no_declare_btn
                            print(f"   ✅ 找到: 【无需声明并发表】")
                    except:
                        pass
                    
                    # 查找"继续发表"按钮（在 double_check_dialog 内）
                    if not target_btn:
                        try:
                            continue_btn = self.page.ele('text:继续发表', timeout=2)
                            if continue_btn and continue_btn.states.is_displayed:
                                target_btn = continue_btn
                                print(f"   ✅ 找到: 【继续发表】")
                        except:
                            pass
                    
                    # 查找弹窗 dialog 内的"发表"按钮（排除工具栏）
                    if not target_btn:
                        try:
                            # 优先从 double_check_dialog 或 weui-desktop-dialog 内查找
                            dialogs = self.page.eles('css:.weui-desktop-dialog', timeout=2)
                            for dialog in dialogs:
                                try:
                                    if dialog.states.is_displayed:
                                        btns = dialog.eles('css:.weui-desktop-btn_primary')
                                        for btn in btns:
                                            if btn.states.is_displayed:
                                                btn_text = btn.text.strip() if btn.text else ""
                                                if btn_text in ["发表", "继续发表", "确定", "确认"]:
                                                    target_btn = btn
                                                    print(f"   ✅ 找到弹窗内: 【{btn_text}】")
                                                    break
                                        if target_btn:
                                            break
                                except:
                                    continue
                        except:
                            pass
                    
                    if target_btn:
                        try:
                            target_btn.click(by_js=True)
                            print(f"   ✅ 点击成功!")
                            time.sleep(2)
                        except Exception as e:
                            try:
                                self.page.run_js('arguments[0].click()', target_btn)
                                print(f"   ✅ JS点击成功!")
                                time.sleep(2)
                            except:
                                print(f"   ⚠️ 点击失败: {e}")
                    else:
                        print(f"   第{attempt+1}次: 未找到可点击的弹窗按钮")
                        # 检查是否已完成（没有弹窗了）
                        try:
                            dialog = self.page.ele('css:.weui-desktop-dialog', timeout=1)
                            if not dialog or not dialog.states.is_displayed:
                                print("   ✅ 弹窗已关闭，发表可能已完成")
                                break
                        except:
                            break
                
                print("   🎉 发表操作完成！")
                return True
            else:
                print("   ⚠️ 未找到发表按钮")
                return False
                
        except Exception as e:
            print(f"   ❌ 发表失败: {e}")
            return False
    
    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.quit()
            print(f"👋 浏览器已关闭")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="微信公众号自动发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 为指定账号发布内容
  python wechat_auto_post.py --account Account_A_CrossBorder
  
  # 使用无头模式（后台运行）
  python wechat_auto_post.py --account Account_A_CrossBorder --headless

注意事项:
  1. 首次使用需要扫码登录
  2. 登录信息会保存在 .browser_data 目录中
  3. 确保已经生成了 output.txt 文件
        """
    )
    
    parser.add_argument(
        "--account",
        type=str,
        required=True,
        help="账号名称（如：Account_A_CrossBorder）"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="使用无头模式（不显示浏览器窗口）"
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"--- 微信公众号自动发布工具 ---")
    print(f"ACCOUNT: {args.account}")
    print(f"{'='*60}\n")
    
    # 创建发布器并执行
    poster = WeChatAutoPoster(args.account, headless=args.headless)
    
    try:
        poster.post()
    finally:
        # 不自动关闭浏览器，让用户检查内容
        pass


if __name__ == "__main__":
    main()
