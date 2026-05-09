
import os
import sys
import asyncio

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import time
import json
import hashlib
from pathlib import Path
from loguru import logger

# ================= 配置区 =================
# 小说根目录
NOVEL_DIR = Path(r"f:\公众号写作\小说\撰写提示词书籍")
# 进度记录文件
PROGRESS_FILE = Path("fiction_video_progress.json")
# 每个视频截取的最大字数（防止超时）
MAX_CHARS = 1000
# 扫描间隔（秒）
INTERVAL = 5
# =========================================

# 添加项目根目录到 Python 路径
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.append(str(PROJECT_ROOT))

try:
    from app.services import task as tm
    from app.services import llm  # 导入 LLM 服务用于文案改写
    from app.models.schema import TaskVideoRequest
    from app.utils import utils
except ImportError as e:
    logger.error(f"❌ 导入模块失败: {e}")
    sys.exit(1)

def rewrite_for_video(original_text: str, title: str) -> str:
    """
    使用 LLM 将原文改写为适合短视频的吸引人文案
    
    Args:
        original_text: 原始小说文本
        title: 章节标题
    
    Returns:
        改写后的视频文案
    """
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
        logger.info("🤖 正在调用 AI 改写文案...")
        rewritten = llm.generate_script(video_subject=title, language="zh-CN", prompt_override=prompt)
        
        if rewritten and "Error:" not in rewritten:
            logger.success(f"✅ 文案改写完成，长度: {len(rewritten)} 字")
            return rewritten
        else:
            logger.warning(f"⚠️  AI 改写失败，使用原文: {rewritten}")
            return original_text[:300]  # 降级方案
    except Exception as e:
        logger.error(f"❌ 文案改写异常: {e}")
        return original_text[:300]

def load_progress():
    if PROGRESS_FILE.exists():
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"processed_files": []}

def save_progress(progress):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def calculate_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def process_chapter(file_path: Path):
    progress = load_progress()
    file_hash = calculate_file_hash(file_path)
    
    # 检查是否已处理（基于路径和内容哈希）
    for record in progress['processed_files']:
        if record['path'] == str(file_path) and record['hash'] == file_hash:
            logger.info(f"⏭️  跳过已处理文件: {file_path.name}")
            return

    logger.info(f"📖 开始处理章节: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            logger.warning(f"⚠️  文件为空: {file_path.name}")
            return

        # 提取标题
        title = file_path.stem.split(" ")[-1][:20]
        
        # 先读取较长的原文用于改写（1000字）
        original_content = content[:1000]
        
        # 🔥 关键改进：调用 AI 改写为短视频文案
        script_content = rewrite_for_video(original_content, title)
        
        # 关键词生成：简单使用标题，或留给 LLM 生成
        # 这里为了省事，可以直接用标题
        
        # 构建请求
        params = TaskVideoRequest(
            video_subject=title,
            video_script=script_content,
            video_terms=title, # 简单设为标题，或者留空让 LLM 生成
            video_source="pexels",
            video_concat_mode="random",
            video_aspect="9:16",
            video_clip_duration=3,
            voice_name="zh-CN-YunxiNeural", # 云希语音
            voice_rate=0.8, # 语速 80%（慢速，更清晰）
            subtitle_enabled=True
        )

        task_id = utils.get_uuid()
        logger.info(f"🚀 提交任务 ID: {task_id} | 标题: {title}")
        
        # 调用生成服务 (同步阻塞)
        tm.start(task_id, params)
        
        logger.success(f"✅ 生成完成: {file_path.name}")
        
        # 记录进度
        progress['processed_files'].append({
            "path": str(file_path),
            "hash": file_hash,
            "task_id": task_id,
            "timestamp": time.time()
        })
        save_progress(progress)
        
    except Exception as e:
        logger.error(f"❌ 处理失败 {file_path.name}: {e}")

def main():
    logger.info(f"📂 扫描小说目录: {NOVEL_DIR}")
    
    # 递归遍历所有 txt 文件
    txt_files = sorted(NOVEL_DIR.rglob("*.txt"))
    
    # 过滤掉非章节文件（系统文件或大纲）
    valid_files = [
        f for f in txt_files 
        if "大纲" not in f.name 
        and "提示词" not in f.name 
        and f.stat().st_size > 100 # 忽略太小的文件
    ]
    
    logger.info(f"🔍 找到 {len(valid_files)} 个有效章节文件")
    
    for file_path in valid_files:
        process_chapter(file_path)
        # 短暂休息，避免并发太高（虽然这里是同步的，但给 GPU 喘息机会）
        time.sleep(2)

if __name__ == "__main__":
    main()
