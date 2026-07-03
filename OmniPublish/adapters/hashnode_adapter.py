"""
Hashnode 平台适配器
官方文档: https://apidocs.hashnode.com/
"""

import httpx
from loguru import logger
from core.adapter_interface import IPlatformAdapter, PublishResult
from core.parser import ArticleMetadata


class HashnodeAdapter(IPlatformAdapter):
    """Hashnode 平台适配器 (使用 GraphQL)"""
    
    API_URL = "https://gql.hashnode.com"
    
    def __init__(self, access_token: str, publication_id: str):
        """
        初始化 Hashnode 适配器
        
        Args:
            access_token: Hashnode Personal Access Token
            publication_id: Publication ID
        """
        import os
        self.access_token = access_token
        self.publication_id = publication_id
        self.headers = {
            "Authorization": access_token,
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
                
        logger.debug("初始化 HashnodeAdapter")
    
    @property
    def platform_name(self) -> str:
        return "Hashnode"
    
    def _sanitize_tag(self, tag: str) -> dict:
        """
        清理标签,确保符合 Hashnode 的格式要求
        
        Hashnode 标签 slug 规则:
        - 只允许小写字母、数字、连字符
        - 不能以连字符开头或结尾
        - 不能有连续连字符
        
        Args:
            tag: 原始标签
        
        Returns:
            dict: {"slug": "clean-slug", "name": "Original Tag"}
        """
        import re
        # 转小写并替换空格为连字符
        slug = tag.lower().replace(' ', '-')
        # 只保留字母、数字、连字符
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        # 移除连续连字符
        slug = re.sub(r'-+', '-', slug)
        # 移除开头和结尾的连字符
        slug = slug.strip('-')
        # 确保不为空
        if not slug:
            slug = "general"
        return {"slug": slug, "name": tag}
    
    def validate_config(self) -> bool:
        """验证 Access Token 是否有效"""
        query = """
        query {
          me {
            id
            username
            name
          }
        }
        """
        
        try:
            logger.debug("验证 Hashnode Access Token...")
            response = httpx.post(
                self.API_URL,
                headers=self.headers,
                json={"query": query},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'errors' in data:
                    logger.error(f"❌ Hashnode Token 无效: {data['errors']}")
                    return False
                
                user_data = data.get('data', {}).get('me', {})
                logger.success(f"✅ Hashnode Token 有效,用户: {user_data.get('username')}")
                return True
            else:
                logger.error(f"❌ Hashnode Token 无效: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            logger.error(f"❌ 验证 Hashnode Token 失败: {e}")
            return False
    
    def publish(self, metadata: ArticleMetadata, content: str) -> PublishResult:
        """
        发布文章到 Hashnode
        
        Args:
            metadata: 文章元数据
            content: Markdown 内容
        
        Returns:
            PublishResult: 发布结果
        """
        logger.info(f"🚀 发布文章到 Hashnode: {metadata.title}")
        
        # 构造 GraphQL Mutation
        mutation = """
        mutation PublishPost($input: PublishPostInput!) {
          publishPost(input: $input) {
            post {
              id
              slug
              title
              url
            }
          }
        }
        """
        
        # 构造变量
        variables = {
            "input": {
                "title": metadata.title,
                "contentMarkdown": content,
                "tags": [self._sanitize_tag(tag) for tag in metadata.tags[:5]],  # Hashnode 限制最多 15 个标签
                "publicationId": self.publication_id,
                "subtitle": metadata.description or ""
            }
        }
        
        # 添加封面图
        if metadata.cover_image and metadata.cover_image.startswith('http'):
            variables["input"]["coverImageOptions"] = {
                "coverImageURL": metadata.cover_image
            }
        
        # 添加 canonical URL
        if metadata.canonical_url:
            variables["input"]["originalArticleURL"] = metadata.canonical_url
        
        # 添加系列
        if metadata.series:
            variables["input"]["seriesId"] = metadata.series  # 需要预先创建系列
        
        try:
            logger.debug(f"发送请求到 Hashnode API...")
            response = httpx.post(
                self.API_URL,
                headers=self.headers,
                json={"query": mutation, "variables": variables},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 检查 GraphQL 错误
                if 'errors' in data:
                    error_msg = str(data['errors'])
                    logger.error(f"❌ Hashnode 发布失败: {error_msg}")
                    return PublishResult(
                        success=False,
                        platform=self.platform_name,
                        error_message=error_msg
                    )
                
                post_data = data.get('data', {}).get('publishPost', {}).get('post', {})
                article_url = post_data.get('url')
                article_id = post_data.get('id')
                
                logger.success(f"✅ Hashnode 发布成功: {article_url}")
                
                return PublishResult(
                    success=True,
                    platform=self.platform_name,
                    article_url=article_url,
                    article_id=article_id,
                    raw_response=post_data
                )
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ Hashnode 发布失败: {error_msg}")
                
                return PublishResult(
                    success=False,
                    platform=self.platform_name,
                    error_message=error_msg
                )
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Hashnode 发布失败: {error_msg}")
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
    
    token = os.getenv('HASHNODE_TOKEN')
    pub_id = os.getenv('HASHNODE_PUBLICATION_ID')
    
    if not token or not pub_id:
        print("⚠️ 请在 .env 文件中配置 HASHNODE_TOKEN 和 HASHNODE_PUBLICATION_ID")
    else:
        adapter = HashnodeAdapter(token, pub_id)
        
        # 测试验证
        if adapter.validate_config():
            print("✅ HashnodeAdapter 配置有效")
        else:
            print("❌ HashnodeAdapter 配置无效")
