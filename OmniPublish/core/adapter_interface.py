"""
平台适配器接口
定义统一的平台适配器标准
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class PublishResult:
    """发布结果"""
    success: bool
    platform: str
    article_url: Optional[str] = None
    article_id: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: dict = None


class IPlatformAdapter(ABC):
    """平台适配器接口"""
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """平台名称"""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """
        验证配置 (API Key, Token 等)
        
        Returns:
            bool: 配置是否有效
        """
        pass
    
    @abstractmethod
    def publish(self, metadata: 'ArticleMetadata', content: str) -> PublishResult:
        """
        发布文章
        
        Args:
            metadata: 文章元数据
            content: Markdown 内容 (图片链接已替换为公共 URL)
        
        Returns:
            PublishResult: 发布结果
        """
        pass
    
    def update(self, article_id: str, metadata: 'ArticleMetadata', content: str) -> PublishResult:
        """
        更新已发布的文章 (可选实现)
        
        Args:
            article_id: 文章 ID
            metadata: 文章元数据
            content: Markdown 内容
        
        Returns:
            PublishResult: 更新结果
        """
        return PublishResult(
            success=False,
            platform=self.platform_name,
            error_message="该平台不支持更新文章"
        )
    
    def delete(self, article_id: str) -> bool:
        """
        删除文章 (可选实现)
        
        Args:
            article_id: 文章 ID
        
        Returns:
            bool: 是否删除成功
        """
        return False
