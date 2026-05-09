# -*- coding: utf-8 -*-
"""
视频去重与防风控模块 (Magic Edit)
利用 FFmpeg 对视频进行微调（画面裁剪、色调偏移、MD5修改等）以规避平台重复检测。
"""

import os
import subprocess
import random
import string
from pathlib import Path
from typing import Optional, List, Dict

class VideoMagicEditor:
    """视频魔改去重器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        try:
            subprocess.run([self.ffmpeg_path, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        except Exception:
            print(f"警告：FFmpeg 未找到，Magic Edit 功能将受限。")

    def change_md5(self, video_path: str) -> bool:
        """通过向文件末尾添加随机字节来修改 MD5"""
        try:
            with open(video_path, 'ab') as f:
                # 添加 1 字节随机数据足以改变 MD5
                f.write(os.urandom(1))
            return True
        except Exception as e:
            print(f"MD5 修改失败: {e}")
            return False

    def apply_magic_edit(
        self, 
        input_path: str, 
        output_path: str, 
        config: Optional[Dict] = None
    ) -> bool:
        """
        全量魔改：裁剪、缩放、色调偏移、帧率微调
        """
        if config is None:
            config = {
                'crop': True,
                'scale': True,
                'color': True,
                'flip': False,
                'speed': True,
                'metadata': True
            }

        input_path = str(Path(input_path).absolute())
        output_path = str(Path(output_path).absolute())

        # 构建 FFmpeg 滤镜链
        filters = []

        # 1. 随机裁剪 (1%-2%)
        if config.get('crop'):
            # crop=w:h:x:y
            # 假设视频是正常比例，我们裁掉边缘的一点点
            # 由于不能在这里直接获取视频宽高，我们使用相对比例
            filters.append("crop=iw*0.98:ih*0.98:iw*0.01:ih*0.01")

        # 2. 随机缩放回原大小 (防止黑边并改变像素布局)
        if config.get('scale'):
            filters.append("scale=iw:ih")

        # 3. 色调微调 (亮度、对比度、饱和度、伽马值 +/- 0.05)
        if config.get('color'):
            b = round(random.uniform(-0.02, 0.02), 3) # 亮度
            c = round(random.uniform(0.98, 1.02), 3)  # 对比度
            s = round(random.uniform(0.98, 1.02), 3)  # 饱和度
            g = round(random.uniform(0.98, 1.02), 3)  # 伽马
            filters.append(f"eq=brightness={b}:contrast={c}:saturation={s}:gamma={g}")

        # 4. 水平镜像 (可选，某些内容不适合镜像)
        if config.get('flip'):
            filters.append("hflip")

        # 5. 帧率/速度极细微调整 (100.1% 或 99.9% 速度)
        # 这种微调人眼无法察觉，但可以改变编码帧序列
        if config.get('speed'):
            # setpts=1.001*PTS 或 0.999*PTS
            speed_factor = random.choice([1.001, 0.999])
            filters.append(f"setpts={speed_factor}*PTS")

        filter_str = ",".join(filters)

        cmd = [
            self.ffmpeg_path,
            "-i", input_path,
            "-vf", filter_str,
            "-c:v", "libx264",
            "-crf", "20",       # 保持较高画质
            "-preset", "veryfast",
            "-c:a", "copy",     # 音频尝试直接复制以提高速度
            "-y",               # 覆盖输出
        ]

        # 6. 清理元数据
        if config.get('metadata'):
            cmd.extend(["-map_metadata", "-1"])

        cmd.append(output_path)

        try:
            print(f"正在执行 Magic Edit: {input_path} -> {output_path}")
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if process.returncode == 0:
                print("Magic Edit 成功！")
                # 修改 MD5 确保万无一失
                self.change_md5(output_path)
                return True
            else:
                print(f"Magic Edit 失败: {process.stderr}")
                return False
        except Exception as e:
            print(f"执行 FFmpeg 命令出错: {e}")
            return False

# 辅助函数
def apply_deduplication(video_path: str, suffix: str = "_edit") -> str:
    """
    对单个视频应用去重的便捷入口
    """
    path = Path(video_path)
    output_path = path.parent / f"{path.stem}{suffix}{path.suffix}"
    
    editor = VideoMagicEditor()
    success = editor.apply_magic_edit(str(path), str(output_path))
    
    return str(output_path) if success else video_path

if __name__ == "__main__":
    print("VideoMagicEditor 模块加载成功")
