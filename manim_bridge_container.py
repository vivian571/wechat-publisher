import os
import sys
import json
import time
import argparse
from pathlib import Path

# ==========================================
# Configuration
# ==========================================
if os.path.exists("/app"):
    TASK_DIR = Path("/app/wechat-publisher/video_tasks")
else:
    TASK_DIR = Path("/Users/ax/wechat-publisher/video_tasks")

def create_manim_task(subject, code, chat_id="unknown", narration=""):
    if not TASK_DIR.exists():
        TASK_DIR.mkdir(parents=True, exist_ok=True)

    task_id = f"manim_{int(time.time())}"
    task_file = TASK_DIR / f"{task_id}.json"
    
    task_data = {
        "id": task_id,
        "engine": "manim",
        "subject": subject,
        "code": code,
        "chat_id": chat_id,
        "narration": narration,
        "status": "pending",
        "created_at": time.time()
    }

    try:
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Manim Task Created: {task_file}")
        return str(task_file)
    except IOError as e:
        print(f"❌ Failed to write task file: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Manim Video Bridge")
    parser.add_argument("--subject", required=True, help="Video Subject")
    parser.add_argument("--code", required=True, help="Manim Python Code")
    parser.add_argument("--chat_id", default="unknown", help="Session ID")
    parser.add_argument("--narration", default="", help="Narration text for TTS")
    
    args = parser.parse_args()
    task_path = create_manim_task(args.subject, args.code, args.chat_id, args.narration)
    
    if task_path:
        print(f"✨ Manim task queued. Task ID: {Path(task_path).stem}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
