"""
Twitter/X 平台适配器
使用 Tweepy 库与 Twitter API v2 交互
官方文档: https://developer.twitter.com/en/docs/twitter-api
"""

import tweepy
from loguru import logger
from core.adapter_interface import IPlatformAdapter, PublishResult
from core.parser import ArticleMetadata
import os


class TwitterAdapter(IPlatformAdapter):
    """Twitter/X 平台适配器"""
    
    MAX_TWEET_LENGTH = 280
    MAX_THREAD_TWEETS = 25  # Twitter 线程最大推文数
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        """
        初始化 Twitter 适配器
        
        Args:
            api_key: Twitter API Key (Consumer Key)
            api_secret: Twitter API Secret (Consumer Secret)
            access_token: Twitter Access Token
            access_token_secret: Twitter Access Token Secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        
        # 配置代理
        proxy = None
        use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
        if use_proxy:
            http_proxy = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
            if http_proxy:
                proxy = http_proxy
                logger.info(f"Twitter adapter will use proxy: {proxy}")
        
        # 初始化 Tweepy 客户端 (API v2)
        try:
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            logger.info("Twitter API v2 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise
    
    @property
    def platform_name(self) -> str:
        return "Twitter"
    
    def _split_into_thread(self, content: str, title: str) -> list[str]:
        """
        将长文本分割成 Twitter 线程
        
        Args:
            content: 文章内容
            title: 文章标题
        
        Returns:
            推文列表
        """
        tweets = []
        
        # 第一条推文：标题 + 摘要
        first_tweet = f"📝 {title}\n\n"
        
        # 提取文章前几句作为摘要
        lines = content.split('\n')
        summary_lines = []
        char_count = len(first_tweet)
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if char_count + len(line) + 1 < self.MAX_TWEET_LENGTH - 20:  # 留20字符给 "🧵👇"
                summary_lines.append(line)
                char_count += len(line) + 1
            else:
                break
        
        first_tweet += '\n'.join(summary_lines)
        first_tweet += "\n\n🧵👇"
        tweets.append(first_tweet)
        
        # 将剩余内容分割成多条推文
        remaining_content = content
        tweet_number = 2
        
        while remaining_content and tweet_number <= self.MAX_THREAD_TWEETS:
            # 每条推文格式: "{tweet_number}/{total} 内容"
            prefix = f"{tweet_number}/ "
            max_content_length = self.MAX_TWEET_LENGTH - len(prefix) - 10  # 留10字符余量
            
            # 找到合适的分割点（优先在句号、换行处分割）
            chunk = remaining_content[:max_content_length]
            
            # 寻找最后一个句号或换行
            split_points = [chunk.rfind('。'), chunk.rfind('\n'), chunk.rfind('. ')]
            split_index = max(split_points)
            
            if split_index > max_content_length * 0.5:  # 如果分割点在后半部分
                chunk = remaining_content[:split_index + 1]
            else:
                chunk = remaining_content[:max_content_length]
            
            tweet = prefix + chunk.strip()
            tweets.append(tweet)
            
            remaining_content = remaining_content[len(chunk):].strip()
            tweet_number += 1
        
        # 更新第一条推文的总数
        if len(tweets) > 1:
            tweets[0] = tweets[0].replace("🧵👇", f"🧵 1/{len(tweets)} 👇")
            # 更新其他推文的总数
            for i in range(1, len(tweets)):
                tweets[i] = tweets[i].replace(f"{i+1}/ ", f"{i+1}/{len(tweets)} ")
        
        return tweets
    
    def validate_config(self) -> bool:
        """验证 Twitter API 凭证是否有效"""
        try:
            # 尝试获取当前用户信息
            me = self.client.get_me()
            if me.data:
                logger.info(f"✅ Twitter API 验证成功，当前用户: @{me.data.username}")
                return True
            else:
                logger.error("❌ Twitter API 验证失败: 无法获取用户信息")
                return False
        except tweepy.TweepyException as e:
            logger.error(f"❌ Twitter API 验证失败: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Twitter API 验证时发生未知错误: {e}")
            return False
    
    def publish(self, metadata: ArticleMetadata, content: str) -> PublishResult:
        """
        发布文章到 Twitter (作为线程)
        
        Args:
            metadata: 文章元数据
            content: Markdown 内容
        
        Returns:
            PublishResult: 发布结果
        """
        try:
            logger.info(f"开始发布到 Twitter: {metadata.title}")
            
            # 将文章分割成线程
            tweets = self._split_into_thread(content, metadata.title)
            logger.info(f"文章已分割为 {len(tweets)} 条推文")
            
            # 发布线程
            tweet_ids = []
            previous_tweet_id = None
            
            for i, tweet_text in enumerate(tweets):
                try:
                    if previous_tweet_id:
                        # 回复前一条推文，形成线程
                        response = self.client.create_tweet(
                            text=tweet_text,
                            in_reply_to_tweet_id=previous_tweet_id
                        )
                    else:
                        # 发布第一条推文
                        response = self.client.create_tweet(text=tweet_text)
                    
                    tweet_id = response.data['id']
                    tweet_ids.append(tweet_id)
                    previous_tweet_id = tweet_id
                    
                    logger.info(f"✅ 推文 {i+1}/{len(tweets)} 发布成功 (ID: {tweet_id})")
                    
                except tweepy.TweepyException as e:
                    logger.error(f"❌ 推文 {i+1} 发布失败: {e}")
                    raise
            
            # 构建线程 URL (第一条推文的 URL)
            me = self.client.get_me()
            username = me.data.username if me.data else "unknown"
            thread_url = f"https://twitter.com/{username}/status/{tweet_ids[0]}"
            
            logger.info(f"🎉 Twitter 线程发布成功！共 {len(tweet_ids)} 条推文")
            
            return PublishResult(
                success=True,
                platform="Twitter",
                article_id=str(tweet_ids[0]),  # 使用第一条推文 ID
                url=thread_url,
                message=f"成功发布 {len(tweet_ids)} 条推文线程"
            )
            
        except tweepy.TweepyException as e:
            error_msg = f"Twitter API 错误: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return PublishResult(
                success=False,
                platform="Twitter",
                message=error_msg
            )
        except Exception as e:
            error_msg = f"发布失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return PublishResult(
                success=False,
                platform="Twitter",
                message=error_msg
            )
    
    def update(self, article_id: str, metadata: ArticleMetadata, content: str) -> PublishResult:
        """
        Twitter 不支持编辑已发布的推文
        
        注意: Twitter API v2 目前不支持编辑推文（除非是 Twitter Blue 用户）
        此方法将返回不支持的错误
        """
        logger.warning("⚠️ Twitter 不支持编辑已发布的推文")
        return PublishResult(
            success=False,
            platform="Twitter",
            message="Twitter 平台不支持编辑已发布的推文。如需更新内容，请删除原推文后重新发布。"
        )


if __name__ == "__main__":
    # 测试代码
    import sys
    from dotenv import load_dotenv
    
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")
    
    load_dotenv()
    
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        print("❌ 请在 .env 文件中配置 Twitter API 凭证")
        sys.exit(1)
    else:
        adapter = TwitterAdapter(api_key, api_secret, access_token, access_token_secret)
        
        # 测试验证
        if adapter.validate_config():
            print("✅ TwitterAdapter 配置有效")
        else:
            print("❌ TwitterAdapter 配置无效")
