import sys
import os

# 这里的逻辑是：为了让 brain 能引用到虚拟环境里的库，我们需要确保环境路径正确
try:
    from rapidocr_onnxruntime import RapidOCR
except ImportError:
    print("❌ 大脑缺氧：请确保你在 (venv) 虚拟环境里运行！")
    sys.exit(1)

class BrainCore:
    def __init__(self):
        print("🧠 [Brain] 正在初始化神经网络...")
        # 初始化 OCR 引擎，只做一次，不用每次都加载
        self.ocr = RapidOCR()
        print("🧠 [Brain] 视觉中枢已就绪。")

    def analyze_screen(self, image_path):
        """
        输入：屏幕截图路径
        输出：屏幕上所有的文字内容列表
        """
        if not os.path.exists(image_path):
            return []

        # 识字
        result, elapse = self.ocr(image_path)
        
        extracted_text = []
        if result:
            for line in result:
                # line[1] 是文字，line[0] 是坐标(box)
                text = line[1]
                box = line[0] 
                extracted_text.append({"text": text, "box": box})
                
        return extracted_text

    def find_keyword(self, text_list, keyword):
        """
        在识别结果里找某个词，如果找到了，返回它的坐标中心点 (x, y)
        """
        for item in text_list:
            if keyword in item["text"]:
                # 计算文字区域的中心点，方便让“手”去点击
                box = item["box"]
                # box 是四个点 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
                # 简单算中心：(x1+x3)/2, (y1+y3)/2
                center_x = int((box[0][0] + box[2][0]) / 2)
                center_y = int((box[0][1] + box[2][1]) / 2)
                print(f"🎯 [Brain] 发现目标 '{keyword}' @ ({center_x}, {center_y})")
                return (center_x, center_y)
        
        return None