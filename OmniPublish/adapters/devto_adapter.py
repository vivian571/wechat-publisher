"""
Dev.to 平台适配器
官方文档: https://developers.forem.com/api/v1
"""

import httpx
from loguru import logger
from core.adapter_interface import IPlatformAdapter, PublishResult
from core.parser import ArticleMetadata


class DevToAdapter(IPlatformAdapter):
    """Dev.to 平台适配器"""
    
    BASE_URL = "https://dev.to/api"
    
    def __init__(self, api_key: str):
        """
        初始化 Dev.to 适配器
        
        Args:
            api_key: Dev.to API Key
        """
        import os
        
        self.api_key = api_key
        self.headers = {
            "api-key": api_key,
            "Content-Type": "application/json"
        }
        
        # 配置代理 (httpx 格式)
        self.proxies = None
        use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
        if use_proxy:
            http_proxy = os.getenv('HTTP_PROXY')
            https_proxy = os.getenv('HTTPS_PROXY')
            if http_proxy or https_proxy:
                # httpx 使用不带斜杠的协议名作为 key
                self.proxies = {}
                if http_proxy:
                    self.proxies["http://"] = http_proxy
                if https_proxy:
                    self.proxies["https://"] = https_proxy
                logger.debug(f"✅ 已启用代理: {http_proxy or https_proxy}")
        
        logger.debug("初始化 DevToAdapter")
    
    @property
    def platform_name(self) -> str:
        return "Dev.to"
    
    def _sanitize_tag(self, tag: str) -> str:
        """
        清理标签,移除 Dev.to 不支持的字符
        
        Dev.to 标签规则:
        - 只允许字母、数字、下划线
        - 不允许连字符、空格等特殊字符
        
        Args:
            tag: 原始标签
        
        Returns:
            清理后的标签
        """
        import re
        # 将连字符和空格替换为空字符串
        cleaned = re.sub(r'[-\s]', '', tag)
        # 只保留字母、数字、下划线
        cleaned = re.sub(r'[^a-zA-Z0-9_]', '', cleaned)
        return cleaned.lower()
    
    def validate_config(self) -> bool:
        """验证 API Key 是否有效"""
        try:
            logger.debug("验证 Dev.to API Key...")
            response = httpx.get(
                f"{self.BASE_URL}/users/me",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                logger.success(f"✅ Dev.to API Key 有效,用户: {user_data.get('username')}")
                return True
            else:
                logger.error(f"❌ Dev.to API Key 无效: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ 验证 Dev.to API Key 失败: {e}")
            return False
    
    def publish(self, metadata: ArticleMetadata, content: str) -> PublishResult:
        """
        发布文章到 Dev.to
        
        Args:
            metadata: 文章元数据
            content: Markdown 内容 (图片链接已替换)
        
        Returns:
            PublishResult: 发布结果
        """
        logger.info(f"🚀 发布文章到 Dev.to: {metadata.title}")
        
        # 清理标签 (移除连字符等不支持的字符)
        original_tags = metadata.tags[:4]
        sanitized_tags = [self._sanitize_tag(tag) for tag in original_tags]
        
        # 记录标签转换
        for orig, clean in zip(original_tags, sanitized_tags):
            if orig != clean:
                logger.debug(f"标签清理: '{orig}' -> '{clean}'")
        
        # 构造 Payload
        payload = {
            "article": {
                "title": metadata.title,
                "body_markdown": content,
                "published": metadata.published,
                "tags": sanitized_tags,  # 使用清理后的标签
                "description": metadata.description
            }
        }
        
        # 添加可选字段
        if metadata.series:
            payload["article"]["series"] = metadata.series
        
        if metadata.canonical_url:
            payload["article"]["canonical_url"] = metadata.canonical_url
        
        # 平台特定配置
        if metadata.platform_config and 'devto' in metadata.platform_config:
            devto_config = metadata.platform_config['devto']
            if 'organization_id' in devto_config:
                payload["article"]["organization_id"] = devto_config['organization_id']
        
        try:
            logger.debug(f"发送请求到 Dev.to API...")
            response = httpx.post(
                f"{self.BASE_URL}/articles",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                article_url = data.get('url')
                article_id = str(data.get('id'))
                
                logger.success(f"✅ Dev.to 发布成功: {article_url}")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    article_url=article_url,
                    article_id=article_id,
                    raw_response=data
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Dev.to 发布失败: {error_msg}")
                
                return PublishResult(
                    success=False,
                    platform=self.platform_name,
                    error_message=error_msg
                )
        
        except httpx.TimeoutException:
            error_msg = "请求超时"
            logger.error(f"❌ Dev.to 发布失败: {error_msg}")
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error_message=error_msg
            )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Dev.to 发布失败: {error_msg}")
            return PublishResult(
                success=False,
                platform=self.platform_name,
                error_message=error_msg
            )
    
    def update(self, article_id: str, metadata: ArticleMetadata, content: str) -> PublishResult:
        """
        更新已发布的文章
        
        Args:
            article_id: 文章 ID
            metadata: 文章元数据
            content: Markdown 内容
        
        Returns:
            PublishResult: 更新结果
        """
        logger.info(f"🔄 更新 Dev.to 文章: {article_id}")
        
        payload = {
            "article": {
                "title": metadata.title,
                "body_markdown": content,
                "tags": metadata.tags[:4]
            }
        }
        
        try:
            response = httpx.put(
                f"{self.BASE_URL}/articles/{article_id}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.success(f"✅ Dev.to 更新成功")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    article_url=data.get('url'),
                    article_id=article_id,
                    raw_response=data
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Dev.to 更新失败: {error_msg}")
                
                return PublishResult(
                    success=False,
                    platform=self.platform_name,
                    error_message=error_msg
                )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Dev.to 更新失败: {error_msg}")
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
    
    api_key = os.getenv('DEVTO_API_KEY')
    if not api_key:
        print("⚠️ 请在 .env 文件中配置 DEVTO_API_KEY")
    else:
        adapter = DevToAdapter(api_key)
        
        # 测试验证
        if adapter.validate_config():
            print("✅ DevToAdapter 配置有效")
        else:
            print("❌ DevToAdapter 配置无效")
