"""
OmniPublish 主程序入口
"""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from utils.logger import setup_logger
from utils.config_loader import ConfigLoader
from utils.r2_client import CloudflareR2Client
from core.parser import ArticleParser
from core.asset_manager import AssetManager
from core.state_manager import StateManager
from adapters.devto_adapter import DevToAdapter
from adapters.hashnode_adapter import HashnodeAdapter
from adapters.medium_adapter import MediumAdapter
from adapters.twitter_adapter import TwitterAdapter


def init_adapters(config: ConfigLoader, skip_validation: bool = False) -> list:
    """
    初始化平台适配器
    
    Args:
        config: 配置加载器
        skip_validation: 是否跳过 API 验证
    
    Returns:
        list: 启用的适配器列表
    """
    adapters = []
    
    # Dev.to
    if config.is_platform_enabled('devto'):
        api_key = config.get('platforms.devto.api_key')
        if api_key:
            adapter = DevToAdapter(api_key)
            if skip_validation or adapter.validate_config():
                adapters.append(adapter)
                logger.info("✅ Dev.to 适配器已启用")
            else:
                logger.warning("⚠️ Dev.to 配置无效,已跳过")
    
    # Hashnode
    if config.is_platform_enabled('hashnode'):
        token = config.get('platforms.hashnode.access_token')
        pub_id = config.get('platforms.hashnode.publication_id')
        if token and pub_id:
            adapter = HashnodeAdapter(token, pub_id)
            if skip_validation or adapter.validate_config():
                adapters.append(adapter)
                logger.info("✅ Hashnode 适配器已启用")
            else:
                logger.warning("⚠️ Hashnode 配置无效,已跳过")
    
    # Medium
    if config.is_platform_enabled('medium'):
        token = config.get('platforms.medium.integration_token')
        if token:
            adapter = MediumAdapter(token)
            if skip_validation or adapter.validate_config():
                adapters.append(adapter)
                logger.info("✅ Medium 适配器已启用")
            else:
                logger.warning("⚠️ Medium 配置无效,已跳过")
    
    # Twitter/X
    if config.is_platform_enabled('twitter'):
        api_key = config.get('platforms.twitter.api_key')
        api_secret = config.get('platforms.twitter.api_secret')
        access_token = config.get('platforms.twitter.access_token')
        access_token_secret = config.get('platforms.twitter.access_token_secret')
        if all([api_key, api_secret, access_token, access_token_secret]):
            adapter = TwitterAdapter(api_key, api_secret, access_token, access_token_secret)
            if skip_validation or adapter.validate_config():
                adapters.append(adapter)
                logger.info("✅ Twitter 适配器已启用")
            else:
                logger.warning("⚠️ Twitter 配置无效,已跳过")
        else:
            logger.warning("⚠️ Twitter API 凭证不完整,已跳过")
    
    return adapters


