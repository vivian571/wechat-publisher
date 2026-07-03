#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容库集成模块
将内容库与现有的generator、auto_scheduler集成
支持自动化工作流中的内容检索、复用和发布
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from content_library import ContentLibrary
from content_recommender import ContentRecommendationEngine, ContentOptimizer
from content_rewriter import ContentRewriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentWorkflowIntegrator:
    """内容库与自动化工作流集成器"""
    
    def __init__(self, config_path: str = "matrix_config.json"):
        """初始化集成器"""
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / config_path
        
        # 加载配置
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 初始化各模块
        self.library = ContentLibrary()
        self.recommender = ContentRecommendationEngine(self.library)
        self.optimizer = ContentOptimizer()
        self.rewriter = ContentRewriter()
        
        logger.info("✅ 内容工作流集成器已初始化")
    
    def generate_with_library_support(self, account_name: str, topic: str = None, 
                                     use_template: bool = True, use_similar: bool = True) -> Dict:
        """
        生成内容并集成内容库支持
        
        Args:
            account_name: 账户名称
            topic: 主题
            use_template: 是否使用模板
            use_similar: 是否查找相似内容参考
        
        Returns:
            生成的内容和相关元数据
        """
        logger.info(f"📝 开始生成内容: {account_name} - {topic}")
        
        result = {
            "account_name": account_name,
            "topic": topic,
            "generated_at": datetime.now().isoformat(),
            "content": "",
            "recommendations": [],
            "templates": [],
            "similar_articles": [],
            "optimization_suggestions": []
        }
        
        # 1. 获取推荐内容和模板
        if use_template or use_similar:
            result["templates"] = self.recommender.recommend_templates(account_name)
            
            if use_similar and result["templates"]:
                logger.info(f"📋 找到{len(result['templates'])}个模板")
                
                # 提取模板内容作为参考
                template_content = ""
                for template in result["templates"][:3]:
                    template_content = self.library.get_template(template["name"])
                    if template_content:
                        break
                
                result["recommendations"].append({
                    "type": "template",
                    "content": template_content[:500] if template_content else ""
                })
        
        # 2. 生成主要内容
        # 这里需要调用原有的 generator.py 中的生成逻辑
        # 为了演示，这里示例一个内容生成的框架
        
        generated_content = self._generate_content_from_ai(account_name, topic)
        result["content"] = generated_content
        
        if generated_content:
            # 3. 自动入库
            article_id = self._auto_store_content(
                title=topic or "未命名",
                content=generated_content,
                account_name=account_name,
                source="generated"
            )
            result["article_id"] = article_id
            
            # 4. 获取相似内容参考
            if use_similar and article_id:
                similar = self.recommender.find_similar_for_adaptation(article_id, min_similarity=0.5)
                result["similar_articles"] = similar[:3]
                logger.info(f"📚 找到{len(similar)}篇相似文章")
            
            # 5. 获取优化建议
            optimization = self.optimizer.suggest_improvements(article_id)
            result["optimization_suggestions"] = optimization.get("suggestions", [])
        
        logger.info(f"✅ 内容生成完成 (ID: {result.get('article_id')})")
        return result
    
    def _generate_content_from_ai(self, account_name: str, topic: str) -> Optional[str]:
        """
        调用AI生成内容（这里是一个placeholder，实际应集成generator.py）
        """
        try:
            # 从generator.py导入ContentGenerator
            from generator import ContentGenerator
            
            generator = ContentGenerator(str(self.config_path))
            account_dir = self.base_dir / "accounts" / account_name
            
            if not account_dir.exists():
                logger.warning(f"⚠️ 账户目录不存在: {account_dir}")
                return None
            
            # 使用generator生成内容
            # 这里需要根据实际的generator.py的接口进行调整
            logger.info(f"🤖 调用AI生成内容: {topic}")
            
            # 示例实现
            content = f"# {topic}\n\n这是一篇关于{topic}的精彩文章。\n\n(实际内容由AI模型生成)"
            
            return content
        
        except Exception as e:
            logger.error(f"❌ 内容生成失败: {e}")
            return None
    
    def _auto_store_content(self, title: str, content: str, account_name: str, 
                           source: str = "generated", tags: List[str] = None) -> Optional[int]:
        """
        自动将内容存储到库
        """
        try:
            article_id = self.library.add_article(
                title=title,
                content=content,
                account_name=account_name,
                category="auto_generated",
                tags=tags or [account_name],
                source=source
            )
            
            if article_id:
                logger.info(f"💾 内容已自动入库 (ID: {article_id})")
            
            return article_id
        
        except Exception as e:
            logger.error(f"❌ 内容入库失败: {e}")
            return None
    
    def publish_with_content_check(self, article_id: int, account_name: str) -> Dict:
        """
        发布前进行内容检查和优化建议
        
        Args:
            article_id: 文章ID
            account_name: 账户名称
        
        Returns:
            发布检查结果
        """
        logger.info(f"🔍 进行发布前检查 (ID: {article_id})...")
        
        check_result = {
            "article_id": article_id,
            "account_name": account_name,
            "status": "pending",
            "checks": [],
            "warnings": [],
            "recommendations": [],
            "can_publish": True
        }
        
        # 1. 获取文章
        conn = __import__('sqlite3').connect(self.library.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, content, rating FROM articles WHERE id = ?
        """, (article_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            check_result["status"] = "error"
            check_result["warnings"].append("文章不存在")
            check_result["can_publish"] = False
            return check_result
        
        title, content, rating = row
        
        # 2. 进行检查
        checks = {
            "title_length": {"pass": 10 <= len(title) <= 30, "message": f"标题长度: {len(title)} 字符"},
            "content_length": {"pass": len(content) >= 500, "message": f"内容长度: {len(content)} 字符"},
            "has_images": {"pass": "[图片]" in content or "[image]" in content.lower(), "message": "包含图片"},
            "readability": {"pass": len(content.split('\n')) >= 3, "message": "段落清晰"}
        }
        
        for check_name, check_info in checks.items():
            check_result["checks"].append({
                "check": check_name,
                "pass": check_info["pass"],
                "message": check_info["message"]
            })
            
            if not check_info["pass"]:
                check_result["warnings"].append(f"⚠️ {check_name}: {check_info['message']}")
        
        # 3. 获取优化建议
        optimization = self.optimizer.suggest_improvements(article_id)
        if optimization.get("suggestions"):
            for suggestion in optimization["suggestions"][:2]:
                check_result["recommendations"].append({
                    "priority": suggestion.get("priority"),
                    "issue": suggestion.get("issue"),
                    "suggestion": suggestion.get("suggestion")
                })
        
        # 4. 检查相似度过高
        similar = self.recommender.find_similar_for_adaptation(article_id, min_similarity=0.85)
        if similar:
            check_result["warnings"].append(f"⚠️ 发现{len(similar)}篇高度相似的文章，请检查是否存在重复")
        
        # 5. 生成最终报告
        check_result["status"] = "ready" if not check_result["warnings"] else "need_review"
        check_result["can_publish"] = len(check_result["warnings"]) == 0
        
        logger.info(f"✅ 检查完成: {'可以发布' if check_result['can_publish'] else '建议审核'}")
        return check_result
    
    def batch_process_for_publishing(self, account_name: str, topic: str = None, 
                                    count: int = 3) -> Dict:
        """
        批量生成、优化和准备内容用于发布
        
        Args:
            account_name: 账户名称
            topic: 主题（可选）
            count: 生成数量
        
        Returns:
            批处理结果
        """
        logger.info(f"🚀 开始批量处理: {account_name} x {count}篇")
        
        batch_result = {
            "account_name": account_name,
            "requested_count": count,
            "processed": 0,
            "success": 0,
            "articles": [],
            "statistics": {}
        }
        
        for i in range(count):
            logger.info(f"\n📄 处理第 {i+1}/{count} 篇...")
            
            # 生成内容
            generation = self.generate_with_library_support(
                account_name=account_name,
                topic=f"{topic} (第{i+1}篇)" if topic else None,
                use_template=True,
                use_similar=True
            )
            
            if generation.get("article_id"):
                # 检查内容
                check = self.publish_with_content_check(
                    generation["article_id"],
                    account_name
                )
                
                batch_result["articles"].append({
                    "article_id": generation["article_id"],
                    "title": generation.get("topic", "未命名"),
                    "can_publish": check["can_publish"],
                    "status": check["status"],
                    "warnings": check["warnings"]
                })
                
                batch_result["success"] += 1
            
            batch_result["processed"] += 1
        
        # 生成统计
        batch_result["statistics"] = self.library.get_statistics(account_name)
        
        logger.info(f"\n✅ 批处理完成: 成功{batch_result['success']}/{count}篇")
        return batch_result
    
    def analyze_and_optimize_library(self, account_name: str = None) -> Dict:
        """
        分析和优化内容库
        
        Args:
            account_name: 可选的账户名称
        
        Returns:
            分析结果
        """
        logger.info(f"📊 分析内容库...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "statistics": self.library.get_statistics(account_name),
            "content_gap": None,
            "top_performers": [],
            "optimization_opportunities": []
        }
        
        if account_name:
            # 分析内容空缺
            gap = self.recommender.analyze_content_gap(account_name)
            analysis["content_gap"] = gap
            
            # 获取高质量文章
            top_articles = self.library.get_high_quality_articles(account_name, limit=5)
            analysis["top_performers"] = [
                {
                    "id": a["id"],
                    "title": a["title"],
                    "rating": a["rating"],
                    "published_at": a["published_at"]
                }
                for a in top_articles
            ]
        
        # 收集优化机会
        analysis["optimization_opportunities"] = [
            "定期回顾高质量内容，提取可复用的模板",
            "对相似内容进行去重或整合",
            "针对低评分内容进行改写或重新发布",
            "分析热门主题，补充相关内容"
        ]
        
        logger.info(f"✅ 分析完成")
        return analysis
    
    def export_report(self, account_name: str = None, export_path: str = "workflow_report.json") -> str:
        """
        导出工作流执行报告
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "library_statistics": self.library.get_statistics(account_name),
            "library_analysis": self.analyze_and_optimize_library(account_name),
            "account_name": account_name
        }
        
        export_full_path = self.base_dir / export_path
        with open(export_full_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 报告已导出: {export_full_path}")
        return str(export_full_path)


def main():
    """主程序演示"""
    import argparse
    
    parser = argparse.ArgumentParser(description="内容库工作流集成")
    parser.add_argument("--account", default="Account_A_CrossBorder", help="账户名称")
    parser.add_argument("--action", default="generate", help="动作: generate/publish/batch/analyze")
    parser.add_argument("--topic", help="主题")
    parser.add_argument("--count", type=int, default=3, help="批量处理数量")
    
    args = parser.parse_args()
    
    integrator = ContentWorkflowIntegrator()
    
    if args.action == "generate":
        result = integrator.generate_with_library_support(
            account_name=args.account,
            topic=args.topic or "AI效率提升"
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "batch":
        result = integrator.batch_process_for_publishing(
            account_name=args.account,
            topic=args.topic,
            count=args.count
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "analyze":
        result = integrator.analyze_and_optimize_library(args.account)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "publish":
        if not args.topic or not args.topic.isdigit():
            print("❌ 请指定文章ID (--topic 用作 article_id)")
            return
        
        result = integrator.publish_with_content_check(
            article_id=int(args.topic),
            account_name=args.account
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
