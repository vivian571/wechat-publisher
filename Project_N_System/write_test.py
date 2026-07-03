import time
from skills.hand_v2 import HandCore

def main():
    hand = HandCore()
    
    print("🤖 准备打字测试...")
    print("👉 请在 5 秒内，手动在手机上打开一个输入框（比如备忘录、微信输入框）")
    print("👉 并且【点击一下输入框】确保光标在闪烁！")
    
    # 倒计时，给你留出操作时间
    for i in range(5, 0, -1):
        print(f"⏳ {i}...")
        time.sleep(1)

    print("\n🚀 开始输入！")
    # 这里输入你想让我写的话（暂时只能英文/拼音）
    hand.type_text("Yi_An_is_here.")
    hand.type_text("Project_N_Online.")
    
    print("✅ 输入完毕。")

if __name__ == "__main__":
    main()