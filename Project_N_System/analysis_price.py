import time
import re
import os
from skills.eye_v2 import VisionCore
from skills.brain_v2 import BrainCore
from skills.hand_v2 import HandCore # 引入“手”

def clean_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def is_trap(text):
    """
    陷阱过滤器
    """
    traps = ["补", "省", "券", "减", "送", "退", "折", "起"]
    for t in traps:
        if t in text:
            return True
    return False

def extract_prices(text_list):
    price_data = []
    
    for item in text_list:
        text = item['text']
        
        if is_trap(text):
            continue

        # 匹配 ¥25.9 或 25.9元
        match_symbol = re.search(r'[¥￥]\s*(\d+(?:\.\d+)?)', text)
        match_yuan = re.search(r'^(\d+(?:\.\d+)?)\s*元$', text)
        
        price = 0.0
        found = False
        
        if match_symbol:
            price = float(match_symbol.group(1))
            found = True
        elif match_yuan:
            price = float(match_yuan.group(1))
            found = True
        
        if found and price > 1.0:
            price_data.append({
                "price": price,
                "raw": text,
            })
            
    return price_data

def main():
    eye = VisionCore()
    brain = BrainCore()
    hand = HandCore() # 初始化手
    
    # 全局最低价记录（不仅仅是当前屏，而是记录一路走来看到的最便宜的）
    global_best_price = None
    
    print("🛒 [全自动购物巡航] 启动！")
    print("👉 请打开 美团/淘宝 的商品列表页")
    print("👉 我会自己动，请把手拿开...")
    time.sleep(2)
    
    try:
        while True:
            # 1. 抓取
            img_path = eye.capture()
            texts = brain.analyze_screen(img_path)
            
            # 2. 分析
            prices = extract_prices(texts)
            
            # 3. 更新全局最低价
            if prices:
                # 当前屏的最低价
                prices.sort(key=lambda x: x['price'])
                current_min = prices[0]
                
                # 如果还没有全局最低，或者发现了更便宜的
                if global_best_price is None or current_min['price'] < global_best_price['price']:
                    global_best_price = current_min
            
            # 4. 刷新显示
            clean_console()
            print("-" * 40)
            print(f"🚀 自动巡航中... (按下 Ctrl+C 紧急刹车)")
            print("-" * 40)
            
            if prices:
                print(f"📄 当前屏幕商品数: {len(prices)}")
                print(f"👀 本页最低: ¥ {prices[0]['price']} ({prices[0]['raw']})")
            else:
                print("🤷‍♂️ 本页未发现有效价格...")
                
            print("-" * 40)
            if global_best_price:
                print(f"👑 【历史最低记录】: ¥ {global_best_price['price']}")
                print(f"   商品信息: {global_best_price['raw']}")
            else:
                print("👑 正在寻找全场最低...")
            print("-" * 40)

            # 5. 关键一步：自己动！
            print("👆 正在翻页...")
            hand.swipe_up() # 模拟手指上滑
            
            # 6. 休息一下等待页面加载
            # 翻页后要多给点时间，不然截图会是模糊的
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 巡航结束。")
        if global_best_price:
            print(f"\n🏆 最终帮你找到了这个最便宜的：¥ {global_best_price['price']}")
            print(f"   {global_best_price['raw']}")

if __name__ == "__main__":
    main()