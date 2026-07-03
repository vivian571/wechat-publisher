import os
import time
import subprocess

class KeyboardCore:
    """
    键盘输入核心模块
    支持中文、英文、特殊字符输入
    """
    
    def __init__(self):
        """初始化键盘模块"""
        print("⌨️ [Keyboard] 键盘模块已初始化")
    
    def type_chinese(self, text):
        """
        利用 ADBKeyBoard 直接输入 UTF-8 中文
        
        Args:
            text: 要输入的文本（支持中文、英文、数字、标点）
        """
        print(f"⌨️ [Keyboard] 正在输入内容: {text[:20]}...")
        
        # 转义特殊字符，防止命令中断
        # 单引号需要特殊处理
        safe_text = text.replace("'", "'\\''")
        
        # 使用 ADB_INPUT_TEXT 广播（已验证可用）
        cmd = f"adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{safe_text}'"
        
        # 执行广播
        result = os.system(cmd)
        
        # 给一点时间让输入完成
        time.sleep(0.3)
        
        if result == 0:
            print(f"✅ [Keyboard] 输入完成: {text[:30]}...")
        else:
            print(f"⚠️ [Keyboard] 输入可能失败，返回码: {result}")
        
        return result == 0
    
    def type_english(self, text):
        """
        输入纯英文/数字（备用方法，更快速）
        
        Args:
            text: 纯英文文本（不支持中文和特殊符号）
        """
        print(f"⌨️ [Keyboard] 输入英文: {text}")
        
        # 使用 input text 命令（仅支持 ASCII）
        # 需要转义空格和特殊字符
        safe_text = text.replace(" ", "%s")
        cmd = f'adb shell input text "{safe_text}"'
        
        result = os.system(cmd)
        time.sleep(0.2)
        
        return result == 0
    
    def type_slow(self, text, delay=0.1):
        """
        逐字输入（用于特殊场景，更稳定但较慢）
        
        Args:
            text: 要输入的文本
            delay: 每个字符之间的延迟（秒）
        """
        print(f"⌨️ [Keyboard] 慢速输入模式: {text[:20]}...")
        
        for char in text:
            safe_char = char.replace("'", "'\\''")
            cmd = f"adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{safe_char}'"
            os.system(cmd)
            time.sleep(delay)
        
        print(f"✅ [Keyboard] 慢速输入完成")
    
    def enter(self):
        """模拟回车键/发送键"""
        print("⏎ [Keyboard] 按下回车键")
        os.system("adb shell input keyevent 66")
        time.sleep(0.2)
    
    def backspace(self, count=1):
        """
        模拟删除键
        
        Args:
            count: 删除次数
        """
        print(f"⌫ [Keyboard] 删除 {count} 个字符")
        for _ in range(count):
            os.system("adb shell input keyevent 67")
            time.sleep(0.1)
    
    def clear_input(self):
        """清空输入框（全选 + 删除）"""
        print("🗑️ [Keyboard] 清空输入框")
        # Ctrl+A (全选)
        os.system("adb shell input keyevent 29 52")  # CTRL + A
        time.sleep(0.2)
        # Delete
        os.system("adb shell input keyevent 67")
        time.sleep(0.2)
    
    def paste(self):
        """模拟粘贴操作"""
        print("📋 [Keyboard] 执行粘贴")
        os.system("adb shell input keyevent 279")  # KEYCODE_PASTE
        time.sleep(0.3)