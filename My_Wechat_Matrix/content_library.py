#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容库管理系统
支持内容的存储、检索、复用和优化
"""

import json
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentLibrary:
    """内容库管理器"""
    
    def __init__(self, db_path: str = "content_library.db"):
        """初始化内容库"""
        self.base_dir = Path(__file__).parent
        self.db_path = self.base_dir / db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 内容表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                account_name TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                rating REAL DEFAULT 0,
                status TEXT DEFAULT 'draft'
            )
        """)
        
        # 内容段落表（用于段落级别的复用）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paragraphs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paragraph_hash TEXT UNIQUE NOT NULL,
                article_id INTEGER,
                paragraph_content TEXT NOT NULL,
                paragraph_type TEXT,
                account_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 1,
                reuse_times INTEGER DEFAULT 0,
                rating REAL DEFAULT 0,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)
        
        # 模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT UNIQUE NOT NULL,
                template_content TEXT NOT NULL,
                category TEXT,
                for_accounts TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0,
                rating REAL DEFAULT 0,
                description TEXT
            )
        """)
        
        # 相似度缓存表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS similarity_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id1 INTEGER NOT NULL,
                article_id2 INTEGER NOT NULL,
                similarity REAL NOT NULL,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(article_id1, article_id2)
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_account ON articles(account_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON articles(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON articles(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created ON articles(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rating ON articles(rating DESC)")
        
        conn.commit()
        conn.close()
        logger.info(f"✅ 数据库初始化完成: {self.db_path}")
    
    @staticmethod
    def calculate_hash(content: str) -> str:
        """计算内容哈希"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_article(
        self, 
        title: str, 
        content: str, 
        account_name: str,
        category: str = None,
        tags: List[str] = None,
        source: str = "generated"
    ) -> Optional[int]:
        """添加文章到内容库"""
        article_hash = self.calculate_hash(content)
        
        # 检查是否已存在
        if self.get_article_by_hash(article_hash):
            logger.warning(f"⚠️ 内容已存在（哈希重复）: {title[:30]}...")
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            tags_str = ",".join(tags) if tags else ""
            cursor.execute("""
                INSERT INTO articles 
                (article_hash, title, content, account_name, category, tags, source, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (article_hash, title, content, account_name, category, tags_str, source, "draft"))
            
            article_id = cursor.lastrowid
            
            # 提取段落并存储（传入当前的 conn 连接）
            self._extract_and_store_paragraphs(conn, content, article_id, account_name)
            
            conn.commit()
            logger.info(f"✅ 文章已添加: {title[:30]}... (ID: {article_id})")
            return article_id
        
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ 文章已存在: {title[:30]}...")
            return None
        finally:
            conn.close()
    
    def _extract_and_store_paragraphs(self, conn, content: str, article_id: int, account_name: str):
        """提取并存储段落（复用传入的数据库连接）"""
        paragraphs = content.split('\n\n')
        cursor = conn.cursor()
        
        for para in paragraphs:
            if len(para.strip()) > 20:  # 只存储有意义的段落
                para_hash = self.calculate_hash(para)
                
                try:
                    cursor.execute("""
                        INSERT INTO paragraphs 
                        (paragraph_hash, article_id, paragraph_content, account_name, paragraph_type)
                        VALUES (?, ?, ?, ?, ?)
                    """, (para_hash, article_id, para, account_name, "normal"))
                except sqlite3.IntegrityError:
                    # 段落已存在，增加复用计数
                    cursor.execute("""
                        UPDATE paragraphs SET reuse_times = reuse_times + 1 
                        WHERE paragraph_hash = ?
                    """, (para_hash,))
    
    def get_article_by_hash(self, article_hash: str) -> Optional[Dict]:
        """根据哈希获取文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content, account_name, category, tags, rating, status
            FROM articles WHERE article_hash = ?
        """, (article_hash,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "account_name": row[3],
                "category": row[4],
                "tags": row[5].split(",") if row[5] else [],
                "rating": row[6],
                "status": row[7]
            }
        return None
    
    def search_articles(
        self,
        account_name: str = None,
        category: str = None,
        tags: List[str] = None,
        min_rating: float = 0,
        limit: int = 20
    ) -> List[Dict]:
        """搜索文章"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, title, content, account_name, category, rating, status FROM articles WHERE 1=1"
        params = []
        
        if account_name:
            query += " AND account_name = ?"
            params.append(account_name)
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if min_rating > 0:
            query += " AND rating >= ?"
            params.append(min_rating)
        
        if tags:
            # 搜索包含任意标签的文章
            tag_conditions = " OR ".join([f"tags LIKE ?" for _ in tags])
            query += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])
        
        query += f" ORDER BY rating DESC, created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "account_name": row[3],
                "category": row[4],
                "rating": row[5],
                "status": row[6]
            })
        
        return results
    
    def get_similar_articles(self, article_id: int, threshold: float = 0.7, limit: int = 5) -> List[Dict]:
        """获取相似文章"""
        from difflib import SequenceMatcher
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 获取源文章内容
        cursor.execute("SELECT content FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        if not row:
            return []
        
        source_content = row[0]
        
        # 获取所有其他文章
        cursor.execute("""
            SELECT id, title, content, account_name, rating 
            FROM articles WHERE id != ? ORDER BY created_at DESC LIMIT 100
        """, (article_id,))
        
        candidates = cursor.fetchall()
        conn.close()
        
        # 计算相似度
        similar_articles = []
        for candidate in candidates:
            similarity = SequenceMatcher(
                None, 
                source_content[:500],  # 只比较前500个字符以提高性能
                candidate[2][:500]
            ).ratio()
            
            if similarity >= threshold:
                similar_articles.append({
                    "id": candidate[0],
                    "title": candidate[1],
                    "similarity": round(similarity, 3),
                    "account_name": candidate[3],
                    "rating": candidate[4]
                })
        
        # 按相似度排序
        similar_articles.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_articles[:limit]
    
    def update_article_rating(self, article_id: int, views: int = 0, likes: int = 0, 
                             shares: int = 0, comments: int = 0):
        """更新文章评分和统计"""
        # 计算评分：(点赞数*2 + 分享数*3 + 评论数*1) / 浏览数 * 100
        total_interactions = likes * 2 + shares * 3 + comments * 1
        rating = (total_interactions / max(views, 1)) * 100 if views > 0 else 0
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE articles 
            SET views = ?, likes = ?, shares = ?, comments = ?, rating = ?, 
                published_at = CURRENT_TIMESTAMP, status = ?
            WHERE id = ?
        """, (views, likes, shares, comments, rating, "published", article_id))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ 文章评分已更新 (ID: {article_id}, 评分: {rating:.2f})")
    
    def get_high_quality_articles(self, account_name: str, limit: int = 10) -> List[Dict]:
        """获取高质量文章（用于模板提取）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content, rating, published_at
            FROM articles 
            WHERE account_name = ? AND status = 'published' AND rating > 0
            ORDER BY rating DESC, published_at DESC
            LIMIT ?
        """, (account_name, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "rating": row[3],
                "published_at": row[4]
            })
        
        return results
    
    def extract_template(self, article_id: int, template_name: str, description: str = "") -> Optional[int]:
        """从高质量文章提取模板"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT content, account_name FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"⚠️ 文章不存在 (ID: {article_id})")
            return None
        
        content, account_name = row
        
        # 创建模板
        try:
            cursor.execute("""
                INSERT INTO templates 
                (template_name, template_content, for_accounts, description)
                VALUES (?, ?, ?, ?)
            """, (template_name, content, account_name, description))
            
            template_id = cursor.lastrowid
            conn.commit()
            logger.info(f"✅ 模板已提取: {template_name} (ID: {template_id})")
            return template_id
        
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ 模板已存在: {template_name}")
            return None
        finally:
            conn.close()
    
    def get_template(self, template_name: str) -> Optional[str]:
        """获取模板内容"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT template_content, usage_count FROM templates 
            WHERE template_name = ?
        """, (template_name,))
        
        row = cursor.fetchone()
        
        if row:
            # 更新使用计数
            cursor.execute("""
                UPDATE templates SET usage_count = usage_count + 1 
                WHERE template_name = ?
            """, (template_name,))
            conn.commit()
        
        conn.close()
        return row[0] if row else None
    
    def list_templates(self, for_accounts: str = None) -> List[Dict]:
        """列出所有模板"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if for_accounts:
            query = """
                SELECT id, template_name, description, usage_count, rating, created_at
                FROM templates 
                WHERE for_accounts LIKE ?
                ORDER BY usage_count DESC
            """
            cursor.execute(query, (f"%{for_accounts}%",))
        else:
            query = """
                SELECT id, template_name, description, usage_count, rating, created_at
                FROM templates 
                ORDER BY usage_count DESC
            """
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "usage_count": row[3],
                "rating": row[4],
                "created_at": row[5]
            })
        
        return results
    
    def get_statistics(self, account_name: str = None) -> Dict:
        """获取内容库统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        if account_name:
            # 单账号统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(shares) as total_shares,
                    AVG(rating) as avg_rating
                FROM articles 
                WHERE account_name = ?
            """, (account_name,))
        else:
            # 全局统计
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(views) as total_views,
                    SUM(likes) as total_likes,
                    SUM(shares) as total_shares,
                    AVG(rating) as avg_rating
                FROM articles
            """)
        
        row = cursor.fetchone()
        
        stats["total_articles"] = row[0] or 0
        stats["total_views"] = row[1] or 0
        stats["total_likes"] = row[2] or 0
        stats["total_shares"] = row[3] or 0
        stats["avg_rating"] = round(row[4], 2) if row[4] else 0
        
        # 获取模板统计
        cursor.execute("SELECT COUNT(*) FROM templates")
        stats["total_templates"] = cursor.fetchone()[0]
        
        # 获取段落统计
        cursor.execute("""
            SELECT COUNT(*) as total, SUM(reuse_times) as total_reuse
            FROM paragraphs
        """)
        para_row = cursor.fetchone()
        stats["total_paragraphs"] = para_row[0] or 0
        stats["paragraph_reuse_times"] = para_row[1] or 0
        
        conn.close()
        return stats
    
    def export_library(self, export_path: str = "content_library_export.json"):
        """导出内容库为JSON"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "articles": [],
            "templates": [],
            "statistics": self.get_statistics()
        }
        
        # 导出所有文章
        cursor.execute("""
            SELECT id, title, content, account_name, category, tags, rating, status
            FROM articles ORDER BY created_at DESC
        """)
        
        for row in cursor.fetchall():
            export_data["articles"].append({
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "account_name": row[3],
                "category": row[4],
                "tags": row[5].split(",") if row[5] else [],
                "rating": row[6],
                "status": row[7]
            })
        
        # 导出所有模板
        cursor.execute("""
            SELECT template_name, template_content, for_accounts, description
            FROM templates ORDER BY usage_count DESC
        """)
        
        for row in cursor.fetchall():
            export_data["templates"].append({
                "name": row[0],
                "content": row[1],
                "for_accounts": row[2],
                "description": row[3]
            })
        
        conn.close()
        
        # 保存为JSON
        export_full_path = self.base_dir / export_path
        with open(export_full_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 内容库已导出: {export_full_path}")
        return str(export_full_path)
