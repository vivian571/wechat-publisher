#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MoneyPrinterTurbo → 抖音自动上传桥接脚本
监控视频生成目录，自动调用 social-auto-upload 发布到抖音
"""

import os
import sys
import time
import json
import hashlib
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List

# ============================================================================
# 配置区
# ============================================================================
# 抖音账号名（必须与登录时使用的账号名一致）
DOUYIN_ACCOUNT = "my_account"

# 监控间隔（秒）
MONITOR_INTERVAL = 60

# 失败重试次数
MAX_RETRIES = 3

# 项目路径
BASE_DIR = Path(__file__).parent.resolve()
MONEYPRINTER_DIR = BASE_DIR / "MoneyPrinterTurbo"
SOCIAL_UPLOAD_DIR = BASE_DIR / "social-auto-upload"
TASKS_DIR = MONEYPRINTER_DIR / "storage" / "tasks"

# 历史记录文件
HISTORY_FILE = BASE_DIR / "upload_history.json"

# 日志配置
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "auto_upload_bridge.log"

# ============================================================================
# 日志系统
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# 工具函数
# ============================================================================
def calculate_file_hash(file_path: Path) -> str:
    """计算文件 MD5 哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def load_upload_history() -> Dict:
    """加载上传历史"""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载历史记录失败: {e}，将创建新记录")
    return {"uploads": []}


