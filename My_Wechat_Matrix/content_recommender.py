#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容推荐与检索系统
基于账户、主题、效果评分的智能推荐
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from content_library import ContentLibrary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentRecommendationEngine:
    """内容推荐引擎"""
    
    def __init__(self, library: ContentLibrary = None):
        """初始化推荐引擎"""
        self.library = library or ContentLibrary()
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / "matrix_config.json"
        
        # 加载账户配置
        self._load_account_configs()
    
    def _load_account_configs(self):
        """加载所有账户配置"""
        self.account_configs = {}
        accounts_dir = self.base_dir / "accounts"
        
        for account_dir in accounts_dir.iterdir():
            if account_dir.is_dir():
                config_file = account_dir / "account_config.json"
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self.account_configs[account_dir.name] = json.load(f)
    
    def recommend_for_reuse(self, account_name: str, topic: str = None, limit: int = 10) -> List[Dict]:
        """
        为账户推荐可复用的高质量内容
        
        Args:
            account_name: 账户名称
            topic: 可选的主题关键词
            limit: 返回推荐数量
        
        Returns:
            推荐的内容列表
        """
        logger.info(f"🔍 为 {account_name} 推荐可复用内容...")
        
        # 获取账户配置
        account_config = self.account_configs.get(account_name, {})
        account_keywords = account_config.get("keywords", [])
        
        # 1. 优先推荐本账户高评分内容
        self_articles = self.library.search_articles(
            account_name=account_name,
            min_rating=3.0,
            limit=limit // 2
        )
        
        recommendations = self_articles.copy()
        
        # 2. 推荐其他账户相关内容
        if len(recommendations) < limit:
            other_keywords = []
            for kw in account_keywords:
                other_articles = self.library.search_articles(
                    tags=[kw],
                    min_rating=2.0,
                    limit=limit - len(recommendations)
                )
                recommendations.extend(other_articles)
        
        # 3. 如果指定了主题，进行主题过滤和排序
        if topic:
            recommendations = self._filter_by_topic(recommendations, topic)
        
        logger.info(f"✅ 生成了 {len(recommendations[:limit])} 条推荐")
        return recommendations[:limit]
    
    def _filter_by_topic(self, articles: List[Dict], topic: str) -> List[Dict]:
        """按主题关键词过滤和排序文章"""
        topic_keywords = topic.lower().split()
        
        scored_articles = []
        for article in articles:
            title_lower = article.get("title", "").lower()
            content_lower = article.get("content", "").lower()[:500]
            
            # 计算主题匹配分数
            title_matches = sum(1 for kw in topic_keywords if kw in title_lower)
            content_matches = sum(1 for kw in topic_keywords if kw in content_lower)
            topic_score = title_matches * 2 + content_matches  # 标题权重更高
            
            scored_articles.append({
                **article,
                "topic_score": topic_score
            })
        
        # 按topic_score排序
        scored_articles.sort(key=lambda x: x["topic_score"], reverse=True)
        
        # 只返回有匹配的文章
        return [a for a in scored_articles if a["topic_score"] > 0]
    
    def recommend_templates(self, account_name: str, category: str = None) -> List[Dict]:
        """
        推荐可用的内容模板
        
        Args:
            account_name: 账户名称
            category: 可选的类别
        
        Returns:
            推荐的模板列表
        """
        logger.info(f"📋 为 {account_name} 推荐内容模板...")
        
        templates = self.library.list_templates(for_accounts=account_name)
        
        # 按使用次数排序
        templates.sort(key=lambda x: x["usage_count"], reverse=True)
        
        logger.info(f"✅ 找到 {len(templates)} 个可用模板")
        return templates[:10]
    
    def find_similar_for_adaptation(self, article_id: int, min_similarity: float = 0.6) -> List[Dict]:
        """
        查找相似文章用于改写
        
        Args:
            article_id: 源文章ID
            min_similarity: 最小相似度阈值
        
        Returns:
            相似文章列表
        """
        logger.info(f"🔄 查找可改写的相似文章 (源文章ID: {article_id})...")
        
        similar_articles = self.library.get_similar_articles(
            article_id, 
            threshold=min_similarity,
            limit=10
        )
        
        logger.info(f"✅ 找到 {len(similar_articles)} 篇相似文章")
        return similar_articles
    
    def get_trending_topics(self, account_name: str = None, days: int = 7, limit: int = 10) -> List[Dict]:
        """
        获取热门主题趋势
        
        Args:
            account_name: 可选的账户名称
            days: 查看天数范围
            limit: 返回数量
        
        Returns:
            热门主题列表
        """
        logger.info(f"📊 获取热门主题趋势 (近{days}天)...")
        
        # 这里可以整合外部热搜API的数据
        # 示例：集成百度热搜、微博热搜等
        
        trending_topics = [
            {
                "topic": "AI效率提升",
                "frequency": 15,
                "trending_up": True,
                "relevance_score": 0.95
            },
            {
                "topic": "副业赚钱",
                "frequency": 12,
                "trending_up": True,
                "relevance_score": 0.85
            },
            {
                "topic": "冬季养生",
                "frequency": 8,
                "trending_up": False,
                "relevance_score": 0.75
            }
        ]
        
        return trending_topics[:limit]
    
    def analyze_content_gap(self, account_name: str) -> Dict:
        """
        分析账户的内容空缺
        
        Args:
            account_name: 账户名称
        
        Returns:
            空缺分析报告
        """
        logger.info(f"📈 分析 {account_name} 的内容空缺...")
        
        account_config = self.account_configs.get(account_name, {})
        keywords = account_config.get("keywords", [])
        
        # 获取已有内容的标签覆盖
        articles = self.library.search_articles(account_name=account_name, limit=100)
        
        covered_keywords = set()
        for article in articles:
            if article.get("tags"):
                for tag in article["tags"]:
                    if any(kw.lower() in tag.lower() for kw in keywords):
                        covered_keywords.add(tag)
        
        # 找出未覆盖的关键词
        missing_keywords = [kw for kw in keywords if kw not in covered_keywords]
        
        gap_report = {
            "account_name": account_name,
            "total_keywords": len(keywords),
            "covered_keywords": len(covered_keywords),
            "coverage_rate": round(len(covered_keywords) / len(keywords) * 100, 2) if keywords else 0,
            "missing_keywords": missing_keywords,
            "suggested_topics": self._generate_gap_topics(missing_keywords)
        }
        
        logger.info(f"✅ 内容覆盖率: {gap_report['coverage_rate']}%")
        return gap_report
    
    def _generate_gap_topics(self, keywords: List[str]) -> List[str]:
        """根据缺失关键词生成建议主题"""
        suggested_topics = []
        
        for keyword in keywords[:5]:  # 只处理前5个
            topics = [
                f"{keyword}的10个必知技巧",
                f"如何用{keyword}提升效率",
                f"{keyword}的常见误区解析",
                f"{keyword}初学者完整指南",
                f"{keyword}案例分享与经验总结"
            ]
            suggested_topics.extend(topics[:2])
        
        return suggested_topics[:10]


