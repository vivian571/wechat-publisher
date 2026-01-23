import os
import time

class HandCore:
    def __init__(self):
        # 初始化时不需要做太重的工作
        pass

    def tap(self, x, y):
        # 基础点击
        cmd = f"adb shell input tap {x} {y}"
        print(f"👋 [Hand] 点击: ({x}, {y})")
        os.system(cmd)
        
    def type_text(self, text):
        # 输入英文/拼音 (ADB 原生不支持直接输中文，后面我会教你‘剪贴板’大法)
        clean_text = text.replace(" ", "%s") 
        cmd = f"adb shell input text {clean_text}"
        print(f"⌨️ [Hand] 输入: {text}")
        os.system(cmd)

    def swipe_up(self):
        # 上滑 (刷视频专用)
        print("👆 [Hand] 上滑屏幕")
        os.system("adb shell input swipe 500 1500 500 500")

    def home(self):
        # 按 Home 键回到桌面
        print("🏠 [Hand] 按下 Home 键")
        os.system("adb shell input keyevent 3")

    def back(self):
        # 按返回键
        print("🔙 [Hand] 按下返回键")
        os.system("adb shell input keyevent 4")
        
    def enter(self):
        # 按回车/发送键
        print("↵ [Hand] 按下回车")
        os.system("adb shell input keyevent 66")