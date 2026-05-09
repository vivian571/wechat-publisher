#!/usr/bin/env python

import asyncio
from playwright.async_api import async_playwright

async def main():
    """
    演示如何使用 Playwright 启动浏览器并访问网页。
    """
    print("正在启动 Playwright 浏览器...")
    
    async with async_playwright() as p:
        # 启动一个 Chromium 浏览器实例
        # headless=False 表示显示浏览器窗口
        browser = await p.chromium.launch(headless=False)
        
        # 创建一个新的浏览器页面
        page = await browser.new_page()
        
        print("浏览器已启动，正在打开网页...")
        
        # 导航到指定的 URL，并增加超时时间
        print("正在导航到抖音首页，请稍候...")
        await page.goto("https://www.douyin.com", timeout=60000)  # 超时时间设置为60秒

        print("页面加载中，正在等待关键元素出现...")
        # 等待页面上的Logo元素出现，这是一个更可靠的判断方式
        await page.wait_for_selector('//a[@aria-label="抖音"]', timeout=60000)
        
        print("网页加载完成，关键元素已出现。")
        print("浏览器窗口将保持打开状态，您可以手动操作。")
        print("关闭浏览器窗口后，脚本将自动退出。")
        
        # 等待页面关闭
        await page.wait_for_event("close")
        
        # 关闭浏览器
        await browser.close()
        
        print("浏览器已关闭，脚本执行完毕。")

if __name__ == "__main__":
    asyncio.run(main())
