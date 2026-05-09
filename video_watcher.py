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
MUSIC_DIR = BASE_DIR / "music" / "energetic"

MONEY_PRINTER_DIR = BASE_DIR / "MoneyPrinterTurbo"
MPT_VENV_PYTHON = MONEY_PRINTER_DIR / "venv" / "bin" / "python3"
EDGE_TTS_CMD = MONEY_PRINTER_DIR / "venv" / "bin" / "edge-tts"

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

def generate_video_manim(code, task_id):
    """
    Renders Manim code.
    """
    print(f"📐 Manim Rendering: {task_id}")
    
    # Save code to a temp file
    manim_file = BASE_DIR / f"manim_{task_id}.py"
    try:
        with open(manim_file, "w", encoding="utf-8") as f:
            f.write(code)
    except Exception as e:
        return False, str(e)

    # Run Manim: -pql means preview (optional here), quality low (for speed), non-interactive
    # We want -ql (low quality) or -qm (medium) for automation.
    # --buffer is not needed. -o is for output name.
    # Classes in the script are usually GenScene as per skill spec.
    # Run Manim via Docker (Official Image)
    # We mount the BASE_DIR to /manim so the container can access script and write to media/
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{BASE_DIR}:/manim",
        "manimcommunity/manim:stable",
        "manim", "-ql", manim_file.name, "GenScene"
    ]
    
    success, output = run_command(cmd, BASE_DIR)
    
    # Clean up source file
    if manim_file.exists():
        os.remove(manim_file)

    if not success:
        return False, output

    # Manim 0.18+ saves to media/videos/manim_<task_id>/480p15/GenScene.mp4
    # Let's find it.
    video_dir = BASE_DIR / "media" / "videos" / f"manim_{task_id}"
    matches = list(video_dir.glob("**/GenScene.mp4"))
    
    if matches:
        return True, str(matches[0])
    
    return False, "Manim finished but video file GenScene.mp4 not found."

def add_audio_to_video(video_path, narration="", task_id=""):
    """
    Add audio (TTS + background music) to video using ffmpeg.
    Returns (success, final_video_path)
    """
    if not narration:
        # No narration, return original video
        return True, video_path
    
    print(f"🎵 Adding audio to video...")
    
    # Generate TTS audio
    tts_file = BASE_DIR / f"tts_{task_id}.mp3"
    try:
        cmd = [
            str(EDGE_TTS_CMD),
            "--voice", "zh-CN-YunxiNeural",
            "--text", narration,
            "--write-media", str(tts_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            print(f"   ❌ TTS generation failed: {result.stderr}")
            return False, f"TTS failed: {result.stderr}"
        print(f"   ✅ TTS generated: {tts_file}")
    except Exception as e:
        print(f"   ❌ TTS error: {e}")
        return False, str(e)
    
    # Find background music (if available)
    bgm_file = None
    if MUSIC_DIR.exists():
        music_files = list(MUSIC_DIR.glob("*.mp3"))
        if music_files:
            import random
            bgm_file = random.choice(music_files)
            print(f"   🎼 Using background music: {bgm_file.name}")
    
    # Merge audio with video using ffmpeg
    final_video = BASE_DIR / f"final_{task_id}.mp4"
    
    try:
        if bgm_file:
            # Mix TTS + BGM (lower BGM volume by 20dB)
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(tts_file),
                "-i", str(bgm_file),
                "-filter_complex",
                "[1:a]volume=1.0[tts];[2:a]volume=0.1,aloop=loop=-1:size=2e+09[bgm];[tts][bgm]amix=inputs=2:duration=shortest[a]",
                "-map", "0:v",
                "-map", "[a]",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(final_video)
            ]
        else:
            # Only TTS
            cmd = [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-i", str(tts_file),
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                str(final_video)
            ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            print(f"   ❌ ffmpeg failed: {result.stderr}")
            return False, f"ffmpeg failed: {result.stderr}"
        
        print(f"   ✅ Audio merged successfully")
        
        # Clean up temp files
        if tts_file.exists():
            os.remove(tts_file)
        
        return True, str(final_video)
        
    except Exception as e:
        print(f"   ❌ Audio merge error: {e}")
        return False, str(e)


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

    # Run Generation based on engine
    engine = data.get("engine", "mpt")
    if engine == "manim":
        success, result = generate_video_manim(data['code'], data['id'])
        
        # Add audio if generation succeeded and narration exists
        if success and data.get('narration'):
            print(f"   🎤 Processing narration...")
            audio_success, audio_result = add_audio_to_video(result, data['narration'], data['id'])
            if audio_success:
                result = audio_result  # Use the video with audio
            else:
                print(f"   ⚠️  Audio processing failed, using silent video: {audio_result}")
    else:
        success, result = generate_video_mpt(data['subject'], data['script'], data['id'])

    if success:
        print(f"   ✅ Generation Complete: {result}")
        
        # Move to Output Dir
        if not OUTPUT_DIR.exists():
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            
        # Standardize filename: Remove spaces and invalid chars
        safe_subject = data['subject'].replace(' ', '_').replace('/', '_')
        target_file = OUTPUT_DIR / f"{safe_subject}_{data['id']}.mp4"
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
