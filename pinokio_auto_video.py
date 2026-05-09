import os
import time
import requests
import json
from gradio_client import Client

# --- 端口配置 (根据用户提供) ---
LIVEPORT_PORT = "7860"
SADTALKER_PORT = "7861"
FLUX_PORT = "7862"
QWEN_TTS_PORT = "7863"

# --- 路径配置 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "video_output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- 任务文案 ---
STORY_TEXT = "别再手动刷 X 了！我让 OpenClaw 每天自动抓取 30 多个账号，运行一个月，封号次数竟然是：零。这种模拟人类行为的自动化，才是真正的数字资产生产线。"
FLUX_PROMPT = "A futuristic cyber hacker sitting in front of a high-tech Mac workstation, cinematic lighting, 8k, digital human style, medium shot."

def run_pipeline():
    try:
        print("🚀 [1/4] 正在启动造人计划 (Flux)...")
        flux_client = Client(f"http://127.0.0.1:{FLUX_PORT}/")
        # Flux API 参数根据 Pinokio 默认版通常为 (prompt, seed, width, height, guidance_scale, steps, ...)
        img_result = flux_client.predict(
            FLUX_PROMPT, 
            "",     # negative prompt
            random.randint(0, 1000000), # seed
            1024,   # width
            1024,   # height
            3.5,    # guidance
            20,     # steps
            api_name="/predict"
        )
        # 兼容不同返回格式
        image_path = img_result if isinstance(img_result, str) else img_result[0]
        print(f"✅ 形象已就绪: {image_path}")

        print("🚀 [2/4] 正在注入灵魂配音 (Qwen3-TTS)...")
        qwen_client = Client(f"http://127.0.0.1:{QWEN_TTS_PORT}/")
        audio_result = qwen_client.predict(
            STORY_TEXT,
            "Chinese", # language
            api_name="/generate"
        )
        audio_path = audio_result
        print(f"✅ 语音已生成: {audio_path}")

        print("🚀 [3/4] 正在进行对嘴合成 (SadTalker)...")
        sad_client = Client(f"http://127.0.0.1:{SADTALKER_PORT}/")
        video_result = sad_client.predict(
            image_path,   # source_image
            audio_path,   # driven_audio
            "full",       # preprocess
            True,         # still mode
            True,         # enhance
            api_name="/generate_video"
        )
        print(f"✅ 基础视频已成型: {video_result}")

        print("🚀 [4/4] 正在执行后期增强 (LivePortrait)...")
        # 注意：这里假设使用 LivePortrait 进行最后的画面细节/光影增强
        live_client = Client(f"http://127.0.0.1:{LIVEPORT_PORT}/")
        final_result = live_client.predict(
            video_result, 
            api_name="/enhance_portrait" 
        )
        
        print(f"🎊 任务圆满完成！最终视频路径: {final_result}")
        return final_result

    except Exception as e:
        print(f"❌ 流程中断: {e}")
        # 即使报错也尝试返回当前阶段结果
        return None

if __name__ == "__main__":
    import random
    run_pipeline()
