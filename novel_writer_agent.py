import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量安全获取 API Key
API_KEY = os.getenv("GROQ_API_KEY")
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_ID = "llama-3.3-70b-versatile"

def call_llm(prompt, max_retries=3):
    if not API_KEY:
        print("❌ 错误: 未设置 GROQ_API_KEY 环境变量，请在 .env 中配置")
        return None

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_ID,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.8,
        "max_tokens": 4000
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(URL, headers=headers, json=payload)
            if response.status_code == 429:
                print(f"⚠️ 触发API频率限制，等待 15 秒后重试... (第 {attempt + 1}/{max_retries} 次)")
                time.sleep(15)
                continue
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            print(f"❌ API 请求错误: {e}")
            if attempt == max_retries - 1:
                return None
            time.sleep(5)
            
    return None

def read_concepts(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def generate_outline(concepts_text):
    prompt = f"""
你是一个顶级的“技术现实主义”网文主编。
请阅读以下今天生成的多个小说脑洞设定，挑选出【最具爆款潜力、现实恐惧感最强】的一个。

【核心任务】
针对你挑选的脑洞，生成一份详细的小说连载大纲，包含以下内容：
1. **入选理由**：为什么这个设定最容易火？（50字）
2. **世界观设定**：技术背景、社会运转规则（100字）
3. **主角人设与困境**：主角是谁，面临什么现实威胁（100字）
4. **黄金三章分集大纲**：
   - 第一章大纲：平淡日常中的突然诡异（现实侵入感）
   - 第二章大纲：技术失控的初步显现（发现细思极恐的真相）
   - 第三章大纲：彻底颠覆认知的悬念钩子（无法回头的深渊）

【脑洞素材库】
{concepts_text}
"""
    print("🧠 正在请求大模型挑选脑洞并生成大纲...")
    return call_llm(prompt)

def generate_chapter(outline_text, chapter_num, chapter_desc):
    prompt = f"""
你是一个顶级的悬疑科幻小说家，擅长创作“技术现实主义”小说。
文风要求：冷静、克制、细节极其真实、具有极强的现实侵入感。不要说教，通过角色的恐惧和遭遇来展现技术的异化。

【背景大纲】
{outline_text}

【当前任务】
请严格根据大纲，撰写【第{chapter_num}章】的具体正文。
本章剧情要求：{chapter_desc}

【写作格式与要求】
1. 直接开始写小说的正文内容，不要说废话。
2. 字数：必须极其详尽细腻，字数越长越好。
3. 必须有细腻的心理活动和诡异的技术细节描写。例如对屏幕、代码、终端的描写要让人有压抑感。
4. 每章结尾必须留有强烈的悬念钩子！
"""
    print(f"✍️ 正在撰写第 {chapter_num} 章...")
    return call_llm(prompt)
    
def main():
    # 动态获取工作目录，优先从环境变量获取，否则使用当前执行脚本的同级目录
    base_dir = os.getenv("WORKSPACE_DIR", os.path.dirname(os.path.abspath(__file__)))
    dir_path = os.path.join(base_dir, "wechat", "documents", "小说")
    
    if not os.path.exists(dir_path):
        print(f"❌ 找不到目录: {dir_path}")
        return

    # 为了防止时间不一致，我们直接读取目录里的文件（取最新的一个脑洞文件）
    files = [f for f in os.listdir(dir_path) if f.endswith("-Trending-Novel-Concepts.md")]
    if not files:
        print("❌ 找不到脑洞文件")
        return
        
    # 使用修改时间排序（从新到旧），比直接排文件名更精准
    files.sort(key=lambda x: os.path.getmtime(os.path.join(dir_path, x)), reverse=True)
    concepts_file = os.path.join(dir_path, files[0])
    print(f"📄 读取脑洞文件: {files[0]}")
    
    concepts_text = read_concepts(concepts_file)
    
    # 1. 生成大纲
    outline = generate_outline(concepts_text)
    if not outline:
        return
        
    print("✅ 大纲生成完毕！\n")
    
    # 2. 生成三章内容
    chapters = []
    chapter_prompts = [
        "第一章：平淡日常中的突然诡异（现实侵入感）",
        "第二章：技术失控的初步显现（发现细思极恐的真相）",
        "第三章：彻底颠覆认知的悬念钩子（无法回头的深渊）"
    ]
    
    for i, desc in enumerate(chapter_prompts, 1):
        content = generate_chapter(outline, i, desc)
        if content:
            chapters.append(f"## 第{i}章\n\n{content}\n\n")
            time.sleep(5) # Groq rate limits
        else:
            print(f"❌ 第 {i} 章生成失败。")
            break
            
    if len(chapters) == 3:
        target_dir = os.path.join(base_dir, "wechat", "documents", "小说", "连载输出")
        os.makedirs(target_dir, exist_ok=True)
        date_str = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(target_dir, f"{date_str}-黄金三章.md")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# 技术现实主义小说连载 - 黄金三章 ({date_str})\n\n")
            f.write("## 核心大纲\n")
            f.write(outline + "\n\n---\n\n")
            for chap in chapters:
                f.write(chap)
                
        print(f"\n✅ 成功生成黄金三章！已保存至: {file_path}")

if __name__ == "__main__":
    main()
