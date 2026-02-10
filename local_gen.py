import sys
import os
import uuid
from pathlib import Path

# Add MPT to path
sys.path.append("/app/wechat-publisher/MoneyPrinterTurbo")
os.chdir("/app/wechat-publisher/MoneyPrinterTurbo") 

# Import MPT modules
from app.services import task as tm
from app.models.schema import VideoParams, VideoAspect

def run():
    subject = "马斯克的第一性原理"
    script = """埃隆·马斯克造火箭、做电动车，凭什么都能成？因为他从不类比思考，只用第一性原理。
大多数人遇到问题，习惯看别人怎么做，这叫“照葫芦画瓢”。结果只能做出改良品，做不出颠覆品。
第一性原理，就是把事情拆解到物理学的最基本事实。
就像电池，别人说成本600美元降不下来。马斯克却把电池拆成碳、镍、铝，发现原材料只要80美元。
中间的差价，就是你的机会！不要被现有经验束缚，回到原点，重新组合。
这一秒开始，拒绝盲从，用第一性原理重塑你的世界。关注我，每天一个思维模型。"""
    
    print(f"Start generation for {subject}")

    params = VideoParams(
        video_subject=subject,
        video_script=script,
        video_terms=["Elon Musk", "Rocket", "Battery", "Physics", "Thinking", "Innovation", "SpaceX", "Tesla"],
        video_aspect=VideoAspect.portrait,
        video_source="pexels",
        voice_name="zh-CN-YunxiNeural",
        subtitle_enabled=True,
        font_name="MicrosoftYaHeiBold.ttc"
    )
    
    task_id = str(uuid.uuid4())
    print(f"TASK_ID:{task_id}")
    
    try:
        tm.start(task_id, params)
        print("Generation completed successfully.")
        # Find output file
        output_dir = Path(f"/app/wechat-publisher/MoneyPrinterTurbo/storage/tasks/{task_id}")
        final_video = output_dir / "final-1.mp4"
        if final_video.exists():
            print(f"VIDEO_PATH:{final_video}")
        else:
            print("Video file not found.")
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run()
