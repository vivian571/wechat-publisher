"""
OCR 测试脚本 - 测试 rapidocr_onnxruntime 功能
"""

from rapidocr_onnxruntime import RapidOCR
import os

print('=' * 50)
print('Project N - OCR 功能测试')
print('=' * 50)

# 初始化 OCR
print('\n1. 初始化 OCR 引擎...')
ocr = RapidOCR()
print('✅ OCR 引擎加载成功!')

# 查找测试图片
test_images = ['test_eye.png', 'logs/screenshots/screen_20260111_191120.png']
test_image = None

for img in test_images:
    if os.path.exists(img):
        test_image = img
        break

if test_image:
    print(f'\n2. 识别图片: {test_image}')
    result, elapse = ocr(test_image)
    
    # elapse 是一个列表 [det_time, cls_time, rec_time]
    total_time = sum(elapse) if isinstance(elapse, list) else elapse
    print(f'   耗时: {total_time:.2f} 秒')
    
    if result:
        print(f'\n3. 识别结果 (共 {len(result)} 个文本区域):')
        print('-' * 50)
        for i, (box, text, score) in enumerate(result[:10]):
            print(f'   [{i+1:2d}] {text}  (置信度: {score:.2f})')
        if len(result) > 10:
            print(f'   ... 还有 {len(result) - 10} 个文本区域')
    else:
        print('\n❌ 未识别到文本')
else:
    print('\n⚠️ 未找到测试图片')
    print('   请先运行: adb shell screencap -p /sdcard/test.png')
    print('   然后运行: adb pull /sdcard/test.png test_eye.png')

print('\n' + '=' * 50)