class ContentOptimizer:
    """内容优化器"""
    
    def __init__(self, ai_client=None):
        """初始化优化器"""
        self.library = ContentLibrary()
        self.ai_client = ai_client
    
    def suggest_improvements(self, article_id: int) -> Dict:
        """
        建议内容改进
        
        Args:
            article_id: 文章ID
        
        Returns:
            改进建议列表
        """
        logger.info(f"💡 分析文章改进建议 (ID: {article_id})...")
        
        conn = __import__('sqlite3').connect(self.library.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT content, title, rating, views
            FROM articles WHERE id = ?
        """, (article_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            logger.warning(f"⚠️ 文章不存在 (ID: {article_id})")
            return {}
        
        content, title, rating, views = row
        
        suggestions = {
            "article_id": article_id,
            "current_rating": rating,
            "suggestions": []
        }
        
        # 1. 内容长度建议
        content_length = len(content)
        if content_length < 500:
            suggestions["suggestions"].append({
                "type": "content_length",
                "issue": "内容过短",
                "suggestion": "建议增加到800-1500字符以获得更好的SEO效果",
                "priority": "high"
            })
        elif content_length > 3000:
            suggestions["suggestions"].append({
                "type": "content_length",
                "issue": "内容过长",
                "suggestion": "考虑分割成多个部分以改善阅读体验",
                "priority": "medium"
            })
        
        # 2. 标题优化建议
        title_length = len(title)
        if title_length < 10:
            suggestions["suggestions"].append({
                "type": "title",
                "issue": "标题过短",
                "suggestion": "建议将标题扩展到10-20个字符",
                "priority": "medium"
            })
        
        # 3. 参与度建议
        if views > 0 and rating < 1:
            suggestions["suggestions"].append({
                "type": "engagement",
                "issue": "参与度低",
                "suggestion": "考虑添加CTA(行动号召)，如提问或调查",
                "priority": "high"
            })
        
        logger.info(f"✅ 生成了 {len(suggestions['suggestions'])} 条改进建议")
        return suggestions
    
    def batch_optimize_content(self, account_name: str, max_items: int = 10) -> Dict:
        """
        批量优化账户内容
        
        Args:
            account_name: 账户名称
            max_items: 最多优化数量
        
        Returns:
            优化结果统计
        """
        logger.info(f"🚀 开始批量优化 {account_name} 的内容...")
        
        articles = self.library.search_articles(
            account_name=account_name,
            min_rating=0,
            limit=max_items
        )
        
        optimization_results = {
            "account_name": account_name,
            "processed": 0,
            "suggestions_count": 0,
            "details": []
        }
        
        for article in articles:
            suggestions = self.suggest_improvements(article["id"])
            
            if suggestions.get("suggestions"):
                optimization_results["details"].append({
                    "article_id": article["id"],
                    "title": article["title"],
                    "suggestions_count": len(suggestions["suggestions"])
                })
                optimization_results["suggestions_count"] += len(suggestions["suggestions"])
            
            optimization_results["processed"] += 1
        
        logger.info(f"✅ 优化完成: 处理{optimization_results['processed']}篇，生成{optimization_results['suggestions_count']}条建议")
        return optimization_results
