import time
from skills.eye_v2 import VisionCore
from skills.brain_v2 import BrainCore
from skills.hand_v2 import HandCore
from skills.keyboard import KeyboardCore

def main():
    eye = VisionCore()
    brain = BrainCore()
    hand = HandCore()
    keyboard = KeyboardCore()

    # 这里的“黑名单”可以根据你的需要增加
    BLACK_LIST_WORDS = ["老婆", "想你", "开门", "复合"]
    OFFICIAL_REPLY = "【自动回复】当前为 Project N 系统接管。请仅交流孩子相关必要信息，其他消息将不予显示。"

    print("🛡️ [SocialGuard] 守卫模式已启动...")
    print("👉 正在监控社交软件界面，我会为你过滤掉不适信息。")

    try:
        while True:
            # 1. 抓取当前屏幕
            img_path = eye.capture()
            texts = brain.analyze_screen(img_path)
            
            # 2. 检查是否有违规词汇
            full_text = "".join([item['text'] for item in texts])
            
            found_trigger = False
            for word in BLACK_LIST_WORDS:
                if word in full_text:
                    print(f"⚠️ 检测到不适词汇: {word}")
                    found_trigger = True
                    break
            
            # 3. 如果触发，立刻执行“干预”
            if found_trigger:
                print("⚡ 启动防御动作：正在自动回复并退出窗口...")
                
                # 点击输入框（这里需要根据你手机的布局微调坐标，或者用文字定位）
                # 我们假设先点击底部中间区域激活输入
                hand.tap(500, 2300) 
                time.sleep(1)
                
                # 代替以安说话
                keyboard.type_chinese(OFFICIAL_REPLY)
                keyboard.enter()
                
                # 回复完立刻“逃离”现场，回到桌面或切换应用
                hand.tap(100, 150) # 点击左上角返回按钮
                print("✅ 已成功拦截并处理。以安，你不需要看这些。")

            time.sleep(2) # 每2秒巡逻一次

    except KeyboardInterrupt:
        print("\n🛑 守卫模式已关闭。")

if __name__ == "__main__":
    main()