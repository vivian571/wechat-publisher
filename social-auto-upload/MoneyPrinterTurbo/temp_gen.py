
import asyncio
import os
import sys
# Add current dir to sys.path to ensure modules are found
sys.path.append(os.getcwd())

try:
    from app.services import task as tm
    from app.models.schema import TaskVideoRequest
    from app.utils import utils
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

async def run():
    params = TaskVideoRequest(
        video_subject='AI Trends',
        video_script='AI is booming everywhere.',
        video_aspect="9:16",
        video_source="pexels",
        voice_name="zh-CN-YunxiNeural",
        subtitle_enabled=True
    )
    task_id = utils.get_uuid()
    print(f"TASK_ID:{task_id}")
    # Simulation mode if backend not fully running
    print("Simulating task start...")
    # tm.start(task_id, params) 

if __name__ == "__main__":
    asyncio.run(run())
