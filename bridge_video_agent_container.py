import os
import sys
import json
import time
import argparse
from pathlib import Path

# ==========================================
# Configuration
# ==========================================
# This path must match the volume mount in docker-compose.yml
# /Users/ax/wechat-publisher/video_tasks -> /app/wechat-publisher/video_tasks
if os.path.exists("/app"):
    TASK_DIR = Path("/app/wechat-publisher/video_tasks")
else:
    # Fallback for local testing on host
    TASK_DIR = Path("/Users/ax/wechat-publisher/video_tasks")

def create_task(subject, script, platform="tencent", chat_id="unknown"):
    """
    Creates a JSON task file for the host watcher to pick up.
    """
    if not TASK_DIR.exists():
        try:
            TASK_DIR.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"❌ Error creating task directory: {e}")
            return None

    task_id = f"task_{int(time.time())}"
    task_file = TASK_DIR / f"{task_id}.json"
    
    task_data = {
        "id": task_id,
        "subject": subject,
        "script": script,
        "platform": platform,
        "chat_id": chat_id,
        "status": "pending",
        "created_at": time.time()
    }

    try:
        with open(task_file, "w", encoding="utf-8") as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Video Task Created: {task_file}")
        print(f"   Subject: {subject}")
        print("   Waiting for Host Watcher to process...")
        return str(task_file)
    except IOError as e:
        print(f"❌ Failed to write task file: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="AI Video Bridge (Hot Folder Mode)")
    parser.add_argument("--subject", required=True, help="Video Subject")
    parser.add_argument("--script", required=True, help="Video Script")
    parser.add_argument("--platform", default="tencent", help="Platform")
    parser.add_argument("--chat_id", default="unknown", help="Session ID for callback")
    
    args = parser.parse_args()
    
    # Create the task file
    task_path = create_task(args.subject, args.script, args.platform, args.chat_id)
    
    if task_path:
        # We output a specific success message that the bot can understand
        print(f"✨ Task queued successfully. File: {task_path}")
    else:
        print("❌ Failed to queue task.")
        sys.exit(1)

if __name__ == "__main__":
    main()
