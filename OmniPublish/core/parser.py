"""
文章解析器模块
负责解析 Markdown 文件的 Frontmatter 和内容
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from pathlib import Path
import frontmatter
from loguru import logger


@dataclass
class ArticleMetadata:
    """文章元数据标准结构"""
    title: str
    tags: List[str]
    cover_image: Optional[str] = None
    canonical_url: Optional[str] = None
    published: bool = True
    series: Optional[str] = None
    description: Optional[str] = None
    platform_config: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        """验证必填字段"""
        if not self.title:
            raise ValueError("文章标题 (title) 是必填字段")
        if not self.tags or len(self.tags) == 0:
            raise ValueError("文章标签 (tags) 是必填字段,至少需要一个标签")


class ArticleParser:
    """Markdown 文章解析器"""
    
    def __init__(self):
        logger.debug("初始化 ArticleParser")
    
    def parse(self, file_path: str) -> tuple[ArticleMetadata, str]:
        """
        解析 Markdown 文件
        
        Args:
            file_path: Markdown 文件路径
        
        Returns:
            (metadata, content): 元数据对象和 Markdown 内容
        
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: Frontmatter 格式错误或缺少必填字段
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        logger.info(f"📝 解析文章: {file_path.name}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            # 提取并处理标签
            raw_tags = post.get('tags', [])
            # 如果标签是字符串（逗号分隔），则拆分为列表
            if isinstance(raw_tags, str):
                tags = [tag.strip() for tag in raw_tags.split(',') if tag.strip()]
            else:
                tags = raw_tags if raw_tags else []
            
            # 提取元数据
            metadata = ArticleMetadata(
                title=post.get('title', ''),
                tags=tags,
                cover_image=post.get('cover_image'),
                canonical_url=post.get('canonical_url'),
                published=post.get('published', True),
                series=post.get('series'),
                description=post.get('description'),
                platform_config=post.get('platform_config', {})
            )
            
            logger.debug(f"解析元数据: title={metadata.title}, tags={metadata.tags}")
            
            return metadata, post.content
        
        except Exception as e:
            logger.error(f"解析文章失败: {e}")
            raise ValueError(f"解析 Frontmatter 失败: {e}")
    
    def validate_metadata(self, metadata: ArticleMetadata) -> bool:
        """
        验证元数据是否完整
        
        Args:
            metadata: 文章元数据
        
        Returns:
            bool: 是否通过验证
        """
        try:
            # 检查标题
            if not metadata.title or len(metadata.title.strip()) == 0:
                logger.warning("文章标题为空")
                return False
            
            # 检查标签
            if not metadata.tags or len(metadata.tags) == 0:
                logger.warning("文章标签为空")
                return False
            
            # 检查标签数量 (建议 2-5 个)
            if len(metadata.tags) > 5:
                logger.warning(f"标签数量过多 ({len(metadata.tags)}),建议不超过 5 个")
            
            logger.debug("✅ 元数据验证通过")
            return True
        
        except Exception as e:
            logger.error(f"验证元数据失败: {e}")
            return False


if __name__ == "__main__":
    # 测试代码
    from loguru import logger
    import sys
    
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    
    # 创建测试文章
    test_content = """---
title: "测试文章"
tags: ["python", "automation"]
cover_image: "./images/cover.png"
canonical_url: "https://myblog.com/test"
published: true
description: "这是一篇测试文章"
---

# 测试内容

这是文章正文。
"""
    
    test_file = Path("test_article.md")
    test_file.write_text(test_content, encoding='utf-8')
    
    # 测试解析
    parser = ArticleParser()
    metadata, content = parser.parse(str(test_file))
    
    print(f"标题: {metadata.title}")
    print(f"标签: {metadata.tags}")
    print(f"内容: {content[:50]}...")
    
    # 清理测试文件
    test_file.unlink()
    
    print("✅ ArticleParser 测试通过")