def save_upload_history(history: Dict):
    """保存上传历史"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def is_uploaded(file_hash: str, history: Dict) -> bool:
    """检查文件是否已上传"""
    return any(record['file_hash'] == file_hash for record in history['uploads'])


def extract_title_from_task(task_dir: Path) -> str:
    """从任务目录提取标题"""
    # 优先从 script.json 提取标题 (MoneyPrinterTurbo 生成的元数据)
    script_file = task_dir / "script.json"
    if script_file.exists():
        try:
            with open(script_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # MoneyPrinterTurbo 结构: params -> video_subject
                params = data.get("params", {})
                title = params.get("video_subject", "")
                
                if title:
                    logger.info(f"从 script.json 提取标题: {title}")
                    return title
        except Exception as e:
            logger.warning(f"读取 script.json 失败: {e}")

    # 其次从 subtitle.srt 提取第一句
    srt_file = task_dir / "subtitle.srt"
    if srt_file.exists():
        try:
            with open(srt_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # SRT 格式：序号、时间轴、字幕文本
                for i, line in enumerate(lines):
                    if line.strip() and not line[0].isdigit() and '-->' not in line:
                        title = line.strip()[:50]  # 限制长度
                        logger.info(f"从字幕提取标题: {title}")
                        return title
        except Exception as e:
            logger.warning(f"读取字幕失败: {e}")
    
    # 备选：使用任务 ID
    task_id = task_dir.name
    return f"AI生成视频_{task_id[:8]}"


# ============================================================================
# 核心上传逻辑
# ============================================================================
def upload_to_douyin(video_path: Path, task_dir: Path) -> bool:
    """
    上传视频到抖音
    
    Args:
        video_path: 视频文件路径
        task_dir: 任务目录（用于提取元数据）
    
    Returns:
        是否上传成功
    """
    title = extract_title_from_task(task_dir)
    
    # --- 关键修改：生成 social-auto-upload 识别的 sidecar metadata 文件 ---
    # 它的逻辑是优先读取同名 .json 文件
    metadata_path = video_path.with_suffix('.json')
    try:
        metadata = {
            "title": title,
            "tags": [] # 暂时留空，后续可支持从 script.json 提取 keywords
        }
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False)
        logger.info(f"已创建元数据文件: {metadata_path.name}")
    except Exception as e:
        logger.error(f"创建元数据文件失败: {e}")
    # -------------------------------------------------------------
    
    # 构建上传命令
    cmd = [
        sys.executable,
        str(SOCIAL_UPLOAD_DIR / "cli_main.py"),
        "douyin",
        DOUYIN_ACCOUNT,
        "upload",
        str(video_path)
    ]
    
    logger.info(f"开始上传: {video_path.name}")
    logger.info(f"标题: {title}")
    logger.info(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 清除代理环境变量（避免干扰）
        env = os.environ.copy()
        env['HTTP_PROXY'] = ''
        env['HTTPS_PROXY'] = ''
        
        result = subprocess.run(
            cmd,
            cwd=str(SOCIAL_UPLOAD_DIR),
            env=env,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300  # 5分钟超时
        )
        
        if result.returncode == 0:
            logger.info(f"✅ 上传成功: {video_path.name}")
            logger.debug(f"输出: {result.stdout}")
            return True
        else:
            logger.error(f"❌ 上传失败: {video_path.name}")
            logger.error(f"错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ 上传超时: {video_path.name}")
        return False
    except Exception as e:
        logger.error(f"❌ 上传异常: {e}")
        return False


def process_video(video_path: Path, task_dir: Path, history: Dict) -> bool:
    """
    处理单个视频（带重试）
    
    Returns:
        是否最终成功
    """
    file_hash = calculate_file_hash(video_path)
    
    # 去重检查
    if is_uploaded(file_hash, history):
        logger.info(f"⏭️  视频已上传过，跳过: {video_path.name}")
        return True
    
    # 重试逻辑
    for attempt in range(1, MAX_RETRIES + 1):
        logger.info(f"第 {attempt}/{MAX_RETRIES} 次尝试上传...")
        
        if upload_to_douyin(video_path, task_dir):
            # 记录成功
            history['uploads'].append({
                'file_hash': file_hash,
                'file_path': str(video_path),
                'task_id': task_dir.name,
                'upload_time': datetime.now().isoformat(),
                'status': 'success',
                'platform': 'douyin',
                'account': DOUYIN_ACCOUNT
            })
            save_upload_history(history)
            return True
        
        if attempt < MAX_RETRIES:
            wait_time = 10 * attempt
            logger.warning(f"等待 {wait_time} 秒后重试...")
            time.sleep(wait_time)
    
    # 所有重试失败
    logger.error(f"❌ 达到最大重试次数，放弃上传: {video_path.name}")
    history['uploads'].append({
        'file_hash': file_hash,
        'file_path': str(video_path),
        'task_id': task_dir.name,
        'upload_time': datetime.now().isoformat(),
        'status': 'failed',
        'platform': 'douyin',
        'account': DOUYIN_ACCOUNT
    })
    save_upload_history(history)
    return False


# ============================================================================
# 监控主循环
# ============================================================================
def scan_for_new_videos() -> List[tuple]:
    """
    扫描新生成的视频
    
    Returns:
        [(video_path, task_dir), ...]
    """
    new_videos = []
    
    if not TASKS_DIR.exists():
        logger.warning(f"任务目录不存在: {TASKS_DIR}")
        return new_videos
    
    for task_dir in TASKS_DIR.iterdir():
        if not task_dir.is_dir():
            continue
        
        # 查找 final-*.mp4
        for video_file in task_dir.glob("final-*.mp4"):
            new_videos.append((video_file, task_dir))
    
    return new_videos


def main_loop():
    """主监控循环"""
    logger.info("=" * 60)
    logger.info("🚀 视频自动上传桥接服务启动")
    logger.info(f"📂 监控目录: {TASKS_DIR}")
    logger.info(f"📱 抖音账号: {DOUYIN_ACCOUNT}")
    logger.info(f"⏱️  扫描间隔: {MONITOR_INTERVAL} 秒")
    logger.info("=" * 60)
    
    # 环境检查
    if not SOCIAL_UPLOAD_DIR.exists():
        logger.error(f"❌ social-auto-upload 目录不存在: {SOCIAL_UPLOAD_DIR}")
        sys.exit(1)
    
    cookie_file = SOCIAL_UPLOAD_DIR / "cookies" / f"douyin_{DOUYIN_ACCOUNT}.json"
    if not cookie_file.exists():
        logger.error(f"❌ 未找到抖音 Cookie: {cookie_file}")
        logger.error("请先执行登录: python cli_main.py douyin my_account login")
        sys.exit(1)
    
    logger.info("✅ 环境检查通过，开始监控...")
    
    history = load_upload_history()
    
    while True:
        try:
            videos = scan_for_new_videos()
            
            if videos:
                logger.info(f"🔍 发现 {len(videos)} 个视频待处理")
                
                for video_path, task_dir in videos:
                    logger.info(f"\n{'='*60}")
                    logger.info(f"📹 处理视频: {video_path.name}")
                    logger.info(f"📁 任务ID: {task_dir.name}")
                    
                    process_video(video_path, task_dir, history)
            
            # 等待下次扫描
            time.sleep(MONITOR_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("\n👋 收到停止信号，正在退出...")
            break
        except Exception as e:
            logger.error(f"❌ 监控循环异常: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(MONITOR_INTERVAL)


if __name__ == "__main__":
    main_loop()
