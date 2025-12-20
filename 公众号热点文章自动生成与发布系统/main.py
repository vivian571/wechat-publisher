# 微博热点文章自动生成与发布系统
# 主程序入口

import os
import time
import logging
import schedule
from datetime import datetime

# 导入配置
from config import DB_CONFIG, WEIBO_CONFIG, AI_MODEL_CONFIG, WECHAT_CONFIG, PATH_CONFIG, LOG_CONFIG

# 导入各模块
from modules.weibo_crawler import WeiboCrawler
from modules.article_generator import ArticleGenerator
from modules.wechat_uploader import WechatUploader
from modules.database import Database

# 初始化日志
def setup_logging():
    # 确保日志目录存在
    os.makedirs(PATH_CONFIG['log_dir'], exist_ok=True)
    
    # 配置日志
    log_file = os.path.join(PATH_CONFIG['log_dir'], f'system_{datetime.now().strftime("%Y%m%d")}.log')
    logging.basicConfig(
        level=getattr(logging, LOG_CONFIG['level']),
        format=LOG_CONFIG['format'],
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('weibo_article_system')

# 确保所有必要的目录都存在
def ensure_directories():
    for dir_path in PATH_CONFIG.values():
        os.makedirs(dir_path, exist_ok=True)
        logging.info(f'确保目录存在: {dir_path}')

# 微博热点抓取任务
def crawl_weibo_task(crawler, db):
    try:
        logging.info('开始抓取微博热点')
        hot_topics = crawler.get_hot_topics()
        
        for topic in hot_topics:
            # 存储热点话题
            topic_id = db.save_topic(topic)
            
            # 获取该话题下的热门微博
            hot_weibos = crawler.get_hot_weibos_by_topic(topic['topic_name'])
            
            # 存储热门微博
            for weibo in hot_weibos:
                weibo['topic_id'] = topic_id
                db.save_weibo(weibo)
                
        logging.info(f'成功抓取 {len(hot_topics)} 个热点话题')
    except Exception as e:
        logging.error(f'抓取微博热点失败: {str(e)}')

# 文章生成任务
def generate_article_task(generator, db):
    try:
        logging.info('开始生成文章')
        # 获取未处理的热点话题
        topics = db.get_unprocessed_topics()
        
        for topic in topics:
            # 获取该话题下的热门微博
            weibos = db.get_weibos_by_topic(topic['id'])
            
            if weibos:
                # 生成文章
                article = generator.generate_article(topic, weibos)
                
                # 保存文章
                article_id = db.save_article(article)
                
                # 更新话题状态为已处理
                db.update_topic_status(topic['id'], 'processed')
                
                logging.info(f'成功为话题 "{topic["topic_name"]}" 生成文章')
            else:
                logging.warning(f'话题 "{topic["topic_name"]}" 下没有足够的微博内容，跳过文章生成')
    except Exception as e:
        logging.error(f'生成文章失败: {str(e)}')

# 微信公众号上传任务
def upload_wechat_task(uploader, db):
    try:
        logging.info('开始上传文章到微信公众号')
        # 获取未上传的文章
        articles = db.get_unuploaded_articles()
        
        for article in articles:
            # 上传文章到微信公众号草稿箱
            result = uploader.upload_to_draft(article)
            
            if result['success']:
                # 更新文章状态为已上传
                db.update_article_status(article['id'], 'uploaded')
                logging.info(f'成功上传文章 "{article["title"]}" 到微信公众号草稿箱')
            else:
                logging.error(f'上传文章 "{article["title"]}" 失败: {result["message"]}')
    except Exception as e:
        logging.error(f'上传文章到微信公众号失败: {str(e)}')

# 主函数
def main():
    # 设置日志
    logger = setup_logging()
    logger.info('系统启动')
    
    # 确保目录存在
    ensure_directories()
    
    try:
        # 初始化数据库
        db = Database(DB_CONFIG)
        db.init_database()
        
        # 初始化各模块
        weibo_crawler = WeiboCrawler(WEIBO_CONFIG)
        article_generator = ArticleGenerator(AI_MODEL_CONFIG, PATH_CONFIG)
        wechat_uploader = WechatUploader(WECHAT_CONFIG)
        
        # 设置定时任务
        # 微博热点抓取任务
        schedule.every(WEIBO_CONFIG['crawl_interval']).seconds.do(
            crawl_weibo_task, crawler=weibo_crawler, db=db
        )
        
        # 文章生成任务
        schedule.every(AI_MODEL_CONFIG['generation_interval']).seconds.do(
            generate_article_task, generator=article_generator, db=db
        )
        
        # 微信公众号上传任务
        schedule.every(WECHAT_CONFIG['upload_interval']).seconds.do(
            upload_wechat_task, uploader=wechat_uploader, db=db
        )
        
        # 立即执行一次抓取任务
        crawl_weibo_task(weibo_crawler, db)
        
        logger.info('所有任务已设置，开始运行定时任务')
        
        # 运行定时任务
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info('系统被用户中断')
    except Exception as e:
        logger.error(f'系统运行出错: {str(e)}')
    finally:
        logger.info('系统关闭')

if __name__ == '__main__':
    main()