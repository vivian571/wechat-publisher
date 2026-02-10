#!/usr/bin/env python3

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import subprocess
from pathlib import Path
from datetime import datetime
import textwrap
from typing import Optional
import tempfile
import asyncio
try:
    from gtts import gTTS
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ gTTS未安装，将创建无声视频。运行 'pip install gTTS' 安装TTS支持")

class SimpleVideoCreator:
    """简单的视频创建器，不依赖ffmpeg的drawtext滤镜"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 临时文件目录
        self.temp_dir = Path(tempfile.gettempdir()) / "simple_video_creator"
        self.temp_dir.mkdir(exist_ok=True)
        
        # 视频参数
        self.width = 1280
        self.height = 720
        self.fps = 24
        self.duration_per_slide = 3  # 每张幻灯片3秒
        self.tts_enabled = TTS_AVAILABLE
        
    def create_text_image(self, text: str, background_color=(0, 0, 0), text_color=(255, 255, 255)) -> np.ndarray:
        """创建包含文字的图像"""
        # 创建空白图像
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        img[:] = background_color
        
        # 使用PIL添加文字
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        
        # 尝试使用系统字体
        try:
            # macOS系统字体
            font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
            if not os.path.exists(font_path):
                font_path = "/System/Library/Fonts/Helvetica.ttc"
            
            font_size = 48
            font = ImageFont.truetype(font_path, font_size)
        except:
            # 如果找不到字体，使用默认字体
            font = ImageFont.load_default()
        
        # 文本换行
        max_width = self.width - 200  # 边距
        lines = textwrap.wrap(text, width=30)  # 每行大约30个字符
        
        # 计算文本总高度
        line_height = 60
        total_height = len(lines) * line_height
        
        # 从顶部开始绘制，留出边距
        y_start = 100
        
        for i, line in enumerate(lines):
            # 计算文本宽度，居中显示
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = y_start + i * line_height
            
            draw.text((x, y), line, font=font, fill=text_color)
        
        return np.array(pil_img)
    
    def create_slide_show_video(self, title: str, content: str, output_path: Path, add_audio: bool = True) -> bool:
        """创建幻灯片式视频，可选添加音频"""
        try:
            # 分割内容为多个幻灯片
            slides = self.create_slides(title, content)
            
            # 创建临时帧文件
            temp_frames = []
            
            for i, slide_text in enumerate(slides):
                # 创建图像
                img_array = self.create_text_image(slide_text)
                
                # 保存为临时文件
                temp_file = self.output_dir / f"temp_frame_{i:04d}.png"
                cv2.imwrite(str(temp_file), cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR))
                temp_frames.append(temp_file)
            
            # 生成音频（如果需要）
            audio_path = None
            if add_audio and self.tts_enabled:
                audio_path = self.create_audio_sequence(slides)
                if audio_path:
                    print(f"音频生成成功: {audio_path.name}")
                else:
                    print("音频生成失败，将创建无声视频")
            
            # 使用ffmpeg创建视频
            result = self.create_video_from_frames(temp_frames, output_path, audio_path)
            
            # 清理临时音频文件（如果存在）
            if audio_path and audio_path.exists():
                try:
                    audio_path.unlink()
                except:
                    pass
            
            return result
            
        except Exception as e:
            print(f"创建幻灯片视频失败: {e}")
            return False
        finally:
            # 清理临时文件
            for temp_file in temp_frames:
                if temp_file.exists():
                    temp_file.unlink()
    
    def create_slides(self, title: str, content: str) -> list:
        """将内容分割为多个幻灯片"""
        slides = []
        
        # 标题幻灯片
        slides.append(f"{title}\n\n精彩内容即将开始...")
        
        # 分割内容为段落
        paragraphs = content.split('\n\n')
        current_slide = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # 如果段落太长，分割到新的幻灯片
            if len(current_slide) + len(para) > 200:  # 限制每页字符数
                if current_slide:
                    slides.append(current_slide)
                current_slide = para
            else:
                if current_slide:
                    current_slide += "\n\n" + para
                else:
                    current_slide = para
        
        if current_slide:
            slides.append(current_slide)
        
        # 结尾幻灯片
        slides.append("感谢观看！\n\n记得点赞和订阅哦！")
        
        return slides[:10]  # 最多10张幻灯片
    
    def create_tts_audio(self, text: str, lang: str = 'en') -> Optional[Path]:
        """使用TTS生成音频文件"""
        if not self.tts_enabled:
            return None
        
        try:
            # 清理文本，移除特殊字符
            clean_text = text.replace('\n', ' ').strip()
            if len(clean_text) < 10:  # 文本太短不生成音频
                return None
            
            # 生成音频文件
            audio_file = self.temp_dir / f"tts_{hash(clean_text)}.mp3"
            
            # 如果文件已存在，直接返回
            if audio_file.exists():
                return audio_file
            
            # 使用gTTS生成音频
            tts = gTTS(text=clean_text, lang=lang, slow=False)
            tts.save(str(audio_file))
            
            return audio_file
            
        except Exception as e:
            print(f"TTS音频生成失败: {e}")
            return None
    
    def create_audio_sequence(self, slides: list) -> Optional[Path]:
        """为所有幻灯片创建音频序列"""
        if not self.tts_enabled:
            return None
        
        try:
            audio_files = []
            
            # 为每个幻灯片生成音频
            for i, slide in enumerate(slides):
                audio_file = self.create_tts_audio(slide)
                if audio_file:
                    audio_files.append(audio_file)
                else:
                    # 如果某个幻灯片没有音频，创建静音填充
                    silent_file = self.temp_dir / f"silent_{i}.mp3"
                    self.create_silent_audio(silent_file, self.duration_per_slide)
                    audio_files.append(silent_file)
            
            # 合并所有音频文件
            combined_audio = self.temp_dir / "combined_audio.mp3"
            self.combine_audio_files(audio_files, combined_audio)
            
            return combined_audio
            
        except Exception as e:
            print(f"音频序列创建失败: {e}")
            return None
    
    def create_silent_audio(self, output_path: Path, duration: int):
        """创建静音音频文件"""
        try:
            cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', 'anullsrc=r=44100:cl=stereo',
                '-t', str(duration),
                '-q:a', '9',
                '-acodec', 'libmp3lame',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"创建静音音频失败: {result.stderr}")
                
        except Exception as e:
            print(f"静音音频创建失败: {e}")
    
    def combine_audio_files(self, audio_files: list, output_path: Path):
        """合并多个音频文件"""
        try:
            # 创建文件列表
            list_file = self.temp_dir / "audio_list.txt"
            with open(list_file, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{audio_file}'\n")
            
            # 使用ffmpeg合并音频
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(list_file),
                '-acodec', 'libmp3lame',
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 清理列表文件
            list_file.unlink()
            
            if result.returncode != 0:
                print(f"音频合并失败: {result.stderr}")
                
        except Exception as e:
            print(f"音频合并失败: {e}")
    
    def create_video_from_frames(self, frame_files: list, output_path: Path, audio_path: Optional[Path] = None) -> bool:
        """使用ffmpeg从帧文件创建视频，可选添加音频"""
        try:
            # 创建帧列表文件
            list_file = self.output_dir / "frame_list.txt"
            with open(list_file, 'w') as f:
                for frame_file in frame_files:
                    # 每张幻灯片重复多次以达到指定时长
                    for _ in range(self.duration_per_slide * self.fps):
                        f.write(f"file '{frame_file}'\n")
                        f.write(f"duration {1/self.fps}\n")
            
            # 构建ffmpeg命令
            if audio_path and audio_path.exists():
                # 有音频的情况
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(list_file),
                    '-i', str(audio_path),  # 音频输入
                    '-vf', 'fps=24',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',  # 音频编码
                    '-pix_fmt', 'yuv420p',
                    '-shortest',  # 以较短的流为准
                    str(output_path)
                ]
                print(f"创建带音频的视频: {output_path.name}")
            else:
                # 无音频的情况（保持原有逻辑）
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(list_file),
                    '-vf', 'fps=24',
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    str(output_path)
                ]
                print(f"创建无声视频: {output_path.name}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # 清理临时文件
            list_file.unlink()
            
            if result.returncode == 0:
                print(f"视频创建成功: {output_path}")
                return True
            else:
                print(f"视频创建失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"创建视频失败: {e}")
            return False
    
    def create_simple_video(self, title: str, content: str, output_filename: str, add_audio: bool = True) -> Optional[Path]:
        """创建简单视频的主函数，可选添加音频"""
        try:
            # 生成输出文件路径
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_')[:50]  # 限制长度
            
            output_file = self.output_dir / f"{safe_title}_article_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            print(f"正在创建视频: {output_file.name}")
            if add_audio and self.tts_enabled:
                print("🎵 将添加TTS音频解说")
            else:
                print("🔇 创建无声视频")
            
            # 创建幻灯片视频
            if self.create_slide_show_video(title, content, output_file, add_audio):
                return output_file
            else:
                return None
                
        except Exception as e:
            print(f"创建视频过程出错: {e}")
            return None

# 测试函数
def test_video_creation():
    """测试视频创建功能"""
    creator = SimpleVideoCreator("/Users/ax/wechat-publisher/social-auto-upload/videoFile")
    
    test_title = "AI Agents: 2026年最大的技术变革"
    test_content = """
    还记得当聊天机器人能写诗就让我们印象深刻的时候吗？那感觉像是石器时代。
    
    2026年，对话已经从"AI能说什么？"转变为"AI能做什么？"
    
    我们已经正式进入了AI智能体的时代——这些自主实体不仅仅是建议代码或起草邮件，
    而是实际上能在整个操作系统和云基础设施中执行多步骤工作流程。
    
    过去，AI是一个强大的工具，但需要持续监督。你会提示，它会回应，你会复制粘贴，
    你会验证，然后你会再次提示。这种"人在回路"的要求意味着虽然单个任务更快，
    但复杂项目仍然需要几天的人工协调。
    """
    
    result = creator.create_simple_video(test_title, test_content, "test")
    
    if result:
        print(f"✅ 测试视频创建成功: {result}")
        return True
    else:
        print("❌ 测试视频创建失败")
        return False

if __name__ == "__main__":
    test_video_creation()