import sys
import os
import asyncio
from pathlib import Path

# 将项目根目录添加到 python 搜索路径
current_file_path = Path(__file__).resolve()
project_root = current_file_path.parent.parent
sys.path.append(str(project_root))

from conf import BASE_DIR
from uploader.douyin_uploader.main import douyin_setup, DouYinVideo
from utils.files_times import generate_schedule_time_next_day, get_title_and_hashtags


if __name__ == '__main__':
    filepath = Path(BASE_DIR) / "videos"
    account_file = Path(BASE_DIR / "cookies" / "douyin_uploader" / "account.json")
    
    # 检查 cookie 文件是否存在
    if not account_file.exists():
        print(f"⚠️ 提示: 未找到 Cookie 文件 {account_file}。脚本将仅运行 AI 优化和封面生成演示，跳过实际上传流程。")
        can_upload = False
    else:
        print(f"✅ 已找到 Cookie 文件，将进行完整上传流程。")
        can_upload = True

    # 获取视频目录
    folder_path = Path(filepath)
    # 获取文件夹中的所有文件
    files = list(folder_path.glob("*.mp4"))
    file_num = len(files)
    
    if file_num == 0:
        print(f"❌ 错误: 在 {filepath} 目录下未找到 .mp4 视频文件。")
        sys.exit(1)

    publish_datetimes = generate_schedule_time_next_day(file_num, 1, daily_times=[16])
    
    if can_upload:
        cookie_setup = asyncio.run(douyin_setup(account_file, handle=False))
    
    # 初始化 AI 优化器、封面生成器和视频去重器
    import conf
    from utils.ai_optimizer import create_optimizer_from_config
    from utils.cover_generator import create_cover_generator_from_config
    from utils.magic_edit import VideoMagicEditor
    
    # 构建配置字典
    config_dict = {k: getattr(conf, k, None) for k in dir(conf) if k.isupper()}
    ai_optimizer = create_optimizer_from_config(config_dict)
    cover_generator = create_cover_generator_from_config(config_dict)
    
    # 初始化视频去重器
    magic_editor = None
    if config_dict.get('MAGIC_EDIT_ENABLED', False):
        magic_editor = VideoMagicEditor()
        print("🔮 视频去重功能已启用")


    for index, file in enumerate(files):
        title, tags = get_title_and_hashtags(str(file))
        
        # AI 内容优化
        if ai_optimizer:
            try:
                print(f"\n🚀 ----------- AI 优化中: {file.name} -----------")
                print(f" 原始标题: {title}")
                optimized = ai_optimizer.optimize_content(title, "douyin")
                title = optimized['title']
                tags = optimized['tags']
                print(f" ✨ 优化标题: {title}")
                print(f" #️⃣ 优化标签: {tags}")
                print(" ------------------------------------------")
            except Exception as e:
                print(f" ❌ AI 优化失败: {e}")

        thumbnail_path = file.with_suffix('.png')
        
        # 封面自动生成
        if cover_generator:
            try:
                print(f"🖼️ 正在生成封面: {file.name}")
                generated_cover = cover_generator.generate_cover(str(file), title)
                thumbnail_path = Path(generated_cover)
            except Exception as e:
                print(f" ❌ 封面生成失败: {e}")
        
        # 视频去重处理 (Magic Edit)
        final_video_path = file
        if magic_editor:
            try:
                print(f"� 正在对视频进行去重处理: {file.name}")
                # 生成去重后的视频文件名
                dedup_output = file.parent / f"{file.stem}_dedup{file.suffix}"
                magic_config = config_dict.get('MAGIC_EDIT_CONFIG', {})
                
                success = magic_editor.apply_magic_edit(
                    str(file), 
                    str(dedup_output),
                    magic_config
                )
                
                if success:
                    final_video_path = dedup_output
                    print(f" ✅ 去重成功: {dedup_output.name}")
                else:
                    print(f" ⚠️ 去重失败，将使用原始视频")
            except Exception as e:
                print(f" ❌ 视频去重失败: {e}")
                
        # 打印视频最终信息
        print(f"\n📝 最终发布信息：")
        print(f" 📁 视频文件：{final_video_path}")
        print(f" 📌 标题：{title}")
        print(f" 🏷️ 标签：{tags}")
        
        if can_upload:
            app = DouYinVideo(title, final_video_path, tags, publish_datetimes[index], account_file, thumbnail_path=thumbnail_path if thumbnail_path.exists() else None)
            asyncio.run(app.main(), debug=False)
        else:
            print(f" ⏩ 跳过实际上传步骤（演示模式）。")
