from datetime import timedelta

from datetime import datetime
from pathlib import Path
import json
from conf import BASE_DIR


def get_absolute_path(relative_path: str, base_dir: str = None) -> str:
    # Convert the relative path to an absolute path
    absolute_path = Path(BASE_DIR) / base_dir / relative_path
    return str(absolute_path)


def get_title_and_hashtags(filename):
    """
    获取视频标题和 hashtag
    优先读取同名配置文件 (.json > .yaml > .txt)
    如果不存在，则使用默认策略生成

    Args:
        filename: 视频文件名

    Returns:
        title (str): 视频标题
        hashtags (list): hashtag 列表
    """
    video_path = Path(filename)
    base_path = video_path.with_suffix('')
    
    # 1. 尝试读取 JSON 配置
    json_path = base_path.with_suffix('.json')
    if json_path.exists():
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get('title', video_path.stem), data.get('tags', [])
        except Exception as e:
            print(f"读取 JSON 失败: {e}")

    # 2. 尝试读取 YAML 配置 (需安装 PyYAML)
    try:
        import yaml
        yaml_path = base_path.with_suffix('.yaml')
        if yaml_path.exists():
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data.get('title', video_path.stem), data.get('tags', [])
    except ImportError:
        pass
    except Exception as e:
        print(f"读取 YAML 失败: {e}")

    # 3. 尝试读取 TXT 配置 (原有逻辑)
    txt_path = base_path.with_suffix('.txt')
    if txt_path.exists():
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    lines = content.split("\n")
                    title = lines[0].strip()
                    # 处理标签：支持空格或逗号分隔，移除 #
                    tags_line = lines[1] if len(lines) > 1 else ""
                    tags = []
                    for tag in tags_line.replace("#", " ").replace(",", " ").split():
                        if tag.strip():
                            tags.append(tag.strip())
                    return title, tags
        except Exception as e:
            print(f"读取 TXT 失败: {e}")

    # 4. 默认回退策略
    print(f"未找到配置文件，使用文件名作为标题: {filename}")
    return video_path.stem, []


def generate_schedule_time_next_day(total_videos, videos_per_day = 1, daily_times=None, timestamps=False, start_days=0):
    """
    Generate a schedule for video uploads, starting from the next day.

    Args:
    - total_videos: Total number of videos to be uploaded.
    - videos_per_day: Number of videos to be uploaded each day.
    - daily_times: Optional list of specific times of the day to publish the videos.
    - timestamps: Boolean to decide whether to return timestamps or datetime objects.
    - start_days: Start from after start_days.

    Returns:
    - A list of scheduling times for the videos, either as timestamps or datetime objects.
    """
    if videos_per_day <= 0:
        raise ValueError("videos_per_day should be a positive integer")

    if daily_times is None:
        # Default times to publish videos if not provided
        daily_times = [6, 11, 14, 16, 22]

    if videos_per_day > len(daily_times):
        raise ValueError("videos_per_day should not exceed the length of daily_times")

    # Generate timestamps
    schedule = []
    current_time = datetime.now()

    for video in range(total_videos):
        day = video // videos_per_day + start_days + 1  # +1 to start from the next day
        daily_video_index = video % videos_per_day

        # Calculate the time for the current video
        hour = daily_times[daily_video_index]
        time_offset = timedelta(days=day, hours=hour - current_time.hour, minutes=-current_time.minute,
                                seconds=-current_time.second, microseconds=-current_time.microsecond)
        timestamp = current_time + time_offset

        schedule.append(timestamp)

    if timestamps:
        schedule = [int(time.timestamp()) for time in schedule]
    return schedule