def publish_article(article_path: str, config: ConfigLoader, adapters: list, state_manager: StateManager, asset_manager: AssetManager = None):
    """
    发布单篇文章
    
    Args:
        article_path: 文章路径
        config: 配置加载器
        adapters: 适配器列表
        state_manager: 状态管理器
        asset_manager: 资源管理器
    """
    article_path = Path(article_path)
    
    if not article_path.exists():
        logger.error(f"❌ 文章文件不存在: {article_path}")
        return
    
    logger.info(f"\n{'='*60}")
    logger.info(f"📝 处理文章: {article_path.name}")
    logger.info(f"{'='*60}\n")
    
    try:
        # 1. 解析文章
        parser = ArticleParser()
        metadata, content = parser.parse(str(article_path))
        
        if not parser.validate_metadata(metadata):
            logger.error("❌ 文章元数据验证失败,跳过发布")
            return
        
        # 2. 处理图片 (如果配置了图床)
        if asset_manager:
            logger.info("🔄 处理图片...")
            content = asset_manager.replace_images(content, article_path.parent)
        else:
            logger.warning("⚠️ 未配置图床,跳过图片处理 (本地图片链接可能无法在平台显示)")
        
        # 3. 添加 canonical URL (如果未设置)
        if not metadata.canonical_url:
            canonical_base = config.get('global.canonical_base_url')
            if canonical_base:
                slug = article_path.stem.lower().replace(' ', '-')
                metadata.canonical_url = f"{canonical_base}/{slug}"
                logger.info(f"🔗 自动生成 canonical URL: {metadata.canonical_url}")
        
        # 4. 发布到各平台
        success_count = 0
        failed_count = 0
        
        for adapter in adapters:
            # 检查是否已发布
            if state_manager.is_published(str(article_path), adapter.platform_name):
                published_url = state_manager.get_published_url(str(article_path), adapter.platform_name)
                logger.info(f"⏭️  {adapter.platform_name} 已发布,跳过: {published_url}")
                continue
            
            # 发布文章
            logger.info(f"\n🚀 发布到 {adapter.platform_name}...")
            result = adapter.publish(metadata, content)
            
            # 记录结果
            state_manager.record_publish(str(article_path), adapter.platform_name, result)
            
            if result.success:
                success_count += 1
                logger.success(f"✅ {adapter.platform_name}: {result.article_url}")
            else:
                failed_count += 1
                logger.error(f"❌ {adapter.platform_name}: {result.error_message}")
        
        # 5. 总结
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 发布完成! 成功: {success_count}, 失败: {failed_count}")
        logger.info(f"{'='*60}\n")
    
    except Exception as e:
        logger.error(f"❌ 处理文章失败: {e}")


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="OmniPublish - 全平台文章发布工具")
    parser.add_argument('--file', help='指定要发布的文章路径')
    parser.add_argument('--mode', choices=['auto', 'manual'], default='manual', help='发布模式')
    parser.add_argument('--log-level', default='INFO', help='日志级别')
    parser.add_argument('--skip-validation', action='store_true', help='跳过 API 验证（用于网络问题时）')
    args = parser.parse_args()
    
    # 加载环境变量
    load_dotenv()
    
    # 初始化日志
    setup_logger(args.log_level)
    
    logger.info("🚀 OmniPublish 启动")
    logger.info(f"📅 版本: 1.0.0")
    
    try:
        # 加载配置
        config = ConfigLoader()
        
        # 初始化图床客户端 (可选)
        asset_manager = None
        r2_config = config.get('image_storage.cloudflare_r2')
        
        # 检查 R2 配置是否完整
        if r2_config and all([
            r2_config.get('account_id'),
            r2_config.get('access_key_id'),
            r2_config.get('secret_access_key'),
            r2_config.get('bucket_name'),
            r2_config.get('public_url')
        ]):
            try:
                r2_client = CloudflareR2Client(
                    account_id=r2_config['account_id'],
                    access_key=r2_config['access_key_id'],
                    secret_key=r2_config['secret_access_key'],
                    bucket=r2_config['bucket_name'],
                    public_url=r2_config['public_url']
                )
                asset_manager = AssetManager(r2_client)
                logger.info("✅ 图床客户端已初始化")
            except Exception as e:
                logger.warning(f"⚠️ 图床客户端初始化失败,将跳过图片处理: {e}")
        else:
            logger.warning("⚠️ R2 配置不完整,将跳过图片处理")
        
        # 初始化核心组件
        state_manager = StateManager()
        
        # 初始化适配器
        adapters = init_adapters(config, args.skip_validation)
        
        if not adapters:
            logger.error("❌ 没有可用的平台适配器,请检查配置")
            sys.exit(1)
        
        logger.info(f"✅ 已启用 {len(adapters)} 个平台适配器")
        
        # 发布文章
        if args.file:
            # 发布指定文章
            publish_article(args.file, config, adapters, state_manager, asset_manager)
        elif args.mode == 'auto':
            # 自动发布模式 (发布 articles/ 目录下的所有文章)
            articles_dir = Path('articles')
            if not articles_dir.exists():
                logger.error("❌ articles/ 目录不存在")
                sys.exit(1)
            
            articles = list(articles_dir.glob('*.md'))
            logger.info(f"📚 找到 {len(articles)} 篇文章")
            
            for article in articles:
                publish_article(str(article), config, adapters, state_manager, asset_manager)
        else:
            logger.error("❌ 请使用 --file 指定文章路径,或使用 --mode auto 自动发布")
            sys.exit(1)
        
        logger.info("✅ OmniPublish 执行完成")
    
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
