# -*- coding: utf-8 -*-
"""
矩阵桥接模块
用于连接 My_Wechat_Matrix 项目和 social-auto-upload 项目
实现"文章 -> 视频"的自动化转化和推送
"""

import os
import time
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, List
import threading

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("警告：未安装 watchdog 库，矩阵联动功能的实时监听不可用")
    Observer = None
    FileSystemEventHandler = object


class MatrixBridge:
    """矩阵桥接器"""

    def __init__(
        self,
        wechat_matrix_dir: str,
        upload_queue_dir: str,
        auto_convert: bool = True
    ):
        """
        初始化矩阵桥接器

        Args:
            wechat_matrix_dir: My_Wechat_Matrix 项目目录
            upload_queue_dir: 视频上传队列目录 (videos 目录)
            auto_convert: 是否自动转换
        """
        self.wechat_matrix_dir = Path(wechat_matrix_dir)
        self.upload_queue_dir = Path(upload_queue_dir)
        self.auto_convert = auto_convert
        
        # 确保目录存在
        if not self.upload_queue_dir.exists():
            self.upload_queue_dir.mkdir(parents=True, exist_ok=True)
            
        self.observer = None
        self.logger = self._init_logger()

    def _init_logger(self):
        """初始化简单的日志记录器"""
        import logging
        logger = logging.getLogger("MatrixBridge")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def start_monitoring(self):
        """开始监听 My_Wechat_Matrix 的文章发布"""
        if not self.wechat_matrix_dir.exists():
            self.logger.error(f"My_Wechat_Matrix 目录不存在: {self.wechat_matrix_dir}")
            return

        if Observer is None:
            self.logger.warning("无法启动实时监听，因为缺少 watchdog 库")
            return

        # 监听 articles 目录（假设文章生成在这里）
        articles_dir = self.wechat_matrix_dir / "articles"
        if not articles_dir.exists():
            # 尝试监听根目录下的输出文件? 
            # 根据用户环境，可能是 f:\公众号写作\My_Wechat_Matrix\output 或类似的
            # 暂时监听根目录
            articles_dir = self.wechat_matrix_dir

        self.logger.info(f"开始监听目录: {articles_dir}")
        
        event_handler = ArticleHandler(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(articles_dir), recursive=True)
        self.observer.start()

    def stop_monitoring(self):
        """停止监听"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.logger.info("停止监听")

    def process_article(self, article_path: str):
        """
        处理新文章
        
        Args:
            article_path: 文章文件路径
        """
        article_path = Path(article_path)
        
        # 过滤非文章文件（假设是 .md 或 .txt）
        if article_path.suffix not in ['.md', '.txt']:
            return
            
        self.logger.info(f"检测到新文章: {article_path.name}")
        
        if not self.auto_convert:
            self.logger.info("自动转换已关闭，跳过")
            return

        try:
            # 1. 解析文章
            content = self._read_article(article_path)
            title = self._extract_title(content) or article_path.stem
            
            # 2. 生成视频脚本（这里是个占位符，未来可以调用 AI）
            script = self._article_to_script(content)
            
            # 3. 这里的逻辑取决于如何生成视频
            # 如果是简单的"图文转视频"，可能需要图片
            # 目前阶段，我们主要做一个"模拟推送"，即如果用户手动生成了视频，
            # 或者是有一个机制生成了视频，我们把它移动到 upload 队列
            
            # TODO: 实现真正的文章转视频逻辑
            # 目前仅记录日志，或者如果同目录下有同名视频，则认为那是生成的视频
            
            potential_video = article_path.with_suffix('.mp4')
            if potential_video.exists():
                self.push_video(str(potential_video), title)
            else:
                self.logger.info(f"未找到对应的视频文件: {potential_video.name}，跳过推送")
                
        except Exception as e:
            self.logger.error(f"处理文章失败: {e}")

    def _read_article(self, path: Path) -> str:
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                return path.read_text(encoding='gbk')
            except:
                return ""

    def _extract_title(self, content: str) -> str:
        # 简单提取第一行作为标题
        lines = content.strip().split('\n')
        if lines:
            return lines[0].replace('#', '').strip()
        return ""

    def _article_to_script(self, content: str) -> str:
        # 简单的摘要提取
        return content[:500] + "..."

    def push_video(self, video_path: str, title: str, tags: List[str] = None):
        """
        将视频推送到上传队列
        
        Args:
            video_path: 视频源路径
            title: 视频标题
            tags: 标签列表
        """
        video_src = Path(video_path)
        if not video_src.exists():
            self.logger.error(f"视频文件不存在: {video_path}")
            return

        # 1. 复制视频文件
        target_video = self.upload_queue_dir / video_src.name
        shutil.copy2(video_src, target_video)
        
        # 2. 创建或更新元数据文件 (.txt)
        txt_path = target_video.with_suffix('.txt')
        
        if tags is None:
            tags = ["自动发布", "AI生成"]
            
        content = f"{title}\n{' '.join(tags)}"
        txt_path.write_text(content, encoding='utf-8')
        
        self.logger.info(f"视频已推送到上传队列: {target_video.name}")


class ArticleHandler(FileSystemEventHandler):
    """文件系统事件处理器"""
    
    def __init__(self, bridge: MatrixBridge):
        self.bridge = bridge
        
    def on_created(self, event):
        if not event.is_directory:
            self.bridge.process_article(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            # 可以在这里处理修改事件，但这可能导致重复处理
            # 暂时忽略
            pass


# 便捷函数
def create_bridge_from_config(config_dict: dict) -> Optional[MatrixBridge]:
    """
    从配置字典创建矩阵桥接器
    """
    if not config_dict.get("MATRIX_BRIDGE_ENABLED", False):
        return None
        
    wechat_matrix_dir = config_dict.get("WECHAT_MATRIX_DIR", "")
    upload_queue_dir = config_dict.get("UPLOAD_QUEUE_DIR", "videos")
    
    if not wechat_matrix_dir:
        print("警告：未配置 WECHAT_MATRIX_DIR，矩阵联动无法启动")
        return None
        
    return MatrixBridge(
        wechat_matrix_dir=wechat_matrix_dir,
        upload_queue_dir=upload_queue_dir
    )

if __name__ == "__main__":
    print("矩阵桥接模块加载成功")
    # 测试代码
    # bridge = MatrixBridge("F:/test_source", "F:/test_queue")
    # bridge.start_monitoring()
    # input("按回车停止...")
    # bridge.stop_monitoring()
