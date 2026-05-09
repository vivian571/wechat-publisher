from abc import ABC, abstractmethod
import logging
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from markdown import Markdown
import frontmatter
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from utils.config import Config
from utils.logger import get_logger


class AccountLogFilter(logging.Filter):
    """自定义日志过滤器，为日志记录添加账户名称。"""
    def __init__(self, account_name: str):
        super().__init__()
        self.account_name = account_name

    def filter(self, record):
        record.account_name = self.account_name
        return True


class BasePublisher(ABC):
    platform_name: str = ''
    """
    所有发布平台的基类。
    定义了发布器的通用接口和常用功能。
    """
    
    def __init__(self, account_name: str, platform_config: dict, common_config: Config):
        """
        初始化发布器。

        Args:
            account_name: 账户名称, e.g., 'my_wechat_account'.
            platform_config: 此账户在 config.yaml 中的特定配置。
            common_config: 共享的全局配置对象。
        """
        self.account_name = account_name
        self.platform_config = platform_config
        self.common_config = common_config
        # 使用 self.platform_name() 获取子类定义的平台名，使日志更清晰
        logger_instance = logging.getLogger(f"publisher.{self.platform_name}.{self.account_name}")

        # 为日志添加账户名称过滤
        for handler in logger_instance.handlers:
            if not any(isinstance(f, AccountLogFilter) for f in handler.filters):
                handler.addFilter(AccountLogFilter(account_name))

        # 为日志记录添加 account_name 上下文
        self.logger = logging.LoggerAdapter(logger_instance, {'account_name': self.account_name})

    
    @abstractmethod
    def publish(self, file_path: str, **kwargs) -> bool:
        """
        发布单个文件。
        
        Args:
            file_path: 要发布的Markdown文件的绝对路径。
            **kwargs: 其他可选参数。
            
        Returns:
            bool: 如果发布成功则返回 True, 否则返回 False。
        """
        raise NotImplementedError
    
    def process_markdown(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        处理Markdown文件，提取内容和元数据。
        
        Args:
            file_path: Markdown文件的路径。
            
        Returns:
            tuple: 包含(html内容, 元数据字典)的元组。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # 使用markdown库转换内容为HTML
            md = Markdown(extensions=['meta', 'extra', 'sane_lists', 'tables', 'fenced_code'])
            html_content = md.convert(post.content)
            
            # 提取元数据
            metadata = {}
            for key, value in post.metadata.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    metadata[key] = value
                elif isinstance(value, (list, tuple)) and all(isinstance(x, (str, int, float, bool)) for x in value):
                    metadata[key] = value[0] if len(value) == 1 else value
            
            # 确保有标题
            if 'title' not in metadata:
                metadata['title'] = Path(file_path).stem
            
            return html_content, metadata
            
        except Exception as e:
            self.log_error(f"处理Markdown文件时出错: {e}", exc_info=True)
            raise
    
    def log_debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)
        
    def log_info(self, message: str):
        """记录一般信息"""
        self.logger.info(f"ℹ️ {message}")
        
    def log_warning(self, message: str):
        """记录警告信息"""
        self.logger.warning(f"⚠️ {message}")
        
    def log_error(self, message: str, exc_info: bool = False):
        """
        记录错误信息
        
        Args:
            message: 错误信息
            exc_info: 是否记录异常堆栈
        """
        self.logger.error(f"❌ {message}", exc_info=exc_info)
        
    def log_success(self, message: str):
        """记录成功信息"""
        self.logger.info(f"✅ {message}")
