
from skills.hand_v2 import HandCore
import time

print("Project N 系统自检中...")
hand = HandCore()
print("尝试连接手机...")
# 测试点击屏幕中央 (你需要确保 ADB 已连接)
hand.tap(500, 1000)
print("✅ 系统就绪。")
