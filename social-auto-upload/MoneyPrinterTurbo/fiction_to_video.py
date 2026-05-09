
import os
import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import time
import json
from pathlib import Path

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.append(str(PROJECT_ROOT))

# 导入 MoneyPrinterTurbo 核心模块
try:
    from app.services import task as tm
    from app.services import llm
    from app.models.schema import TaskVideoRequest
    from app.utils import utils
    from loguru import logger
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    print("请确保在 MoneyPrinterTurbo 目录下运行此脚本，并激活了虚拟环境")
    sys.exit(1)

def rewrite_for_video(original_text: str, title: str) -> str:
    """使用 LLM 将原文改写为适合短视频的吸引人文案"""
    prompt = f"""你是一位短视频文案专家。请将以下书籍内容改写为一段吸引人的短视频文案（60秒以内）。

要求：
1. 开头必须有强烈的钩子，吸引观众停留
2. 语言要口语化、有节奏感，适合朗读
3. 突出核心观点和金句
4. 结尾要有行动号召或引发思考
5. 控制在 200-300 字以内

章节标题：{title}

原文内容：
{original_text}

请直接输出改写后的文案，不要有任何前缀说明："""

    try:
        print("🤖 正在调用 AI 改写文案...")
        rewritten = llm.generate_script(video_subject=title, language="zh-CN")
        
        # 由于 generate_script 不支持 prompt_override，我们需要直接调用底层函数
        # 这里简化处理，直接用原 API
        from app.services.llm import _generate_response
        rewritten = _generate_response(prompt=prompt)
        
        if rewritten and "Error:" not in rewritten:
            print(f"✅ 文案改写完成，长度: {len(rewritten)} 字")
            return rewritten
        else:
            print(f"⚠️  AI 改写失败，使用原文摘要")
            return original_text[:300]
    except Exception as e:
        print(f"❌ 文案改写异常: {e}")
        return original_text[:300]

def generate_video_from_file(file_path: Path):
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return

    print(f"📖 正在读取: {file_path.name}")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return

    # 提取标题（文件名去后缀）
    title = file_path.stem.split(" ")[-1] # 取 "1.1 标题" 中的 "标题" 部分
    if len(title) > 20: 
        title = title[:20]

    # 读取原文用于改写
    original_content = content[:1000]
    
    # 🔥 调用 AI 改写为短视频文案
    script_content = rewrite_for_video(original_content, title)
    
    print(f"🎬 视频主题: {title}")
    print(f"📝 改写后文案长度: {len(script_content)} 字符")

    # 构建请求参数
    # 参考 app/models/schema.py 中的默认值
    params = TaskVideoRequest(
        video_subject=title,
        video_script=script_content, # 直接使用小说内容作为脚本，跳过 LLM 写稿
        video_terms=title, # 关键词简单设为标题，或者留空让内部生成
        video_source="pexels",
        video_concat_mode="random",
        video_aspect="9:16", # 竖屏
        video_clip_duration=3,
        voice_name="zh-CN-YunxiNeural", # 云希语音
        voice_rate=0.8, # 语速 80%（慢速，更清晰）
        subtitle_enabled=True
    )

    task_id = utils.get_uuid()
    print(f"🚀 开始生成任务 ID: {task_id}")
    
    try:
        # 这里直接调用 Service 层的 start 方法
        # 注意: tm.start 可能是一个耗时操作，或者它会将任务放入后台队列
        # 观察 video.py, tm.start 是被 task_manager.add_task 调用的
        # 但如果我们直接调 tm.start，它将在当前线程执行
        result = tm.start(task_id, params)
        print(f"✅ 视频生成完成！")
        print(f"📁 输出目录: storage/tasks/{task_id}")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 硬编码测试文件路径
    # 指挥官可以修改这里来指向不同的章节
    target_file = Path(r"f:\公众号写作\小说\撰写提示词书籍\第一章引言\1.1 什么是提示词工程：开启 AI 时代的“暗号”.txt")
    
    generate_video_from_file(target_file)
