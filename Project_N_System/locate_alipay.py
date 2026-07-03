"""
支付宝消息页面定位助手
帮助找到正确的 Activity 和消息标签坐标
"""

import os
import time

print("=== 支付宝消息页面定位助手 ===\n")

# 1. 测试不同的启动方式
print("测试1: 使用主 Activity 启动...")
os.system("adb shell am start -n com.eg.android.AlipayGphone/.AlipayLogin")
time.sleep(3)

# 2. 获取当前 Activity
print("\n获取当前 Activity...")
os.system("adb shell dumpsys window | findstr mCurrentFocus")

# 3. 获取屏幕尺寸
print("\n获取屏幕尺寸...")
os.system("adb shell wm size")

# 4. 截图并保存
print("\n截取当前屏幕...")
os.system("adb shell screencap -p /sdcard/alipay_screen.png")
os.system("adb pull /sdcard/alipay_screen.png .")
print("✅ 截图已保存为 alipay_screen.png")

print("\n" + "=" * 50)
print("请查看 alipay_screen.png,找到底部'消息'标签的大致位置")
print("通常在屏幕底部,可能的坐标范围:")
print("  - X: 屏幕宽度的 1/4 到 3/4 之间")
print("  - Y: 屏幕高度的 90% 左右")
print("=" * 50)
