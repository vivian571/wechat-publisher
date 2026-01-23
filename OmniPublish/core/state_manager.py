"""
状态管理器模块
负责记录文章在各平台的发布状态
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from loguru import logger


class StateManager:
    """发布状态管理器"""
    
    def __init__(self, state_file: str = ".omnipublish/state.json"):
        """
        初始化状态管理器
        
        Args:
            state_file: 状态文件路径
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()
        logger.debug(f"初始化 StateManager: {self.state_file}")
    
    def _load_state(self) -> dict:
        """加载状态文件"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                logger.debug(f"加载状态文件: {len(state)} 篇文章")
                return state
            except Exception as e:
                logger.warning(f"加载状态文件失败,使用空状态: {e}")
                return {}
        return {}
    
    def save_state(self):
        """保存状态到文件"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.debug("状态文件已保存")
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")
    
    def record_publish(self, article_path: str, platform: str, result: 'PublishResult'):
        """
        记录发布结果
        
        Args:
            article_path: 文章路径
            platform: 平台名称
            result: 发布结果
        """
        if article_path not in self.state:
            self.state[article_path] = {}
        
        self.state[article_path][platform] = {
            'success': result.success,
            'url': result.article_url,
            'article_id': result.article_id,
            'published_at': datetime.now().isoformat(),
            'error': result.error_message
        }
        
        self.save_state()
        
        if result.success:
            logger.success(f"✅ 记录发布成功: {platform}")
        else:
            logger.warning(f"⚠️ 记录发布失败: {platform} - {result.error_message}")
    
    def get_article_status(self, article_path: str) -> Dict[str, dict]:
        """
        获取文章在所有平台的发布状态
        
        Args:
            article_path: 文章路径
        
        Returns:
            Dict[str, dict]: 各平台的发布状态
        """
        return self.state.get(article_path, {})
    
    def is_published(self, article_path: str, platform: str) -> bool:
        """
        检查文章是否已在指定平台发布
        
        Args:
            article_path: 文章路径
            platform: 平台名称
        
        Returns:
            bool: 是否已发布
        """
        article_state = self.state.get(article_path, {})
        platform_state = article_state.get(platform, {})
        return platform_state.get('success', False)
    
    def get_published_url(self, article_path: str, platform: str) -> Optional[str]:
        """
        获取文章在指定平台的 URL
        
        Args:
            article_path: 文章路径
            platform: 平台名称
        
        Returns:
            Optional[str]: 文章 URL,如果未发布则返回 None
        """
        article_state = self.state.get(article_path, {})
        platform_state = article_state.get(platform, {})
        return platform_state.get('url')
    
    def clear_article_state(self, article_path: str):
        """
        清除文章的发布状态
        
        Args:
            article_path: 文章路径
        """
        if article_path in self.state:
            del self.state[article_path]
            self.save_state()
            logger.info(f"已清除文章状态: {article_path}")
    
    def get_all_articles(self) -> list:
        """
        获取所有已发布的文章路径
        
        Returns:
            list: 文章路径列表
        """
        return list(self.state.keys())


if __name__ == "__main__":
    # 测试代码
    import sys
    from loguru import logger
    from core.adapter_interface import PublishResult
    
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    
    # 创建临时状态文件
    test_state_file = ".omnipublish/test_state.json"
    manager = StateManager(test_state_file)
    
    # 测试记录发布
    result = PublishResult(
        success=True,
        platform="Dev.to",
        article_url="https://dev.to/test/article",
        article_id="123456"
    )
    
    manager.record_publish("articles/test.md", "Dev.to", result)
    
    # 测试查询状态
    print(f"是否已发布: {manager.is_published('articles/test.md', 'Dev.to')}")
    print(f"文章 URL: {manager.get_published_url('articles/test.md', 'Dev.to')}")
    
    # 清理测试文件
    Path(test_state_file).unlink(missing_ok=True)
    
    print("✅ StateManager 测试通过")
