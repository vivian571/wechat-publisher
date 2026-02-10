import os
import sys
import subprocess
import argparse
from pathlib import Path

# ==========================================
# 配置区域
# ==========================================
MONEY_PRINTER_DIR = Path("/Users/ax/wechat-publisher/MoneyPrinterTurbo")
SOCIAL_UPLOAD_DIR = Path("/Users/ax/wechat-publisher/social-auto-upload")

MPT_VENV_PYTHON = MONEY_PRINTER_DIR / "venv" / "bin" / "python3"
SAU_VENV_PYTHON = SOCIAL_UPLOAD_DIR / "venv" / "bin" / "python3"

def run_command(cmd, cwd, env=None):
    """通用命令执行器"""
    print(f"执行命令: {' '.join(map(str, cmd))} in {cwd}")
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env=env
    )
    if result.returncode != 0:
        print(f"❌ 命令失败 (code {result.returncode})")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        return False, result.stdout
    return True, result.stdout

def generate_video(subject, script):
    """
    通过调用 MoneyPrinterTurbo 的内部逻辑生成视频。
    由于 MPT 没有现成的通用生成 CLI，我们临时创建一个简单的运行脚本或者调用其现有的脚本逻辑。
    这里我们模拟 fiction_to_video.py 的逻辑，但通过子进程调用。
    """
    print(f"🎬 启动视频生成: {subject}")
    
    # 我们创建一个临时脚本来触发生成，以确保在 MPT 的 venv 中运行
    temp_script = MONEY_PRINTER_DIR / "temp_gen.py"
    script_content = f"""
import asyncio
import os
from pathlib import Path
from app.services import task as tm
from app.models.schema import TaskVideoRequest
from app.utils import utils

async def run():
    params = TaskVideoRequest(
        video_subject={repr(subject)},
        video_script={repr(script)},
        video_aspect="9:16",
        video_source="pexels",
        voice_name="zh-CN-YunxiNeural",
        subtitle_enabled=True
    )
    task_id = utils.get_uuid()
    print(f"TASK_ID:{{task_id}}")
    tm.start(task_id, params)

if __name__ == "__main__":
    asyncio.run(run())
"""
    with open(temp_script, "w") as f:
        f.write(script_content)

    success, output = run_command([MPT_VENV_PYTHON, "temp_gen.py"], MONEY_PRINTER_DIR)
    
    # 提取 Task ID
    task_id = None
    for line in output.splitlines():
        if line.startswith("TASK_ID:"):
            task_id = line.split(":")[1].strip()
    
    if success and task_id:
        video_path = MONEY_PRINTER_DIR / "storage" / "tasks" / task_id / "final-1.mp4"
        # 有些版本可能是 combined-1.mp4 或存放在不同子目录，这里做简单兼容
        if not video_path.exists():
            matches = list((MONEY_PRINTER_DIR / "storage" / "tasks" / task_id).glob("*.mp4"))
            if matches:
                video_path = matches[0]
        
        return str(video_path)
    return None

def upload_video(video_path, platform, account):
    """使用 social-auto-upload 发布视频"""
    print(f"📤 启动视频发布 -> {platform} ({account})")
    
    # 调用 cli_main.py
    cmd = [
        SAU_VENV_PYTHON,
        "cli_main.py",
        platform,
        account,
        "upload",
        video_path
    ]
    
    success, output = run_command(cmd, SOCIAL_UPLOAD_DIR)
    return success

def main():
    parser = argparse.ArgumentParser(description="AI 视频生产发布桥接工具 (V2)")
    parser.add_argument("--subject", required=True, help="视频主题")
    parser.add_argument("--script", required=True, help="视频脚本文字")
    parser.add_argument("--platform", default="tencent", choices=["douyin", "tencent"], help="发布平台")
    parser.add_argument("--account", default="main", help="账号名称")
    
    args = parser.parse_args()
    
    # 1. 生成视频
    video_file = generate_video(args.subject, args.script)
    
    # 2. 发布视频
    if video_file and os.path.exists(video_file):
        print(f"✅ 找到生成的视频: {video_file}")
        success = upload_video(video_file, args.platform, args.account)
        if success:
            print("✨ 全流程自动化完成！")
    else:
        print("❌ 视频生成失败或文件未找到")

if __name__ == "__main__":
    main()

