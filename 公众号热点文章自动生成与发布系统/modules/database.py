# 数据库模块
# 负责数据的存储和检索

import pymysql
import logging
from datetime import datetime

class Database:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('database')
        self.conn = None
    
    def connect(self):
        """连接到数据库"""
        try:
            self.conn = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                charset=self.config['charset']
            )
            return True
        except Exception as e:
            self.logger.error(f"数据库连接失败: {str(e)}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def init_database(self):
        """初始化数据库表结构"""
        try:
            # 尝试连接到数据库，如果数据库不存在则创建
            try:
                conn = pymysql.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    user=self.config['user'],
                    password=self.config['password'],
                    charset=self.config['charset']
                )
                cursor = conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                self.logger.error(f"创建数据库失败: {str(e)}")
                return False
            
            # 连接到指定数据库
            if not self.connect():
                return False
            
            cursor = self.conn.cursor()
            
            # 创建热点话题表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic_name VARCHAR(255) NOT NULL,
                read_count BIGINT,
                discussion_count BIGINT,
                rank_index INT,
                status VARCHAR(20) DEFAULT 'new',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY (topic_name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建微博内容表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS weibos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic_id INT,
                weibo_id VARCHAR(64),
                user_name VARCHAR(255),
                content TEXT,
                publish_time DATETIME,
                like_count INT,
                repost_count INT,
                comment_count INT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id),
                UNIQUE KEY (weibo_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 创建文章表
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INT AUTO_INCREMENT PRIMARY KEY,
                topic_id INT,
                title VARCHAR(255) NOT NULL,
                content LONGTEXT NOT NULL,
                status VARCHAR(20) DEFAULT 'new',
                file_path VARCHAR(255),
                wechat_media_id VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (topic_id) REFERENCES topics(id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            self.conn.commit()
            cursor.close()
            self.logger.info("数据库初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"初始化数据库失败: {str(e)}")
            return False
    
    def save_topic(self, topic):
        """保存热点话题"""
        if not self.conn and not self.connect():
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # 检查话题是否已存在
            cursor.execute("SELECT id FROM topics WHERE topic_name = %s", (topic['topic_name'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新已存在的话题
                topic_id = existing[0]
                cursor.execute("""
                UPDATE topics SET 
                    read_count = %s,
                    discussion_count = %s,
                    rank_index = %s,
                    updated_at = %s
                WHERE id = %s
                """, (
                    topic.get('read_count', 0),
                    topic.get('discussion_count', 0),
                    topic.get('rank_index', 0),
                    datetime.now(),
                    topic_id
                ))
            else:
                # 插入新话题
                cursor.execute("""
                INSERT INTO topics (topic_name, read_count, discussion_count, rank_index, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """, (
                    topic['topic_name'],
                    topic.get('read_count', 0),
                    topic.get('discussion_count', 0),
                    topic.get('rank_index', 0),
                    datetime.now()
                ))
                topic_id = cursor.lastrowid
            
            self.conn.commit()
            cursor.close()
            return topic_id
        except Exception as e:
            self.logger.error(f"保存话题失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def save_weibo(self, weibo):
        """保存微博内容"""
        if not self.conn and not self.connect():
            return None
        
        try:
            cursor = self.conn.cursor()
            
            # 检查微博是否已存在
            cursor.execute("SELECT id FROM weibos WHERE weibo_id = %s", (weibo['weibo_id'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新已存在的微博
                weibo_id = existing[0]
                cursor.execute("""
                UPDATE weibos SET 
                    like_count = %s,
                    repost_count = %s,
                    comment_count = %s
                WHERE id = %s
                """, (
                    weibo.get('like_count', 0),
                    weibo.get('repost_count', 0),
                    weibo.get('comment_count', 0),
                    weibo_id
                ))
            else:
                # 插入新微博
                cursor.execute("""
                INSERT INTO weibos (topic_id, weibo_id, user_name, content, publish_time, like_count, repost_count, comment_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    weibo['topic_id'],
                    weibo['weibo_id'],
                    weibo.get('user_name', ''),
                    weibo.get('content', ''),
                    weibo.get('publish_time', datetime.now()),
                    weibo.get('like_count', 0),
                    weibo.get('repost_count', 0),
                    weibo.get('comment_count', 0)
                ))
                weibo_id = cursor.lastrowid
            
            self.conn.commit()
            cursor.close()
            return weibo_id
        except Exception as e:
            self.logger.error(f"保存微博失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def save_article(self, article):
        """保存生成的文章"""
        if not self.conn and not self.connect():
            return None
        
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
            INSERT INTO articles (topic_id, title, content, file_path, status)
            VALUES (%s, %s, %s, %s, %s)
            """, (
                article['topic_id'],
                article['title'],
                article['content'],
                article.get('file_path', ''),
                'new'
            ))
            
            article_id = cursor.lastrowid
            self.conn.commit()
            cursor.close()
            return article_id
        except Exception as e:
            self.logger.error(f"保存文章失败: {str(e)}")
            self.conn.rollback()
            return None
    
    def get_unprocessed_topics(self, limit=5):
        """获取未处理的热点话题"""
        if not self.conn and not self.connect():
            return []
        
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
            SELECT * FROM topics 
            WHERE status = 'new' 
            ORDER BY rank_index ASC, discussion_count DESC 
            LIMIT %s
            """, (limit,))
            
            topics = cursor.fetchall()
            cursor.close()
            return topics
        except Exception as e:
            self.logger.error(f"获取未处理话题失败: {str(e)}")
            return []
    
    def get_weibos_by_topic(self, topic_id, limit=10):
        """获取指定话题下的微博内容"""
        if not self.conn and not self.connect():
            return []
        
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
            SELECT * FROM weibos 
            WHERE topic_id = %s 
            ORDER BY like_count DESC, comment_count DESC 
            LIMIT %s
            """, (topic_id, limit))
            
            weibos = cursor.fetchall()
            cursor.close()
            return weibos
        except Exception as e:
            self.logger.error(f"获取话题微博失败: {str(e)}")
            return []
    
    def get_unuploaded_articles(self, limit=5):
        """获取未上传的文章"""
        if not self.conn and not self.connect():
            return []
        
        try:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
            SELECT * FROM articles 
            WHERE status = 'new' 
            ORDER BY created_at ASC 
            LIMIT %s
            """, (limit,))
            
            articles = cursor.fetchall()
            cursor.close()
            return articles
        except Exception as e:
            self.logger.error(f"获取未上传文章失败: {str(e)}")
            return []
    
    def update_topic_status(self, topic_id, status):
        """更新话题状态"""
        if not self.conn and not self.connect():
            return False
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
            UPDATE topics SET status = %s WHERE id = %s
            """, (status, topic_id))
            
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"更新话题状态失败: {str(e)}")
            self.conn.rollback()
            return False
    
    def update_article_status(self, article_id, status, wechat_media_id=None):
        """更新文章状态"""
        if not self.conn and not self.connect():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            if wechat_media_id:
                cursor.execute("""
                UPDATE articles SET status = %s, wechat_media_id = %s WHERE id = %s
                """, (status, wechat_media_id, article_id))
            else:
                cursor.execute("""
                UPDATE articles SET status = %s WHERE id = %s
                """, (status, article_id))
            
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"更新文章状态失败: {str(e)}")
            self.conn.rollback()
            return False