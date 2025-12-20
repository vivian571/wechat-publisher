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
        
        # 初始化浏览器
        self.page = self._init_browser(headless)
        
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
        co.set_window_size(1400, 900)
        
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
        等待用户扫码登录
        
        Args:
            timeout: 超时时间（秒），默认5分钟
        """
        print(f"📱 请使用微信扫描二维码登录...")
        print(f"⏱️  等待时间: {timeout}秒")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 检查是否已登录
            try:
                menu = self.page.ele("css:.weui-desktop-menu__list", timeout=2)
                if menu:
                    print(f"✅ 登录成功！")
                    time.sleep(2)  # 等待页面完全加载
                    return True
            except:
                pass
            
            # 每2秒检查一次
            time.sleep(2)
            
            # 显示倒计时
            remaining = int(timeout - (time.time() - start_time))
            if remaining % 10 == 0:
                print(f"⏱️  剩余时间: {remaining}秒")
        
        raise TimeoutError(f"登录超时（{timeout}秒）")
    
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
        
        # 点击左侧菜单的"内容管理"或"素材管理"
        try:
            # 尝试找到"内容管理"菜单
            content_menu = self.page.ele("text:内容管理", timeout=5)
            content_menu.click()
            time.sleep(2)
        except:
            print(f"⚠️  未找到'内容管理'菜单，尝试直接访问草稿箱...")
        
        # 直接访问草稿箱页面
        self.page.get("https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=10&token=&lang=zh_CN")
        time.sleep(3)
        
        print(f"✅ 已打开编辑器页面")
    
    def fill_content(self, title: str, html_body: str):
        """
        填充内容到编辑器
        
        Args:
            title: 文章标题
            html_body: HTML正文内容
        """
        print(f"✍️  正在填充内容...")
        
        # 填写标题
        try:
            title_input = self.page.ele("css:#js_appmsg_title", timeout=5)
            title_input.clear()
            title_input.input(title)
            print(f"✅ 标题已填写")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️  填写标题失败: {e}")
        
        # 填充正文内容
        try:
            # 微信编辑器使用 iframe
            # 先切换到编辑器 iframe
            iframe = self.page.ele("css:#ueditor_0", timeout=5)
            
            if iframe:
                # 使用 JavaScript 设置内容
                # 微信使用 UEditor，可以通过 JavaScript 设置内容
                # 先处理反引号转义，避免在 f-string 中使用反斜杠
                escaped_html = html_body.replace('`', '\\`')
                js_code = f"""
                var editor = UE.getEditor('editor');
                editor.ready(function() {{
                    editor.setContent(`{escaped_html}`);
                }});
                """
                
                self.page.run_js(js_code)
                print(f"✅ 正文内容已填充（通过 JavaScript）")
                time.sleep(2)
            else:
                print(f"⚠️  未找到编辑器 iframe")
                
        except Exception as e:
            print(f"⚠️  填充正文失败: {e}")
            print(f"💡 提示: 您可能需要手动粘贴内容")
        
        print(f"✅ 内容填充完成！")
        print(f"💡 请检查内容格式，确认无误后点击保存")
    
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
