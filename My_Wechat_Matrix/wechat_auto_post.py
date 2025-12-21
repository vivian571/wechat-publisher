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
from pathlib import Path
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
        """
        cover_patterns = ['cover_fixed.*', 'cover.*', 'Cover.*', '封面.*']
        
        for pattern in cover_patterns:
            matches = list(self.account_dir.glob(pattern))
            for match in matches:
                if match.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                    print(f"📷 找到封面图片: {match.name}")
                    return str(match)
        
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
        
        # 设置用户数据目录以保持登录状态
        user_data_dir = self.base_dir / ".browser_data"
        user_data_dir.mkdir(exist_ok=True)
        co.set_user_data_path(str(user_data_dir))
        
        # 设置无头模式
        if headless:
            co.headless()
        
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
            # === 方法1：最稳的 URL 检测 ===
            # 只要网址里包含 'cgi-bin/home'，说明绝对进去了
            if "cgi-bin/home" in self.page.url:
                print(f"✅ 检测到后台主页 URL，登录成功！")
                # 给一点时间让页面元素加载完
                time.sleep(3)
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
        

    
    def load_html_content(self) -> tuple[str, str]:
        """
        加载 HTML 内容
        
        Returns:
            (title, html_body): 标题和HTML正文内容
        """
        html_file = self.account_dir / "output.html"
        
        if not html_file.exists():
            raise FileNotFoundError(
                f"未找到 output.html 文件: {html_file}\n"
                f"请先运行: python generator.py --account {self.account_name}"
            )
        
        print(f"📄 正在读取内容: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取标题（第一个 h1 标签）
        title_tag = soup.find('h1')
        title = title_tag.get_text().strip() if title_tag else "未命名文章"
        
        # 提取正文内容（js_content div 中的内容）
        content_div = soup.find('div', id='js_content')
        if content_div:
            html_body = str(content_div)
        else:
            # 如果没有 js_content，使用 body 中的内容
            body = soup.find('body')
            html_body = str(body) if body else html_content
        
        print(f"✅ 标题: {title}")
        print(f"✅ 内容长度: {len(html_body)} 字符")
        
        return title, html_body
    
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
            # 观察截图，"文章" 是普通的 publish，createType=1
            editor_url = f"https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=1&token={token}&lang=zh_CN"
            # 注意：type=77 是普通文章（非图文消息），createType=1
            # 如果不行，还是回退到点击按钮
            
            print(f"🔗 尝试访问文章编辑器: {editor_url}")
            self.page.get(editor_url)
            time.sleep(5) 

        
        print(f"✅ 已尝试打开编辑器页面")
    
    def fill_content(self, title_text: str, html_content: str):
        """
        填充内容到编辑器 (针对 2024/2025 新版 Mock-Iframe 编辑器)
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

        # 2. 填写正文 (针对模拟 Iframe 的 div 注入)
        try:
            print("⚡️ 正在尝试定位模拟 Iframe 正文区域...")
            
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
                # 处理 HTML 字符转义
                safe_html = html_content.replace('`', '\\`').replace('\\', '\\\\')
                
                # 直接通过 JS 注入 innerHTML
                css_selector = target_ele.css_path
                js_code = f"""
                var editor = document.querySelector('{css_selector}');
                if (editor) {{
                    editor.innerHTML = `{safe_html}`;
                    // 触发 input 事件通知编辑器内容已更新
                    editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
                """
                self.page.run_js(js_code)
                print("🎉 正文内容注入成功！")
                
                # === 处理封面、原创、创作来源 ===
                self._handle_additional_settings(title_text)
                
            else:
                print("❌ 无法定位正文区域。")
                
        except Exception as e:
            print(f"❌ 注入正文时发生异常: {e}")
            
        print(f"✅ 填充操作结束")

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
        """处理封面、原创和创作来源设置 (两阶段封面上传法)"""
        print("🛠️  正在处理文章设置（封面、原创、来源）...")
        
        # ==========================================
        # 🖼️ 两阶段封面设置法（避免转圈问题）
        # 阶段一：先上传到素材库
        # 阶段二：从图片库选择
        # ==========================================
        try:
            print("🖼️ 正在设置封面（两阶段法）...")
            
            # 检查是否有本地封面图片
            if self.cover_image_path:
                # 预处理封面（确保比例正确）
                processed_cover = self._preprocess_cover_image(self.cover_image_path)
                print(f"📁 使用封面图片: {processed_cover}")
                
                # 阶段二：从图片库选择封面
                self._stage2_select_from_library()
            else:
                print("⚠️ 未找到本地封面图片，跳过封面设置")
                print("   提示：请在账号目录放置 cover.jpg 或 cover.png 文件")

        except Exception as e:
            print(f"❌ 封面设置跳过: {e}")
            import traceback
            traceback.print_exc()
    
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
    
    def _stage2_select_from_library(self) -> bool:
        """
        封面设置：直接上传本地文件
        避免使用"从图片库选择"以绕过微信的反自动化检测
        """
        print("\n🎯 === 封面设置：直接上传 ===")
        
        # 🐛 调试模式
        DEBUG_MODE = True
        
        def debug_wait(step_name: str):
            if DEBUG_MODE:
                print(f"\n🐛 [调试模式] {step_name} 完成，等待10秒供观察...")
                for i in range(10, 0, -1):
                    print(f"   倒计时: {i}秒", end='\r')
                    time.sleep(1)
                print("\n   继续执行下一步...")
        
        try:
            if not self.cover_image_path:
                print("❌ 没有封面图片路径")
                return False
            
            # ========================================
            # 步骤1: 点击封面区域，打开弹窗
            # ========================================
            print("📍 步骤1: 点击封面区域...")
            
            cover_btn = self.page.ele('text:选择封面', timeout=3)
            if not cover_btn:
                cover_btn = self.page.ele('css:.js_cover_area', timeout=2)
            if not cover_btn:
                cover_btn = self.page.ele('text:拖拽或选择封面', timeout=2)
            
            if cover_btn:
                cover_btn.click()
                print("   ✅ 已点击封面区域，弹窗应该已打开")
                time.sleep(3)  # 等待弹窗完全加载
                debug_wait("步骤1: 点击封面区域")
            else:
                print("   ❌ 未找到封面区域")
                return False
            
            # ========================================
            # 步骤2: 直接通过 input[type="file"] 上传
            # 不切换标签，避免触发微信检测
            # ========================================
            print("📍 步骤2: 直接上传文件...")
            
            # 找到所有file input
            file_inputs = self.page.eles('css:input[type="file"]', timeout=5)
            print(f"   找到 {len(file_inputs) if file_inputs else 0} 个文件上传入口")
            
            # 打印每个input的详细信息
            for idx, inp in enumerate(file_inputs if file_inputs else []):
                try:
                    inp_id = inp.attr('id') or '无'
                    inp_name = inp.attr('name') or '无'
                    inp_class = inp.attr('class') or '无'
                    print(f"   Input {idx + 1}: id='{inp_id}', name='{inp_name}', class='{inp_class}'")
                except:
                    pass
            
            upload_success = False
            for idx, file_input in enumerate(file_inputs if file_inputs else []):
                try:
                    print(f"\n   尝试使用第 {idx + 1} 个input上传...")
                    file_input.input(self.cover_image_path)
                    print(f"   ✅ 文件路径已注入: {self.cover_image_path}")
                    
                    # 手动触发change事件
                    try:
                        self.page.run_js("arguments[0].dispatchEvent(new Event('change', { bubbles: true }))", file_input)
                        print("   触发了change事件")
                    except:
                        pass
                    
                    time.sleep(3)  #等待响应
                    
                    # 检查是否出现了图片预览
                    preview = self.page.ele('css:img[src*="blob:"]', timeout=2)
                    if preview:
                        print("   ✅ 检测到图片预览！上传成功")
                        upload_success = True
                        time.sleep(2)
                        debug_wait("步骤2: 上传文件")
                        break
                    else:
                        print(f"   ⚠️ 第 {idx + 1} 个input未产生预览，尝试下一个...")
                except Exception as e:
                    print(f"   第 {idx + 1} 个input失败: {e}")
                    continue
            
            if not upload_success:
                print("   ❌ 所有input都上传失败")
                return False
            
            # ========================================
            # 步骤3: 点击确认按钮（可能有多次）
            # ========================================
            print("📍 步骤3: 处理后续确认...")
            
            for attempt in range(5):
                time.sleep(2)
                
                # 找确认按钮，过滤干扰项
                confirm_btn = None
                btns = self.page.eles('css:.weui-desktop-dialog__ft .weui-desktop-btn_primary', timeout=3)
                for btn in btns:
                    btn_text = btn.text.strip() if btn.text else ""
                    # 过滤干扰按钮
                    if btn_text in ["退出登录", "换风格", "前往实名", "取消", "关闭"]:
                        continue
                    # 接受这些按钮
                    if btn_text in ["下一步", "确定", "完成"] and btn.states.is_displayed:
                        confirm_btn = btn
                        break
                
                if confirm_btn:
                    btn_text = confirm_btn.text.strip()
                    print(f"   第{attempt + 1}次确认: 点击【{btn_text}】...")
                    try:
                        confirm_btn.click()
                    except:
                        try:
                            self.page.run_js('arguments[0].click()', confirm_btn)
                        except:
                            pass
                    
                    if DEBUG_MODE and attempt == 0:
                        debug_wait(f"步骤3: 第一次确认({btn_text})")
                else:
                    print(f"   第{attempt + 1}次: 未找到确认按钮，可能已完成")
                    break
            
            print("🎉 封面设置流程完成！")
            return True
            
        except Exception as e:
            print(f"❌ 封面设置失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _try_direct_upload(self):
        """尝试直接通过 input[type=file] 上传封面"""
        try:
            if self.cover_image_path:
                file_input = self.page.ele('css:input[type="file"]', timeout=3)
                if file_input:
                    print(f"📤 尝试直接上传: {self.cover_image_path}")
                    file_input.input(self.cover_image_path)
                    time.sleep(5)
                    self._click_confirm_physical()
        except Exception as e:
            print(f"⚠️ 直接上传失败: {e}")
    
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
    
    def post(self):
        """执行完整的发布流程"""
        try:
            # 1. 检查登录状态
            if not self.check_login():
                # 2. 等待扫码登录
                self.wait_for_login()
            
            # 3. 加载内容
            title, html_body = self.load_html_content()
            
            # 4. 创建新草稿
            self.create_new_draft()
            
            # 5. 填充内容
            self.fill_content(title, html_body)
            
            print(f"\n{'='*60}")
            print(f"✨ 自动发布流程完成！")
            print(f"📝 文章标题: {title}")
            print(f"💡 请在浏览器中检查内容，确认无误后点击保存")
            print(f"{'='*60}\n")
            
            # 保持浏览器打开，让用户检查
            print(f"💡 浏览器将保持打开状态，按 Ctrl+C 退出...")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n👋 退出程序")
                
        except Exception as e:
            print(f"\n❌ 发布失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
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
  3. 确保已经生成了 output.html 文件
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
    print(f"🚀 微信公众号自动发布工具")
    print(f"📱 账号: {args.account}")
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
