"""
封面上传调试脚本 - 每一步截图并保存
用于分析自动化点击失败的问题
"""
import os
import time
from datetime import datetime
from DrissionPage import ChromiumPage

class CoverUploadDebugger:
    """封面上传调试器 - 每步截图"""
    
    def __init__(self, account_name: str):
        self.account_name = account_name
        self.step_count = 0
        
        # 创建截图目录
        self.screenshot_dir = f"debug_screenshots/{account_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(self.screenshot_dir, exist_ok=True)
        print(f"📸 截图保存目录: {self.screenshot_dir}")
        
        # 连接已打开的浏览器
        self.page = ChromiumPage()
        
    def screenshot(self, step_name: str):
        """截图并保存"""
        self.step_count += 1
        filename = f"{self.step_count:02d}_{step_name}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        try:
            self.page.get_screenshot(filepath)
            print(f"📸 [{self.step_count}] 截图已保存: {filename}")
        except Exception as e:
            print(f"❌ 截图失败: {e}")
        
        return filepath
    
    def debug_cover_upload(self):
        """调试封面上传流程"""
        print("\n" + "="*60)
        print("🔍 开始调试封面上传流程")
        print("="*60 + "\n")
        
        # Step 1: 初始状态
        self.screenshot("01_初始状态")
        time.sleep(1)
        
        # Step 2: 查找封面按钮
        print("\n📌 Step 2: 查找封面按钮...")
        cover_btn = self.page.ele('css:div[class*="cover"][class*="btn"]', timeout=5)
        if cover_btn:
            print(f"   ✅ 找到封面按钮")
            self.screenshot("02_找到封面按钮")
            
            # Step 3: 点击封面按钮
            print("\n📌 Step 3: 点击封面按钮...")
            cover_btn.click(by_js=True)
            time.sleep(2)
            self.screenshot("03_点击封面按钮后")
            
            # Step 4: 查找AI配图按钮
            print("\n📌 Step 4: 查找AI配图按钮...")
            ai_btn = self.page.ele('text:AI', timeout=3)
            if ai_btn and 'AI' in ai_btn.text:
                print(f"   ✅ 找到AI配图按钮: {ai_btn.text}")
                self.screenshot("04_找到AI配图按钮")
                
                # Step 5: 点击AI配图按钮
                print("\n📌 Step 5: 点击AI配图按钮...")
                ai_btn.click(by_js=True)
                time.sleep(3)
                self.screenshot("05_点击AI配图后")
                
                # Step 6: 查找输入框
                print("\n📌 Step 6: 查找输入框...")
                input_box = self.page.ele('css:textarea[placeholder*="描述"]', timeout=3)
                if input_box:
                    print(f"   ✅ 找到输入框")
                    self.screenshot("06_找到输入框")
                    
                    # Step 7: 输入随机字母
                    print("\n📌 Step 7: 输入随机字母...")
                    import random
                    import string
                    letter = random.choice(string.ascii_lowercase)
                    input_box.clear()
                    input_box.input(letter)
                    print(f"   ✅ 输入: {letter}")
                    time.sleep(2)
                    self.screenshot("07_输入字母后")
                    
                    # Step 8: 查找图片容器
                    print("\n📌 Step 8: 查找图片容器...")
                    time.sleep(2)
                    containers = self.page.eles('css:.image-item', timeout=3)
                    if containers:
                        first_container = containers[0]
                        print(f"   ✅ 找到 {len(containers)} 个图片容器")
                        self.screenshot("08_找到图片容器")
                        
                        # Step 9: Hover图片容器
                        print("\n📌 Step 9: Hover图片容器...")
                        first_container.hover()
                        time.sleep(1)
                        self.screenshot("09_hover图片后")
                        
                        # Step 10: 查找插入按钮
                        print("\n📌 Step 10: 查找插入按钮...")
                        insert_btn = self.page.ele('css:.insert-btn', timeout=3)
                        if insert_btn:
                            print(f"   ✅ 找到插入按钮: {insert_btn.text}")
                            self.screenshot("10_找到插入按钮")
                            
                            # Step 11: 尝试多种点击方式
                            print("\n📌 Step 11: 尝试点击插入按钮...")
                            
                            # 方法1: actions点击
                            print("   → 方法1: actions.click()...")
                            try:
                                self.page.actions.click(insert_btn)
                                print("   ✅ actions点击执行完成")
                            except Exception as e:
                                print(f"   ❌ actions点击失败: {e}")
                            
                            time.sleep(2)
                            self.screenshot("11a_actions点击后")
                            
                            # 检查是否弹出预览窗口
                            preview_dialog = self.page.ele('css:.ai_image_fine_tuning_dialog', timeout=2)
                            if preview_dialog:
                                print("   🎉 预览弹窗已出现!")
                                self.screenshot("11b_预览弹窗出现")
                            else:
                                print("   ⚠️ 预览弹窗未出现，尝试其他方法...")
                                
                                # 方法2: 直接click
                                print("   → 方法2: click()...")
                                try:
                                    insert_btn = self.page.ele('css:.insert-btn', timeout=2)
                                    if insert_btn:
                                        insert_btn.click()
                                        print("   ✅ 直接点击执行完成")
                                except Exception as e:
                                    print(f"   ❌ 直接点击失败: {e}")
                                
                                time.sleep(2)
                                self.screenshot("11c_直接点击后")
                                
                                # 方法3: JS点击
                                print("   → 方法3: click(by_js=True)...")
                                try:
                                    insert_btn = self.page.ele('css:.insert-btn', timeout=2)
                                    if insert_btn:
                                        insert_btn.click(by_js=True)
                                        print("   ✅ JS点击执行完成")
                                except Exception as e:
                                    print(f"   ❌ JS点击失败: {e}")
                                
                                time.sleep(2)
                                self.screenshot("11d_JS点击后")
                                
                                # 方法4: 使用JavaScript触发点击事件
                                print("   → 方法4: 使用dispatchEvent触发click...")
                                try:
                                    insert_btn = self.page.ele('css:.insert-btn', timeout=2)
                                    if insert_btn:
                                        self.page.run_js("""
                                            var event = new MouseEvent('click', {
                                                view: window,
                                                bubbles: true,
                                                cancelable: true
                                            });
                                            arguments[0].dispatchEvent(event);
                                        """, insert_btn)
                                        print("   ✅ dispatchEvent执行完成")
                                except Exception as e:
                                    print(f"   ❌ dispatchEvent失败: {e}")
                                
                                time.sleep(2)
                                self.screenshot("11e_dispatchEvent后")
                            
                            # Step 12: 最终状态
                            self.screenshot("12_最终状态")
                            
                        else:
                            print("   ❌ 未找到插入按钮")
                            self.screenshot("10_未找到插入按钮")
                    else:
                        print("   ❌ 未找到图片容器")
                        self.screenshot("08_未找到图片容器")
                else:
                    print("   ❌ 未找到输入框")
            else:
                print("   ❌ 未找到AI配图按钮")
        else:
            print("   ❌ 未找到封面按钮")
        
        print("\n" + "="*60)
        print(f"🔍 调试完成！截图保存在: {self.screenshot_dir}")
        print("="*60 + "\n")


def main():
    """运行调试器"""
    import argparse
    parser = argparse.ArgumentParser(description='封面上传调试器')
    parser.add_argument('--account', type=str, default='Account_A_CrossBorder', help='账号名称')
    args = parser.parse_args()
    
    debugger = CoverUploadDebugger(args.account)
    debugger.debug_cover_upload()


if __name__ == "__main__":
    main()
