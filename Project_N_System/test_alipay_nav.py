"""
测试脚本 - 验证支付宝消息定位功能
"""

import time
import os
from skills.eye_v2 import EyeCore
from skills.brain_v2 import BrainCore
from skills.hand_v2 import HandCore

def test_alipay_navigation():
    print("=== 测试支付宝消息定位功能 ===\n")
    
    eye = EyeCore()
    brain = BrainCore()
    hand = HandCore()
    
    # 1. 启动支付宝
    print("1. 启动支付宝...")
    os.system("adb shell am start -n com.eg.android.AlipayGphone/.AlipayLogin")
    time.sleep(3)
    
    # 2. 截图并识别
    print("\n2. 截图并识别屏幕文字...")
    img_path = eye.capture()
    texts = brain.analyze_screen(img_path)
    
    print(f"   识别到 {len(texts)} 个文本区域")
    
    # 3. 查找"消息"标签
    print("\n3. 查找'消息'标签...")
    message_pos = brain.find_keyword(texts, "消息")
    
    if message_pos:
        print(f"   ✅ 找到'消息'标签位置: {message_pos}")
        
        # 询问是否点击
        print("\n是否点击'消息'标签? (y/n)")
        # choice = input().lower()
        # if choice == 'y':
        #     hand.tap(message_pos[0], message_pos[1])
        #     print("   已点击!")
    else:
        print("   ❌ 未找到'消息'标签")
        print("\n   识别到的文字:")
        for item in texts[:10]:
            print(f"     - {item['text']}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_alipay_navigation()
