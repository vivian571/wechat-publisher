from DrissionPage import ChromiumPage, ChromiumOptions
import time

try:
    print("正在启动浏览器 (无头模式)...")
    co = ChromiumOptions()
    co.headless()
    page = ChromiumPage(co)
    print("浏览器已启动，正在访问 example.com...")
    page.get("https://example.com")
    print(f"页面标题: {page.title}")
    page.quit()
    print("测试成功！")
except Exception as e:
    print(f"测试失败: {e}")
