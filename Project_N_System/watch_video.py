import time
import os
import glob
from difflib import SequenceMatcher
from skills.eye_v2 import VisionCore
from skills.brain_v2 import BrainCore
import re

def clean_old_logs():
    files = glob.glob("logs/*.png")
    for f in files:
        try:
            os.remove(f)
        except:
            pass

def clean_text(text):
    """
    深度清洗手术刀：把混在句子里的杂质挖走
    """
    if not text:
        return ""
        
    # 1. 擦除 "7.8万", "1.9w", "1000+" 这种点赞数
    # 逻辑：数字 + (万/w/W/+)
    text = re.sub(r'\d+(\.\d+)?[万wW\+]', '', text)
    
    # 2. 擦除 "12:30", "01:22" 这种时间戳
    text = re.sub(r'\d+:\d+', '', text)
    
    # 3. 去掉奇怪的单字符（OCR有时候会把图标识别成杂乱的符号）
    # 这里保留中文、英文、标点，去掉其他乱七八糟的
    # (这一步如果不放心可以先注释掉，但通常很有用)
    # text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？、,!?\.]', '', text)
    
    # 4. 去掉首尾空格
    return text.strip()

def is_garbage(text):
    """
    垃圾过滤器：如果是纯数字或者太短的垃圾，直接丢弃
    """
    # 清洗一下再判断
    clean = text.strip()
    
    # 如果清洗完只剩下数字，或者什么都不剩了，那就是垃圾
    if not clean:
        return True
    if clean.isdigit(): # 纯数字 "2024"
        return True
    
    # 也可以过滤掉太短的片段 (比如只有1个字)
    if len(clean) < 2:
        return True
        
    return False

def is_similar(str1, str2):
    if not str1 or not str2:
        return False
    s1 = str1.replace(" ", "")
    s2 = str2.replace(" ", "")
    
    # 底部杂音黑名单 (加强版)
    noise_words = ["首页", "朋友", "消息", "我", "弹幕", "点赞", "分享", "评论", "收藏"]
    noise_count = sum(1 for w in noise_words if w in s1)
    if noise_count >= 2: 
        return True 

    return SequenceMatcher(None, s1, s2).ratio() > 0.8

def main():
    clean_old_logs()
    eye = VisionCore()
    brain = BrainCore()
    all_subtitles = []
    
    print("\n🧼 [深度净化版] 字幕记录员已上线")
    print("👉 已启用正则表达式手术刀，强行挖除 '1.9万' 等杂质")
    print("-" * 30)

    try:
        while True:
            start_time = time.time()
            img_path = eye.capture()
            texts = brain.analyze_screen(img_path)
            
            current_screen_subs = []
            for item in texts:
                raw_text = item['text']
                box = item['box']
                
                center_y = (box[0][1] + box[2][1]) / 2
                center_x = (box[0][0] + box[2][0]) / 2
                
                # 依然保持空间限制
                if 1000 < center_y < 1900 and 150 < center_x < 950:
                    
                    # 【核心步骤】先做深度清洗
                    cleaned_text = clean_text(raw_text)
                    
                    # 再判断剩下来的东西是不是垃圾
                    if not is_garbage(cleaned_text):
                        current_screen_subs.append(cleaned_text)
            
            if current_screen_subs:
                full_line = " ".join(current_screen_subs)
                
                # 再次清洗 full_line (防止拼接后出现奇怪空格)
                full_line = full_line.replace("  ", " ") 
                
                if not all_subtitles or not is_similar(full_line, all_subtitles[-1]):
                    timestamp = time.strftime("%M:%S")
                    print(f"[{timestamp}] {full_line}")
                    all_subtitles.append(full_line)
            
            elapsed = time.time() - start_time
            if elapsed < 2.0:
                time.sleep(2.0 - elapsed)

    except KeyboardInterrupt:
        print("\n\n🛑 停止记录。")
        filename = f"logs/note_{time.strftime('%H%M')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(all_subtitles))
        print(f"✅ 净化版笔记已保存: {filename}")

if __name__ == "__main__":
    main()