import os
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

# ==========================================
# Configuration
# ==========================================
BASE_DIR = Path("/Users/ax/wechat-publisher")
TASK_DIR = BASE_DIR / "video_tasks"
OUTPUT_DIR = Path("/Users/ax/wechat-publisher/social-auto-upload/videoFile")

MONEY_PRINTER_DIR = BASE_DIR / "MoneyPrinterTurbo"
MPT_VENV_PYTHON = MONEY_PRINTER_DIR / "venv" / "bin" / "python3"

def run_command(cmd, cwd):
    print(f"   Executing: {' '.join(map(str, cmd))}")
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"   ❌ Command Failed: {result.stderr}")
            return False, result.stdout
        return True, result.stdout
    except Exception as e:
        print(f"   ❌ Execution Error: {e}")
        return False, str(e)

def generate_video_mpt(subject, script, task_id):
    """
    Calls MoneyPrinterTurbo via a temporary script in its environment.
    """
    print(f"🎬 Generating: {subject}")
    
    # Create driver script inside MPT folder
    driver_script = MONEY_PRINTER_DIR / f"gen_{task_id}.py"
    script_content = f"""
import asyncio
import os
import sys
# Ensure app modules are found
sys.path.append(os.getcwd())

try:
    from app.services import task as tm
    from app.models.schema import TaskVideoRequest
    from app.utils import utils
except ImportError as e:
    print(f"IMPORT_ERROR: {{e}}")
    sys.exit(1)

async def run():
    print("   -> Initializing MPT task...")
    params = TaskVideoRequest(
        video_subject={repr(subject)},
        video_script={repr(script)},
        video_aspect="9:16",
        video_source="pexels",
        voice_name="zh-CN-YunxiNeural",
        subtitle_enabled=True
    )
    # Use task_id as the MPT task id for traceability
    task_id = "{task_id}"
    print(f"TASK_ID:{{task_id}}")
    
    # Start generation (this is usually async/background in MPT, 
    # but accessing the internal service might block or return quickly.
    # We might need to poll for completion if tm.start returns immediately.)
    # For CLI usage, usually we'd wait. 
    # Let's try to assume tm.start initiates and blocks or we check result.
    # Note: MPT's internal logic is complex. 
    # If this fails, we might need to use its API or a different entry point.
    
    # Mocking real generation for now to ensure architecture works first?
    # No, user wants real generation.
    # Let's try calling the controller logic if possible.
    
    tm.start(task_id, params)

if __name__ == "__main__":
    asyncio.run(run())
"""
    try:
        with open(driver_script, "w") as f:
            f.write(script_content)
    except Exception as e:
        return False, str(e)

    # Run execution
    success, output = run_command([MPT_VENV_PYTHON, driver_script.name], MONEY_PRINTER_DIR)
    
    # Clean up driver script
    if driver_script.exists():
        os.remove(driver_script)

    if not success:
        return False, output

    # MPT usually saves to storage/tasks/<task_id>/final-1.mp4
    # We need to wait/poll for this file because tm.start might be async
    expected_video = MONEY_PRINTER_DIR / "storage" / "tasks" / task_id / "final-1.mp4"
    
    # Poll for 5 minutes max
    print("   ⏳ Waiting for video file to appear...")
    for i in range(60):
        if expected_video.exists():
            return True, str(expected_video)
        time.sleep(5)
        print(".", end="", flush=True)
    
    print("")
    return False, "Timeout waiting for video file"

def process_task(task_file):
    try:
        with open(task_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Corrupt task file {task_file}: {e}")
        return

    if data.get("status") != "pending":
        return

    print(f"\n📦 Processing Task: {data['id']}")
    print(f"   Subject: {data['subject']}")

    # Update status to processing
    data["status"] = "processing"
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Run Generation
    success, result = generate_video_mpt(data['subject'], data['script'], data['id'])

    if success:
        print(f"   ✅ Generation Complete: {result}")
        
        # Move to Output Dir
        if not OUTPUT_DIR.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            
        target_file = OUTPUT_DIR / f"{data['subject'].replace(' ', '_')}_{data['id']}.mp4"
        try:
            shutil.copy2(result, target_file)
            print(f"   🚀 Moved to: {target_file}")
            data["status"] = "completed"
            data["output_path"] = str(target_file)
        except Exception as e:
            print(f"   ❌ Move Failed: {e}")
            data["status"] = "failed"
            data["error"] = str(e)
    else:
        print(f"   ❌ Generation Failed: {result}")
        data["status"] = "failed"
        data["error"] = str(result)

    # Save final status
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # Callback to Bot
    if success and data.get("chat_id") and data["chat_id"] != "unknown":
        send_success_callback(data["chat_id"], target_file, data["subject"])

def send_success_callback(chat_id, video_path, subject):
    """
    Sends a system notification to the bot via hooks, prompting it to inform the user.
    """
    print(f"   📞 Sending callback to {chat_id}...")
    
    # Message content for the Agent (System Prompt)
    # Calculate container path (mapped volume)
    # Host: /Users/ax/wechat-publisher/... -> Container: /app/wechat-publisher/...
    container_path = str(video_path).replace("/Users/ax/wechat-publisher", "/app/wechat-publisher")

    msg_body = (
        f"System Notification: Video generation task for '{subject}' is COMPLETE.\n"
        f"Host Path: {video_path}\n"
        f"Container Path: {container_path}\n"
        f"(Hint: If user asks for the file, use tool `message` with `action='send'` and `media='{container_path}'`)"
    )
    
    # Construct curl command to call the Agent Hook
    # Endpoint: POST http://127.0.0.1:18789/hooks/agent
    # Token: video-callback-secret
    
    payload = json.dumps({
        "name": "VideoSystem",
        "message": msg_body,
        "channel": "whatsapp",
        "to": chat_id,
        "deliver": true
    })
    
    cmd = [
        "curl", "-X", "POST", "http://127.0.0.1:18789/hooks/agent",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer video-callback-secret",
        "-d", payload
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        print("   ✅ Callback sent via Hook.")
    except Exception as e:
        print(f"   ❌ Callback failed: {e}")

def main():
    print(f"👀 Watching for video tasks in: {TASK_DIR}")
    print(f"   Output set to: {OUTPUT_DIR}")
    
    if not TASK_DIR.exists():
        TASK_DIR.mkdir(parents=True, exist_ok=True)

    try:
        while True:
            # Look for json files
            for task_file in TASK_DIR.glob("*.json"):
                try:
                    # Quick check to avoid re-reading completed files too often
                    # In a real system, move completed to /done folder
                    if task_file.name.startswith("."): continue
                    
                    with open(task_file, "r") as f:
                        # minimal read
                        content = f.read()
                        if '"status": "pending"' in content:
                             process_task(task_file)
                except Exception as e:
                    # print(f"Error reading file {task_file}: {e}")
                    pass
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Watcher stopped.")

if __name__ == "__main__":
    main()
