import os
import pathlib
import httpx
from openai import OpenAI

# 设置代理
PROXY_URL = "http://127.0.0.1:3067"
os.environ["HTTP_PROXY"] = PROXY_URL
os.environ["HTTPS_PROXY"] = PROXY_URL

def generate():
    api_key = "f18aacb6499a4d8d9fcedb80543831e2.ZuWicOFsWW8wzYSF"
    base_url = "https://open.bigmodel.cn/api/paas/v4/"
    
    # 使用 httpx 创建带代理的 client (如果需要)
    # 智谱 API 通常在国内，可能不需要代理，但如果 OpenAI 库强制走代理则需要确保代理通畅
    client = OpenAI(
        api_key=api_key, 
        base_url=base_url,
        http_client=httpx.Client(proxy=None) # 尝试直连智谱，因为 BigModel 通常在大陆
    )
    
    system_content = """你现在是一名专注于【AI指令工程 / 提示词技巧】的顶级博主，你的文章风格犀利且真诚，就像 Yi An 一样。你擅长把复杂的AI技术翻译成小白都能听懂的赚钱/提效方法论。

1. 核心任务
写一篇深度教学长文。
主题：如何写出让ChatGPT瞬间变聪明的“爆款提示词”？
核心内容必须包含：
- 为什么你的AI只会废话？（痛点分析）
- 顶级提示词的万能公式（角色+任务+要求+风格）。
- 3个实战对比案例。
- 一套可直接复制的“万能爆款写作提示词”。

字数要求：2000字以上，情感充沛，充满网感。
特殊要求：在正文中合适位置插入 [图片：XXX场景] 占位符。
格式要求：文章第一行必须是最终选定的爆款标题，第二行空行，第三行开始正文。严禁Markdown符号。

请开始写作。"""

    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": system_content}],
            temperature=0.8
        )
        
        content = response.choices[0].message.content
        
        # 确保保存到正确的目录
        output_path = pathlib.Path("f:/公众号写作/My_Wechat_Matrix/accounts/Account_A_CrossBorder/output.txt")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding='utf-8')
        print(f"✅ 文章生成成功: {output_path}")
    except Exception as e:
        print(f"❌ 生成失败: {e}")

if __name__ == "__main__":
    generate()
