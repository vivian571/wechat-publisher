"""
ADB Keyboard 调试脚本
用于诊断和测试 ADB Keyboard 的输入功能
"""
import os
import time

def check_keyboard_status():
    """检查键盘状态"""
    print("=" * 50)
    print("🔍 [诊断 1] 检查 ADB Keyboard 安装状态")
    print("=" * 50)
    
    # 1. 检查包是否安装
    print("\n📦 检查包安装...")
    os.system("adb shell pm list packages | findstr keyboard")
    
    # 2. 检查当前输入法
    print("\n⌨️ 检查当前输入法...")
    os.system("adb shell settings get secure default_input_method")
    
    # 3. 检查已启用的输入法
    print("\n✅ 检查已启用的输入法列表...")
    os.system("adb shell ime list -s")
    
    print("\n" + "=" * 50)

def test_input_methods():
    """测试不同的输入方法"""
    print("\n🧪 [诊断 2] 测试不同的输入方法")
    print("=" * 50)
    
    print("\n👉 请在手机上打开【备忘录】或【微信】")
    print("👉 并且【点击输入框】，确保光标在闪烁！")
    print("👉 准备好后，我会在 5 秒后开始测试...\n")
    
    for i in range(5, 0, -1):
        print(f"⏳ {i}...")
        time.sleep(1)
    
    # 方法 1: 使用 ADB_INPUT_TEXT 广播
    print("\n📡 [方法 1] 使用 ADB_INPUT_TEXT 广播...")
    cmd1 = 'adb shell am broadcast -a ADB_INPUT_TEXT --es msg "测试方法1"'
    os.system(cmd1)
    time.sleep(2)
    
    # 方法 2: 使用 ADB_INPUT_CHARS 广播
    print("\n📡 [方法 2] 使用 ADB_INPUT_CHARS 广播...")
    cmd2 = 'adb shell am broadcast -a ADB_INPUT_CHARS --es msg "测试方法2"'
    os.system(cmd2)
    time.sleep(2)
    
    # 方法 3: 使用 ADB_EDITOR_CODE (模拟按键)
    print("\n📡 [方法 3] 模拟空格键...")
    cmd3 = 'adb shell am broadcast -a ADB_INPUT_CODE --ei code 62'
    os.system(cmd3)
    time.sleep(1)
    
    print("\n✅ 测试完成！请检查手机上是否有任何文字出现。")

def test_alternative_method():
    """测试备用方法 - 使用 input text 命令"""
    print("\n" + "=" * 50)
    print("🔄 [诊断 3] 测试备用方法 (adb shell input text)")
    print("=" * 50)
    
    print("\n⚠️ 注意：这个方法不支持中文，只能输入英文和数字")
    print("👉 请确保输入框仍然有焦点...\n")
    
    time.sleep(3)
    
    # 使用 adb shell input text (只支持 ASCII)
    print("📝 输入英文测试...")
    os.system('adb shell input text "Hello123"')
    time.sleep(1)
    
    print("\n✅ 如果看到 'Hello123'，说明 ADB 连接正常，但 ADB Keyboard 可能有问题")

def check_permissions():
    """检查权限"""
    print("\n" + "=" * 50)
    print("🔐 [诊断 4] 检查应用权限")
    print("=" * 50)
    
    print("\n📋 ADB Keyboard 的权限信息：")
    os.system("adb shell dumpsys package com.android.adbkeyboard | findstr permission")

def main():
    print("\n🚀 ADB Keyboard 完整诊断工具")
    print("=" * 50)
    
    # 步骤 1: 检查状态
    check_keyboard_status()
    
    # 步骤 2: 测试输入
    test_input_methods()
    
    # 步骤 3: 备用方法
    test_alternative_method()
    
    # 步骤 4: 检查权限
    check_permissions()
    
    print("\n" + "=" * 50)
    print("📊 诊断报告总结")
    print("=" * 50)
    print("""
如果所有方法都失败：
1. ✅ ADB Keyboard 已安装且已设置为默认输入法
2. ❌ 但广播接收可能被 vivo 系统阻止

解决方案：
方案 A: 在手机【设置】→【应用管理】→【ADB Keyboard】中：
   - 允许后台运行
   - 允许自启动
   - 关闭省电优化

方案 B: 使用备用输入方案（仅英文）：
   - 使用 adb shell input text 命令
   - 或者使用 uiautomator2 库

方案 C: 尝试重启 ADB Keyboard：
   - adb shell am force-stop com.android.adbkeyboard
   - adb shell ime set com.android.adbkeyboard/.AdbIME
    """)

if __name__ == "__main__":
    main()
