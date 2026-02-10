import asyncio
import sys
from playwright.async_api import async_playwright

async def test():
    print("Testing Playwright...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.baidu.com")
            title = await page.title()
            print(f"Success! Page title: {title}")
            await browser.close()
    except Exception as e:
        print(f"Playwright failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
