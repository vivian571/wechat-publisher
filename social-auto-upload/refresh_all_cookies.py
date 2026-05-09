"""
一键重新获取所有平台 Cookie 的脚本
使用方法: python refresh_all_cookies.py
"""
import asyncio
import sqlite3
from pathlib import Path
from playwright.async_api import async_playwright

# 导入项目配置
import sys
sys.path.insert(0, str(Path(__file__).parent))

from conf import BASE_DIR, LOCAL_CHROME_HEADLESS
from utils.base_social_media import set_init_script

# 平台配置
PLATFORMS = {
    1: {
        "name": "小红书",
        "url": "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=video",
        "check_text": ["手机号登录", "扫码登录"]
    },
    2: {
        "name": "视频号",
        "url": "https://channels.weixin.qq.com/platform/post/create",
        "check_text": ["微信小店"]
    },
    3: {
        "name": "抖音",
        "url": "https://creator.douyin.com/creator-micro/content/upload",
        "check_text": ["扫码登录"]
    },
    4: {
        "name": "快手",
        "url": "https://cp.kuaishou.com/article/publish/video",
        "check_text": ["机构服务"]
    }
}

async def refresh_cookie(account_id, platform_type, cookie_file, username):
    """刷新单个账号的 Cookie"""
    platform = PLATFORMS.get(platform_type)
    if not platform:
        print(f"⚠️  未知平台类型: {platform_type}")
        return False
    
    cookie_path = Path(BASE_DIR / "cookiesFile" / cookie_file)
    
    print(f"\n{'='*50}")
    print(f"🔄 正在刷新: {platform['name']} - {username}")
    print(f"📁 Cookie 文件: {cookie_file}")
    print(f"{'='*50}\n")
    
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(headless=False)  # 必须显示浏览器
            context = await browser.new_context()
            context = await set_init_script(context)
            page = await context.new_page()
            
            # 访问发布页面
            print(f"📍 正在访问: {platform['url']}")
            await page.goto(platform['url'])
            
            print("\n" + "="*50)
            print("⏸️  浏览器已打开,请按以下步骤操作:")
            print("="*50)
            print("1. 扫码登录或输入账号密码登录")
            print("2. 确认能看到发布界面(不是登录页面)")
            print("3. 在浏览器调试器中点击 '继续' 按钮")
            print("4. 等待 Cookie 自动保存")
            print("="*50 + "\n")
            
            # 暂停,等待用户登录
            await page.pause()
            
            # 保存 Cookie
            await context.storage_state(path=str(cookie_path))
            print(f"\n✅ {platform['name']} - {username} Cookie 已保存!")
            
            await context.close()
            await browser.close()
            return True
            
        except Exception as e:
            print(f"\n❌ {platform['name']} - {username} Cookie 刷新失败: {str(e)}")
            return False

async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🚀 一键刷新所有平台 Cookie")
    print("="*60 + "\n")
    
    # 读取数据库中的所有账号
    db_path = Path(BASE_DIR / "db" / "database.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, filePath, userName FROM user_info WHERE status = 1")
    accounts = cursor.fetchall()
    conn.close()
    
    if not accounts:
        print("⚠️  没有找到需要刷新的账号")
        return
    
    print(f"📋 找到 {len(accounts)} 个账号需要刷新:\n")
    for idx, (account_id, platform_type, cookie_file, username) in enumerate(accounts, 1):
        platform_name = PLATFORMS.get(platform_type, {}).get("name", "未知平台")
        print(f"  {idx}. {platform_name} - {username}")
    
    print("\n" + "="*60)
    choice = input("是否刷新所有账号? (y/n): ").strip().lower()
    
    if choice != 'y':
        print("❌ 已取消")
        return
    
    # 逐个刷新
    success_count = 0
    for account_id, platform_type, cookie_file, username in accounts:
        result = await refresh_cookie(account_id, platform_type, cookie_file, username)
        if result:
            success_count += 1
        
        # 等待用户准备下一个账号
        if account_id != accounts[-1][0]:  # 不是最后一个账号
            input("\n按回车键继续刷新下一个账号...")
    
    print("\n" + "="*60)
    print(f"✅ 完成! 成功刷新 {success_count}/{len(accounts)} 个账号")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
