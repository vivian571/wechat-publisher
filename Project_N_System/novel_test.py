import time
from skills.keyboard import KeyboardCore
from skills.hand_v2 import HandCore

def main():
    keyboard = KeyboardCore()
    hand = HandCore()
    
    print("🤖 [中文输入测试] 准备启动...")
    print("👉 请在 5 秒内，手动在手机上打开微信、备忘录或任何输入窗口。")
    print("👉 并且一定要【点一下输入框】，确保光标在闪烁！")
    
    for i in range(5, 0, -1):
        print(f"⏳ {i}...")
        time.sleep(1)

    # 1. 输入中文
    content = "以安，这是我为你写下的第一行中文。Project N 终于会说话了。"
    keyboard.type_chinese(content)
    
    # 2. 模拟发送 (可选)
    # time.sleep(1)
    # keyboard.enter()
    
    print("\n✅ 输入完成！看看手机上是不是出现了中文字？")

if __name__ == "__main__":
    main()