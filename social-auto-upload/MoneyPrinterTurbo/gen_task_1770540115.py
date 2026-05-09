
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
    print(f"IMPORT_ERROR: {e}")
    sys.exit(1)

async def run():
    print("   -> Initializing MPT task...")
    params = TaskVideoRequest(
        video_subject='TestSubject',
        video_script='Test Script Content',
        video_aspect="9:16",
        video_source="pexels",
        voice_name="zh-CN-YunxiNeural",
        subtitle_enabled=True
    )
    # Use task_id as the MPT task id for traceability
    task_id = "task_1770540115"
    print(f"TASK_ID:{task_id}")
    
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
