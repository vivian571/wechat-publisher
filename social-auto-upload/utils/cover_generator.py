# -*- coding: utf-8 -*-
"""
封面生成器模块
使用 FFmpeg 提取视频关键帧，并可选地添加标题文字叠加
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import random


class CoverGenerator:
    """视频封面生成器"""

    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        初始化封面生成器

        Args:
            ffmpeg_path: FFmpeg 可执行文件路径
        """
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """检查 FFmpeg 是否可用"""
        try:
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"警告：FFmpeg 未找到或不可用（路径：{self.ffmpeg_path}）")
            print("封面生成功能将受限，请确保已安装 FFmpeg")

    def extract_keyframes(
        self,
        video_path: str,
        num_frames: int = 3,
        output_dir: Optional[str] = None,
    ) -> List[str]:
        """
        从视频中提取关键帧

        Args:
            video_path: 视频文件路径
            num_frames: 要提取的帧数
            output_dir: 输出目录（默认为视频所在目录）

        Returns:
            提取的关键帧图片路径列表
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        if output_dir is None:
            output_dir = video_path.parent
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # 获取视频时长
        duration = self._get_video_duration(str(video_path))
        if duration <= 0:
            print(f"无法获取视频时长: {video_path}")
            return []

        # 计算提取帧的时间点（避开开头和结尾）
        start_offset = max(1, duration * 0.1)  # 跳过前 10%
        end_offset = max(1, duration * 0.9)  # 跳过后 10%
        usable_duration = end_offset - start_offset

        if usable_duration <= 0:
            # 视频太短，只提取中间帧
            timestamps = [duration / 2]
        else:
            # 均匀分布提取点
            timestamps = [
                start_offset + (usable_duration / (num_frames + 1)) * (i + 1)
                for i in range(num_frames)
            ]

        # 提取关键帧
        frame_paths = []
        for i, timestamp in enumerate(timestamps):
            output_path = output_dir / f"{video_path.stem}_frame_{i + 1}.png"
            if self._extract_frame_at_timestamp(str(video_path), timestamp, str(output_path)):
                frame_paths.append(str(output_path))

        return frame_paths

    def _get_video_duration(self, video_path: str) -> float:
        """
        获取视频时长（秒）

        Args:
            video_path: 视频文件路径

        Returns:
            视频时长（秒），失败返回 0
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-f", "null",
                "-"
            ]
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # 从 stderr 中解析时长
            for line in result.stderr.split("\n"):
                if "Duration:" in line:
                    # 格式：Duration: 00:01:23.45
                    duration_str = line.split("Duration:")[1].split(",")[0].strip()
                    h, m, s = duration_str.split(":")
                    return int(h) * 3600 + int(m) * 60 + float(s)
        except Exception as e:
            print(f"获取视频时长失败: {e}")
        return 0

    def _extract_frame_at_timestamp(
        self,
        video_path: str,
        timestamp: float,
        output_path: str,
    ) -> bool:
        """
        在指定时间点提取帧

        Args:
            video_path: 视频文件路径
            timestamp: 时间点（秒）
            output_path: 输出图片路径

        Returns:
            是否成功
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-ss", str(timestamp),
                "-i", video_path,
                "-vframes", "1",
                "-q:v", "2",  # 高质量
                "-y",  # 覆盖已存在的文件
                output_path,
            ]
            subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"提取帧失败（时间点 {timestamp}s）: {e}")
            return False

    def add_title_overlay(
        self,
        image_path: str,
        title: str,
        style: str = "default",
        output_path: Optional[str] = None,
    ) -> str:
        """
        在图片上添加标题文字叠加

        Args:
            image_path: 原始图片路径
            title: 标题文字
            style: 样式（default/modern/minimal）
            output_path: 输出路径（默认覆盖原图）

        Returns:
            输出图片路径
        """
        if output_path is None:
            output_path = image_path

        try:
            # 打开图片
            img = Image.open(image_path)
            draw = ImageDraw.Draw(img)

            # 获取图片尺寸
            width, height = img.size

            # 根据样式设置参数
            if style == "modern":
                font_size = int(height * 0.08)
                text_color = (255, 255, 255)
                bg_color = (0, 0, 0, 180)  # 半透明黑色
                position = "bottom"
            elif style == "minimal":
                font_size = int(height * 0.06)
                text_color = (255, 255, 255)
                bg_color = None
                position = "top"
            else:  # default
                font_size = int(height * 0.07)
                text_color = (255, 255, 255)
                bg_color = (0, 0, 0, 150)
                position = "center"

            # 尝试加载字体（优先使用系统字体）
            font = self._get_font(font_size)

            # 计算文字尺寸
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 自动换行（如果文字太长）
            if text_width > width * 0.9:
                title = self._wrap_text(title, font, width * 0.9, draw)
                bbox = draw.textbbox((0, 0), title, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

            # 计算位置
            if position == "top":
                x = (width - text_width) // 2
                y = int(height * 0.1)
            elif position == "bottom":
                x = (width - text_width) // 2
                y = int(height * 0.85 - text_height)
            else:  # center
                x = (width - text_width) // 2
                y = (height - text_height) // 2

            # 绘制背景（如果有）
            if bg_color:
                padding = 20
                bg_bbox = [
                    x - padding,
                    y - padding,
                    x + text_width + padding,
                    y + text_height + padding,
                ]
                # 创建半透明层
                overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
                overlay_draw = ImageDraw.Draw(overlay)
                overlay_draw.rectangle(bg_bbox, fill=bg_color)
                img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
                draw = ImageDraw.Draw(img)

            # 绘制文字
            draw.text((x, y), title, font=font, fill=text_color)

            # 保存图片
            img.save(output_path, quality=95)
            return output_path

        except Exception as e:
            print(f"添加标题叠加失败: {e}")
            return image_path

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """
        获取字体

        Args:
            size: 字体大小

        Returns:
            字体对象
        """
        # 尝试常见的中文字体路径
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
            "C:/Windows/Fonts/simsun.ttc",  # 宋体
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # Linux
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue

        # 如果找不到字体，使用默认字体
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: float, draw: ImageDraw.Draw) -> str:
        """
        文字自动换行

        Args:
            text: 原始文字
            font: 字体
            max_width: 最大宽度
            draw: 绘图对象

        Returns:
            换行后的文字
        """
        words = list(text)  # 中文按字符分割
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]

            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return "\n".join(lines)

    def select_best_cover(self, image_paths: List[str]) -> str:
        """
        从多个候选图片中选择最佳封面
        当前使用简单策略：随机选择或选择中间的

        Args:
            image_paths: 候选图片路径列表

        Returns:
            最佳封面路径
        """
        if not image_paths:
            raise ValueError("候选图片列表为空")

        # 简单策略：选择中间的图片
        # 未来可以扩展为基于图像质量评分的智能选择
        return image_paths[len(image_paths) // 2]

    def generate_cover(
        self,
        video_path: str,
        title: str = "",
        style: str = "default",
        num_candidates: int = 3,
    ) -> str:
        """
        生成视频封面（完整流程）

        Args:
            video_path: 视频文件路径
            title: 标题（可选，如果提供则添加文字叠加）
            style: 封面样式
            num_candidates: 候选帧数量

        Returns:
            生成的封面图片路径
        """
        video_path = Path(video_path)

        # 1. 提取关键帧
        print(f"正在从视频提取关键帧: {video_path.name}")
        frame_paths = self.extract_keyframes(str(video_path), num_candidates)

        if not frame_paths:
            raise RuntimeError(f"无法从视频提取关键帧: {video_path}")

        # 2. 选择最佳帧
        best_frame = self.select_best_cover(frame_paths)
        print(f"选择最佳帧: {Path(best_frame).name}")

        # 3. 生成最终封面
        output_path = video_path.parent / f"{video_path.stem}_cover.png"

        # 如果提供了标题，添加文字叠加
        if title:
            print(f"添加标题叠加: {title}")
            final_cover = self.add_title_overlay(best_frame, title, style, str(output_path))
        else:
            # 直接复制最佳帧
            import shutil
            shutil.copy(best_frame, output_path)
            final_cover = str(output_path)

        # 4. 清理临时文件
        for frame_path in frame_paths:
            if frame_path != final_cover:
                try:
                    os.remove(frame_path)
                except Exception:
                    pass

        print(f"封面生成成功: {output_path.name}")
        return final_cover


# 便捷函数
def create_cover_generator_from_config(config_dict: dict) -> Optional[CoverGenerator]:
    """
    从配置字典创建封面生成器

    Args:
        config_dict: 配置字典，应包含以下键：
            - COVER_GENERATOR_ENABLED: 是否启用
            - FFMPEG_PATH: FFmpeg 路径（可选）

    Returns:
        CoverGenerator 实例，如果未启用则返回 None
    """
    if not config_dict.get("COVER_GENERATOR_ENABLED", False):
        return None

    ffmpeg_path = config_dict.get("FFMPEG_PATH", "ffmpeg")

    try:
        return CoverGenerator(ffmpeg_path=ffmpeg_path)
    except Exception as e:
        print(f"创建封面生成器失败: {e}")
        return None


if __name__ == "__main__":
    # 测试代码
    print("封面生成器模块加载成功！")
    print("依赖：FFmpeg、Pillow")
