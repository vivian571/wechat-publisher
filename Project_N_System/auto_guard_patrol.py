import time
import os
from skills.eye_v2 import EyeCore
from skills.brain_v2 import BrainCore
from skills.hand_v2 import HandCore
from skills.keyboard import KeyboardCore

def open_alipay_chat(eye, brain, hand):
    """智能打开支付宝消息列表"""
    print("🚀 正在启动支付宝...")
    
    # 启动支付宝主页
    os.system("adb shell am start -n com.eg.android.AlipayGphone/.AlipayLogin")
    time.sleep(3)
    
    # 使用 OCR 找到"消息"标签并点击
    print("🔍 正在定位'消息'标签...")
    img_path = eye.capture()
    texts = brain.analyze_screen(img_path)
    
    # 寻找"消息"文字
    message_pos = brain.find_keyword(texts, "消息")
    if message_pos:
        print(f"📱 点击消息标签 @ {message_pos}")
        hand.tap(message_pos[0], message_pos[1])
        time.sleep(2)
        return True
    else:
        print("⚠️ 未找到'消息'标签,可能已经在消息页面")
        return True

 

def main():
    eye = EyeCore()
    brain = BrainCore()
    hand = HandCore()
    keyboard = KeyboardCore()

    # --- 🔒 以安的专属配置区 ---
    TARGET_NAME = "欠我钱和抚养费"  # ⚠️ 记得改成他在你支付宝里的备注名
    REPLY_TEXT = "【系统代理回复】请仅在此处交流孩子必要信息，其余内容已自动拦截。"
    
    # 你实测的两个“小飞机”坐标
    SEND_NORMAL = (1124, 2380)   # 没表情包时的位置
    SEND_EMOJI = (1142, 1175)    # 弹出表情包时的位置

    print("🛡️ [SocialGuard v4.0] 巡逻模式已就绪，以安你可以去休息了。")
    
    try:
        while True:
            # 1. 截屏并分析
            img_path = eye.capture()
            texts = brain.analyze_screen(img_path)
            full_text = "".join([t['text'] for t in texts])
            
            # 2. 检查是否有新消息提示
            if "支付宝" in full_text:
                print("⚠️ 发现潜在干扰，执行拦截任务...")
                
                # 第一步：进入消息列表
                open_alipay_chat(eye, brain, hand) 
                
                # 第二步：寻找并点击对话框
                img_path_list = eye.capture()
                list_texts = brain.analyze_screen(img_path_list)
                
                found_chat = False
                for item in list_texts:
                    if TARGET_NAME in item['text']:
                        print(f"📍 找到目标对话框: {TARGET_NAME}，潜入中...")
                        bx = (item['box'][0][0] + item['box'][2][0]) / 2
                        by = (item['box'][0][1] + item['box'][2][1]) / 2
                        hand.tap(bx, by) 
                        found_chat = True
                        time.sleep(2) 
                        break
                
                # 第三步：执行“双重弹射”回复逻辑
                if found_chat:
                    print("📝 正在输入回复，已开启表情包避让模式...")
                    # 激活输入框 (避开两边图标，点中间)
                    hand.tap(500, 2150) 
                    time.sleep(1)
                    
                    # 自动输入文字
                    keyboard.type_chinese(REPLY_TEXT)
                    time.sleep(1.5) 
                    
                    # 🚀 连续点击两个可能的“小飞机”位置，确保万无一失
                    print(f"🚀 点击位置 A {SEND_NORMAL}")
                    hand.tap(SEND_NORMAL[0], SEND_NORMAL[1])
                    time.sleep(0.5)
                    
                    print(f"🚀 点击位置 B {SEND_EMOJI}")
                    hand.tap(SEND_EMOJI[0], SEND_EMOJI[1])
                    
                    print("✅ 消息已射出，任务达成。")
                    time.sleep(3) 
                else:
                    print(f"❓ 列表里没看到 '{TARGET_NAME}'。")

                # 第四步：不论结果如何，立刻撤离回桌面
                print("🧹 清理现场，返回桌面。")
                os.system("adb shell input keyevent 3") 
            
            time.sleep(5) # 每5秒巡逻一次

    except KeyboardInterrupt:
        print("\n🛑 守卫模式已关闭。")

if __name__ == "__main__":
    main()