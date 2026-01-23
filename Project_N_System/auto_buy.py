import time
import re
import os
from skills.eye_v2 import VisionCore
from skills.brain_v2 import BrainCore
from skills.hand_v2 import HandCore

# --- 核心配置 ---
MAX_PAGES = 5  # 你想让它滑几页？（建议先设5页测试，熟练了再改20）
SWIPE_DELAY = 3 # 每一页停留几秒（给OCR反应时间）

def clean_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def swipe_down_to_go_up():
    """这是‘往回走’的动作：手指从上往下滑，页面就会上去"""
    print("🔙 正在往回翻...")
    os.system("adb shell input swipe 500 500 500 1500")
    time.sleep(2)

def is_trap(text):
    traps = ["补", "省", "券", "减", "送", "退", "折", "起", "饭卡"]
    for t in traps:
        if t in text:
            return True
    return False

def analyze_current_page(texts):
    """分析当前页的最低价"""
    page_best_item = None
    page_min_price = 99999.0
    
    for item in texts:
        text = item['text']
        if is_trap(text): continue

        match_symbol = re.search(r'[¥￥]\s*(\d+(?:\.\d+)?)', text)
        match_yuan = re.search(r'^(\d+(?:\.\d+)?)\s*元$', text)
        
        price = 0.0
        if match_symbol: price = float(match_symbol.group(1))
        elif match_yuan: price = float(match_yuan.group(1))
            
        if price > 1.0:
            if price < page_min_price:
                page_min_price = price
                page_best_item = item
                
    return page_best_item, page_min_price

def main():
    eye = VisionCore()
    brain = BrainCore()
    hand = HandCore()
    
    # 记忆体：用来存全场最佳
    global_best = {
        "price": 99999.0,
        "page_index": 0,  # 记录它在第几页
        "text": "",       # 记录它的名字，方便回来找
        "box": []
    }
    
    print(f"🛒 [智能回溯采购] 启动！计划扫描 {MAX_PAGES} 页...")
    print("👉 请打开商品列表，双手离开手机！")
    time.sleep(2)
    
    # === 第一阶段：探索模式 ===
    for current_page in range(1, MAX_PAGES + 1):
        clean_console()
        print(f"🕵️ 正在扫描第 [{current_page}/{MAX_PAGES}] 页...")
        
        # 1. 看
        img_path = eye.capture()
        texts = brain.analyze_screen(img_path)
        
        # 2. 找当前页最佳
        item, price = analyze_current_page(texts)
        
        # 3. PK 全局最佳
        if item and price < global_best["price"]:
            print(f"✨ 发现新低价！¥ {price} (在第 {current_page} 页)")
            global_best["price"] = price
            global_best["page_index"] = current_page
            global_best["text"] = item['text']
            global_best["box"] = item['box'] # 这里的坐标是当页的，回来后会变，所以主要靠文字找
        else:
            print(f"   本页最低 ¥ {price if item else 'N/A'}，未打破记录 (¥ {global_best['price']})")
            
        # 4. 翻页 (如果是最后一页就不翻了)
        if current_page < MAX_PAGES:
            print("👇 继续往下找...")
            hand.swipe_up() # 往下翻
            time.sleep(SWIPE_DELAY)
            
    # === 第二阶段：返程模式 ===
    print("\n" + "="*30)
    print("🏁 扫描结束！准备回头去买最好的...")
    print(f"🏆 目标：第 {global_best['page_index']} 页的 ¥ {global_best['price']}")
    print(f"📝 商品特征：{global_best['text']}")
    print("="*30)
    
    # 计算要往回翻几次
    # 比如现在在第5页，目标在第2页，需要往回翻 5-2 = 3 次
    steps_back = MAX_PAGES - global_best['page_index']
    
    if steps_back > 0:
        print(f"🔙 需要往回翻 {steps_back} 次，请坐稳...")
        for i in range(steps_back):
            swipe_down_to_go_up()
    else:
        print("😄 运气真好，最便宜的就在刚才这最后一页！")

    # === 第三阶段：精准抓捕 ===
    print("👀 已回到大概位置，正在重新定位目标...")
    time.sleep(2) # 等页面停稳
    
    # 再看一次屏幕
    img_path = eye.capture()
    texts = brain.analyze_screen(img_path)
    
    # 在屏幕上找那个熟悉的文字
    target_text = global_best["text"]
    found_target = None
    
    # 模糊查找：只要包含了之前的关键信息就行
    # 取前5个字做关键词，防止OCR识别有微小差异
    keyword = target_text[:5] 
    
    for item in texts:
        # 如果包含关键词，或者价格对得上
        if keyword in item['text'] or str(int(global_best['price'])) in item['text']:
            found_target = item
            break
            
    if found_target:
        print(f"🎯 找到了！位置在 {found_target['box']}")
        box = found_target['box']
        cx = int((box[0][0] + box[2][0]) / 2)
        cy = int((box[0][1] + box[2][1]) / 2)
        
        print("👆 执行点击！")
        hand.tap(cx, cy)
        print("\n✅ 任务完成！请以安确认支付。")
    else:
        print(f"\n😵 糟糕，回到第 {global_best['page_index']} 页了，但没看清那个商品。")
        print("可能回翻的时候有点误差，你手动找找那个 ¥" + str(global_best['price']) + " 的商品？")

if __name__ == "__main__":
    main()