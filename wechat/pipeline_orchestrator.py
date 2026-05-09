import os
import glob
import json
import requests
from pathlib import Path

# ---------------- 配置区 ----------------
OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b-local"  # 使用轻量级高频模型

# 目录配置
BASE_DIR = "/Users/ax/wechat-publisher/wechat/documents"
APPROVED_TAG = "_approved"
REJECTED_TAG = "_rejected"

# ---------------- Agent 身份设定 ----------------
# 审核员 (Auditor) 的系统指令
AUDITOR_SYSTEM_PROMPT = """你是一个极其严格的短视频文案主编 (Auditor)。
你的任务是审核底下的撰稿人提交的短视频脚本。
审核标准：
1. 是否有吸引人的“黄金三秒”开头（Hook）？
2. 语言是否口语化，适合短视频口播？
3. 字数是否精简，没有废话？
4. 是否包含诱导用户点赞、评论、关注的结尾（CTA）？

请严格输出 JSON 格式的结果（只输出 JSON，不要有任何 Markdown 代码块包裹，也不要有额外文字）：
{
    "approved": true 或 false,
    "feedback": "如果拒绝，请给出具体的重写指导意见。如果通过，请写'审核通过'。"
}
"""

# 撰稿人 (Writer) 的系统指令 (用于根据反馈重写)
WRITER_SYSTEM_PROMPT = """你是一个爆款短视频文案写手。
主编刚刚打回了你的稿件，并给出了修改意见。
请你根据主编的意见，**重新改写**这篇文案。
务必只输出修改后的纯文本内容，不要包含任何多余的寒暄和解释。"""

def call_auditor_agent(content: str) -> dict:
    """调用 Auditor 特工进行审核"""
    print("   [Auditor] 正在仔细审阅稿件...")
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
                {"role": "user", "content": f"请审核以下稿件：\n\n{content}"}
            ],
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.3}
        }
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        result_text = response.json()["message"]["content"]
        return json.loads(result_text)
    except Exception as e:
        print(f"   [Auditor Error] 审核过程出错: {e}")
        return {"approved": False, "feedback": "系统错误，未能完成审核。"}

def call_writer_agent(original_content: str, feedback: str) -> str:
    """调用 Writer 特工进行重写"""
    print(f"   [Writer] 收到主编反馈: {feedback}")
    print("   [Writer] 正在疯狂重写中...")
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": WRITER_SYSTEM_PROMPT},
                {"role": "user", "content": f"【主编修改意见】:\n{feedback}\n\n【原稿件】:\n{original_content}\n\n请严格根据意见输出改写后的新文案。"}
            ],
            "stream": False,
            "options": {"temperature": 0.7}
        }
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"].strip()
    except Exception as e:
        print(f"   [Writer Error] 重写过程出错: {e}")
        return original_content

def process_pipeline():
    print("🚀 正在启动【矩阵自动化流转车间】...")
    
    # 查找所有未审核、也未被打回的 .md 文件
    search_pattern = os.path.join(BASE_DIR, "*", "*.md")
    all_files = glob.glob(search_pattern)
    
    pending_files = [f for f in all_files if APPROVED_TAG not in f and REJECTED_TAG not in f]
    
    if not pending_files:
        print("✅ 当前没有需要审核的稿件。车间休息中...")
        return

    print(f"📦 发现 {len(pending_files)} 篇待审核稿件。开始流水线作业...\n")

    for file_path in pending_files:
        path_obj = Path(file_path)
        account_name = path_obj.parent.name
        print(f"📄 正在处理账号【{account_name}】的稿件: {path_obj.name}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Step 1: 审核员登场
        audit_result = call_auditor_agent(content)
        
        if audit_result.get("approved"):
            print("   ✅ [Auditor 裁决]: 审核通过！放行进入渲染车间。")
            # 重命名文件，打上通过标签
            new_path = file_path.replace(".md", f"{APPROVED_TAG}.md")
            os.rename(file_path, new_path)
        else:
            print(f"   ❌ [Auditor 裁决]: 稿件被打回。原因: {audit_result.get('feedback')}")
            # Step 2: 撰稿人根据反馈重写
            new_content = call_writer_agent(content, audit_result.get("feedback"))
            
            # 将新稿件保存回原文件，等待下一轮审核
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("   🔄 [Pipeline]: 重写完成，已保存为新版本，将在下一轮被重新审核。")
        
        print("-" * 50)

if __name__ == "__main__":
    process_pipeline()
