"""
键盘功能完整测试
测试所有输入方法：中文、英文、删除、换行等
"""
import time
from skills.keyboard import KeyboardCore

def main():
    print("🎹 键盘功能完整测试")
    print("=" * 50)
    
    # 初始化键盘
    kb = KeyboardCore()
    
    print("\n👉 请在手机上打开【备忘录】或【微信聊天窗口】")
    print("👉 点击输入框，确保光标在闪烁！")
    print("👉 准备好后，测试将在 5 秒后开始...\n")
    
    for i in range(5, 0, -1):
        print(f"⏳ {i}...")
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📝 [测试 1] 中文输入")
    print("=" * 50)
    kb.type_chinese("以安，这是一条测试消息！")
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📝 [测试 2] 换行")
    print("=" * 50)
    kb.enter()
    time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📝 [测试 3] 英文输入（快速模式）")
    print("=" * 50)
    kb.type_english("Hello World 123")
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📝 [测试 4] 混合输入")
    print("=" * 50)
    kb.enter()
    kb.type_chinese("今天天气真好，温度25°C")
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📝 [测试 5] 删除功能")
    print("=" * 50)
    print("删除最后 3 个字符...")
    kb.backspace(3)
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📝 [测试 6] 特殊字符")
    print("=" * 50)
    kb.enter()
    kb.type_chinese("特殊符号测试：@#￥%…&*（）")
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("📝 [测试 7] 长文本输入")
    print("=" * 50)
    kb.enter()
    long_text = """这是一段较长的文本测试。
Project N 系统现在可以：
1. 自动识别屏幕内容
2. 智能输入中英文
3. 模拟各种按键操作
功能非常强大！"""
    kb.type_chinese(long_text)
    time.sleep(3)
    
    print("\n" + "=" * 50)
    print("📝 [测试 8] 慢速输入（逐字模式）")
    print("=" * 50)
    kb.enter()
    kb.type_slow("慢速输入测试", delay=0.2)
    time.sleep(2)
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)
    print("\n请检查手机上的输入结果。")
    print("如果一切正常，说明键盘模块已完全可用！🎉")

if __name__ == "__main__":
    main()
