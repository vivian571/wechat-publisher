"""
Medium 平台适配器
官方文档: https://github.com/Medium/medium-api-docs
"""

import httpx
from loguru import logger
from core.adapter_interface import IPlatformAdapter, PublishResult
from core.parser import ArticleMetadata


class MediumAdapter(IPlatformAdapter):
    """Medium 平台适配器"""
    
    BASE_URL = "https://api.medium.com/v1"
    
    def __init__(self, integration_token: str):
        """
        初始化 Medium 适配器
        
        Args:
            integration_token: Medium Integration Token
        """
        self.integration_token = integration_token
        self.headers = {
            "Authorization": f"Bearer {integration_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.user_id = None
        logger.debug("初始化 MediumAdapter")
    
    @property
    def platform_name(self) -> str:
        return "Medium"
    
    def validate_config(self) -> bool:
        """验证 Integration Token 是否有效"""
        try:
            logger.debug("验证 Medium Integration Token...")
            response = httpx.get(
                f"{self.BASE_URL}/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json().get('data', {})
                self.user_id = data.get('id')
                username = data.get('username')
                logger.success(f"✅ Medium Token 有效,用户: {username}")
                return True
            else:
                logger.error(f"❌ Medium Token 无效: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ 验证 Medium Token 失败: {e}")
            return False
    
    def _get_user_id(self) -> str:
        """获取用户 ID"""
        if self.user_id:
            return self.user_id
        
        try:
            response = httpx.get(
                f"{self.BASE_URL}/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                self.user_id = response.json().get('data', {}).get('id')
                return self.user_id
            else:
                raise Exception(f"获取用户 ID 失败: HTTP {response.status_code}")
        
        except Exception as e:
            logger.error(f"获取用户 ID 失败: {e}")
            raise
    
    def publish(self, metadata: ArticleMetadata, content: str) -> PublishResult:
        """
        发布文章到 Medium
        
        注意: Medium API 只能创建草稿或 Unlisted 文章
        
        Args:
            metadata: 文章元数据
            content: Markdown 内容
        
        Returns:
            PublishResult: 发布结果
        """
        logger.info(f"🚀 发布文章到 Medium: {metadata.title}")
        
        try:
            # 获取用户 ID
            user_id = self._get_user_id()
            
            # 确定发布状态
            publish_status = "draft"  # 默认为草稿
            if metadata.platform_config and 'medium' in metadata.platform_config:
                publish_status = metadata.platform_config['medium'].get('publish_status', 'draft')
            
            # 构造 Payload
            payload = {
                "title": metadata.title,
                "contentFormat": "markdown",
                "content": content,
                "tags": metadata.tags[:5],  # Medium 最多 5 个标签
                "publishStatus": publish_status,
                "license": "all-rights-reserved",
                "notifyFollowers": False
            }
            
            # 添加 canonical URL
            if metadata.canonical_url:
                payload["canonicalUrl"] = metadata.canonical_url
            
            logger.debug(f"发送请求到 Medium API (状态: {publish_status})...")
            response = httpx.post(
                f"{self.BASE_URL}/users/{user_id}/posts",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json().get('data', {})
                article_url = data.get('url')
                article_id = data.get('id')
                
                logger.success(f"✅ Medium 发布成功 ({publish_status}): {article_url}")
                
                if publish_status == "draft":
                    logger.info("💡 提示: Medium 文章已保存为草稿,请手动发布")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    article_url=article_url,
                    article_id=article_id,
                    raw_response=data
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Medium 发布失败: {error_msg}")
                
                return PublishResult(
                    success=False,
                    platform=self.platform_name,
                    error_message=error_msg
                )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Medium 发布失败: {error_msg}")
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error_message=error_msg
            )


if __name__ == "__main__":
    # 测试代码
    import sys
    import os
    from dotenv import load_dotenv
    
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    
    load_dotenv()
    
    token = os.getenv('MEDIUM_TOKEN')
    
    if not token:
        print("⚠️ 请在 .env 文件中配置 MEDIUM_TOKEN")
    else:
        adapter = MediumAdapter(token)
        
        # 测试验证
        if adapter.validate_config():
            print("✅ MediumAdapter 配置有效")
        else:
            print("❌ MediumAdapter 配置无效")
