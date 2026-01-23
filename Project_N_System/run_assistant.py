import time
from skills.eye_v2 import VisionCore
from skills.brain_v2 import BrainCore
from skills.hand_v2 import HandCore

def main():
    print("🤖 Project N (Yi An Edition) 正在启动...")
    
    # 1. 唤醒所有器官
    eye = VisionCore()
    brain = BrainCore()
    hand = HandCore() 
    
    print("\n✅ 助手已上线！请操作你的手机，我会盯着看的。")
    print("按 Ctrl+C 可以让我停下来。\n")

    try:
        while True:
            # 第一步：看
            img_path = eye.capture()
            
            # 第二步：想
            texts = brain.analyze_screen(img_path)
            
            # 第三步：说（打印它看到了什么）
            print("-" * 30)
            found_keywords = []
            for item in texts:
                t = item['text']
                if len(t) > 1:
                    found_keywords.append(t)
            
            print(f"👁️ 我看到了: {found_keywords}")

            # --- 自动化逻辑区域 ---
            # 目标：如果看到 "微信"，就自动点进去
            target = "微信"
            coord = brain.find_keyword(texts, target)
            
            if coord:
                print(f"💡 发现 '{target}'！位置在 {coord}，正在执行点击...")
                # 真正的点击动作！
                hand.tap(coord[0], coord[1])
                print("✨ 点击完成，休息 5 秒...")
                time.sleep(5)
            else:
                # 没找到就只需休息 3 秒
                time.sleep(3)

    except KeyboardInterrupt:
        print("\n👋 休息一下。Project N 待机中。")

if __name__ == "__main__":
    main()