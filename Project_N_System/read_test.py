import os
from rapidocr_onnxruntime import RapidOCR

# 1. 唤醒识字引擎
print("🧠 正在加载语言中枢 (RapidOCR)...")
engine = RapidOCR()

# 2. 指定我们要读的目标（就是刚才那张截图）
image_path = 'test_eye.png'

if not os.path.exists(image_path):
    print("❌ 没找到图片！请先运行截屏命令。")
else:
    print(f"👁️ 正在阅读: {image_path} ...")
    
    # 3. 开始识别
    result, elapse = engine(image_path)
    
    print("\n" + "="*20 + " 识别结果 " + "="*20)
    if result:
        for line in result:
            # line[1] 是文字内容，line[2] 是置信度
            text = line[1]
            confidence = line[2]
            print(f"📄: {text}")
    else:
        print("⚠️ 这张图里好像没有字？")
    
    print("="*50)
    print("✅ 阅读完毕。")