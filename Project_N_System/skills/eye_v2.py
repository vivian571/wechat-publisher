import os
import time

class EyeCore:
    def capture(self):
        # 截屏并保存
        save_path = "./logs/current_view.png"
        # 确保目录存在
        os.makedirs("./logs", exist_ok=True)
        
        # 调用 ADB 截图
        # print("[Eye] 正在捕获视网膜数据...")
        os.system("adb shell screencap -p /sdcard/n_temp.png")
        os.system(f"adb pull /sdcard/n_temp.png {save_path} > nul 2>&1") # > nul 是为了不显示那堆传输日志
        
        return save_path