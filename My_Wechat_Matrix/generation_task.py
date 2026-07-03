import os
import sys
from pathlib import Path
from generator import ContentGenerator
from image_generator import generate_cover_for_article

def run_matrix_generation():
    generator = ContentGenerator()
    
    tasks = [
        {
            "account": "Account_A_CrossBorder",
            "topic": "达沃斯风云：特朗普关税威胁与跨境电商的出海新局"
        },
        {
            "account": "Account_B_English",
            "topic": "从英伟达CEO黄仁勋的达沃斯演讲，学最地道的AI时代职场英语"
        },
        {
            "account": "Account_C_Life",
            "topic": "家常红烧肉：冬日里最极致的味蕾慰藉（附秘制浓郁酱汁配方）"
        },
        {
            "account": "Account_D_Tech",
            "topic": "重庆“汽车第一城”背后的智驾博弈：谁在引领中国汽车下半场？"
        }
    ]
    
    print("🚀 开始执行批量生成任务...")
    
    for task in tasks:
        account_name = task["account"]
        topic = task["topic"]
        
        print(f"\n--- 处理账号: {account_name} ---")
        try:
            # 1. 生成文章内容
            output_file = generator.generate_content(account_name, topic=topic)
            
            if output_file:
                # 2. 读取生成的标题 (output.txt 的第一行)
                with open(output_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        generated_title = lines[0].strip()
                        print(f"📄 已生成标题: {generated_title}")
                        
                        # 3. 生成封面图
                        account_dir = Path(output_file).parent
                        cover_path = generate_cover_for_article(generated_title, str(account_dir))
                        if cover_path:
                            print(f"🎨 封面图已生成: {cover_path}")
                        else:
                            print("⚠️ 封面图生成失败")
        except Exception as e:
            print(f"❌ {account_name} 任务失败: {e}")

if __name__ == "__main__":
    run_matrix_generation()
