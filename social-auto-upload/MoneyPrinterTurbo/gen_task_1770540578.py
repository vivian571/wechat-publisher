
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
        video_subject='GitHub 爆火项目：Shannon AI 黑客',
        video_script='3000星一夜爆火！这个叫 Shannon 的 GitHub 项目彻底炸了。它不是帮你写代码，而是变身全自动 AI 黑客！给它一个 URL，它能自主规划、自主攻击、甚至自主修补漏洞。在 XBOW 测试中成功率高达 96%。这哪是工具，这简直是请了个数字版的渗透测试专家！安全圈的家人们，还没 Fork 的赶紧去看看，别等你的 Web 应用被 AI 攻破了才知道它。关注我，带你拆解更多 AI 黑科技！',
        video_aspect="9:16",
        video_source="pexels",
        voice_name="zh-CN-YunxiNeural",
        subtitle_enabled=True
    )
    # Use task_id as the MPT task id for traceability
    task_id = "task_1770540578"
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
