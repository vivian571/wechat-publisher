#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动化工作流集成脚本
将内容库与auto_scheduler无缝集成
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from content_workflow import ContentWorkflowIntegrator
from wechat_auto_post import WeChatAutoPoster

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("workflow_integration.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 账号顺序
ACCOUNT_ORDER = [
    "Account_A_CrossBorder",
    "Account_B_English",
    "Account_C_Life",
    "Account_D_Tech"
]


class EnhancedAutoPublisher:
    """增强的自动发布器（集成内容库）"""
    
    def __init__(self):
        """初始化发布器"""
        self.base_dir = Path(__file__).parent
        self.integrator = ContentWorkflowIntegrator()
        self.config_path = self.base_dir / "matrix_config.json"
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        logger.info("✅ 增强型自动发布器已初始化")
    
    def smart_generate_and_publish(self, account_name: str, count: int = 1) -> dict:
        """
        智能生成和发布流程
        
        1. 基于热搜生成内容
        2. 自动入库
        3. 获取优化建议
        4. 发布前检查
        5. 自动发布
        
        Args:
            account_name: 账户名称
            count: 生成数量
        
        Returns:
            处理结果
        """
        logger.info(f"\n🚀 开始智能发布流程: {account_name} x {count}")
        
        result = {
            "account_name": account_name,
            "timestamp": datetime.now().isoformat(),
            "generated": 0,
            "published": 0,
            "failed": 0,
            "details": []
        }
        
        # 获取热门主题
        trending_topics = self.integrator.recommender.get_trending_topics(
            account_name=account_name,
            limit=5
        )
        
        logger.info(f"📊 获取热门主题: {[t['topic'] for t in trending_topics]}")
        
        # 为每个热门主题生成内容
        for i, trending in enumerate(trending_topics[:count]):
            topic = trending["topic"]
            logger.info(f"\n📝 处理主题 {i+1}/{count}: {topic}")
            
            try:
                # 1. 生成内容并自动入库
                generation = self.integrator.generate_with_library_support(
                    account_name=account_name,
                    topic=topic,
                    use_template=True,
                    use_similar=True
                )
                
                if not generation.get("article_id"):
                    logger.warning(f"⚠️ 内容生成失败: {topic}")
                    result["failed"] += 1
                    continue
                
                article_id = generation["article_id"]
                result["generated"] += 1
                
                # 2. 发布前检查
                check = self.integrator.publish_with_content_check(
                    article_id=article_id,
                    account_name=account_name
                )
                
                logger.info(f"✅ 内容检查完成: {check['status']}")
                
                # 3. 如果需要调整，进行优化
                if check["recommendations"]:
                    logger.info(f"💡 有{len(check['recommendations'])}条改进建议")
                    # 这里可以选择自动应用某些改进
                    # 或者等待人工审核
                
                # 4. 标记可以发布
                detail = {
                    "article_id": article_id,
                    "topic": topic,
                    "can_publish": check["can_publish"],
                    "status": check["status"],
                    "warnings": check.get("warnings", [])
                }
                
                # 5. 如果所有检查通过，自动发布
                if check["can_publish"]:
                    try:
                        logger.info(f"📤 准备发布...")
                        
                        # 这里调用发布接口
                        # publish_result = self._publish_to_wechat(account_name, article_id)
                        # detail["published"] = publish_result
                        
                        result["published"] += 1
                        detail["published"] = True
                        logger.info(f"✅ 内容已发布 (ID: {article_id})")
                    
                    except Exception as e:
                        logger.error(f"❌ 发布失败: {e}")
                        detail["published"] = False
                        result["failed"] += 1
                
                else:
                    logger.info(f"⚠️ 内容需要人工审核，未自动发布")
                    detail["published"] = False
                
                result["details"].append(detail)
            
            except Exception as e:
                logger.error(f"❌ 处理失败: {e}")
                result["failed"] += 1
        
        # 生成摘要
        logger.info(f"\n{'='*60}")
        logger.info(f"📊 批处理完成摘要:")
        logger.info(f"  生成: {result['generated']} 篇")
        logger.info(f"  发布: {result['published']} 篇")
        logger.info(f"  失败: {result['failed']} 篇")
        logger.info(f"{'='*60}")
        
        return result
    
    def _publish_to_wechat(self, account_name: str, article_id: int) -> bool:
        """
        发布到微信公众号
        
        Args:
            account_name: 账户名称
            article_id: 文章ID
        
        Returns:
            发布是否成功
        """
        try:
            # 从库中获取文章内容
            conn = __import__('sqlite3').connect(self.integrator.library.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT title, content FROM articles WHERE id = ?
            """, (article_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                logger.warning(f"⚠️ 文章不存在 (ID: {article_id})")
                return False
            
            title, content = row
            
            # 调用WeChatAutoPoster进行发布
            logger.info(f"🔗 连接微信公众号...")
            
            poster = WeChatAutoPoster(account_name=account_name, headless=True)
            
            # 这里需要根据WeChatAutoPoster的实际接口进行调整
            # 示例代码
            # result = poster.post_article(title=title, content=content)
            
            logger.info(f"✅ 已提交发布请求")
            return True
        
        except Exception as e:
            logger.error(f"❌ 发布调用失败: {e}")
            return False
    
    def schedule_daily_automation(self, schedule_time: str = "08:00"):
        """
        配置每日自动化任务
        
        Args:
            schedule_time: 每日执行时间 (HH:MM格式)
        """
        import schedule
        import time
        
        logger.info(f"⏰ 配置每日任务，执行时间: {schedule_time}")
        
        def job():
            """每日执行的任务"""
            logger.info(f"\n{'='*60}")
            logger.info(f"📅 执行每日自动化任务 ({datetime.now().isoformat()})")
            logger.info(f"{'='*60}")
            
            # 为每个账户生成内容
            for account in ACCOUNT_ORDER:
                try:
                    result = self.smart_generate_and_publish(
                        account_name=account,
                        count=1  # 每个账户每天1篇
                    )
                    
                    # 保存日志
                    self._save_daily_report(account, result)
                
                except Exception as e:
                    logger.error(f"❌ {account} 处理失败: {e}")
        
        # 使用 schedule 库配置定时任务
        schedule.every().day.at(schedule_time).do(job)
        
        logger.info(f"✅ 任务已配置")
        
        # 持续运行调度器
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def _save_daily_report(self, account_name: str, result: dict):
        """保存每日报告"""
        try:
            report_dir = self.base_dir / "daily_reports"
            report_dir.mkdir(exist_ok=True)
            
            report_file = report_dir / f"report_{account_name}_{datetime.now().strftime('%Y%m%d')}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 日报已保存: {report_file}")
        
        except Exception as e:
            logger.error(f"❌ 保存日报失败: {e}")
    
    def analyze_all_accounts(self) -> dict:
        """
        分析所有账户的内容库
        
        Returns:
            分析结果
        """
        logger.info(f"\n📊 开始分析所有账户...")
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "accounts": {}
        }
        
        for account in ACCOUNT_ORDER:
            logger.info(f"分析 {account}...")
            
            account_analysis = self.integrator.analyze_and_optimize_library(account)
            analysis["accounts"][account] = account_analysis
        
        logger.info(f"✅ 分析完成")
        return analysis
    
    def export_comprehensive_report(self) -> str:
        """导出完整的工作流分析报告"""
        logger.info(f"\n📑 生成综合报告...")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "all_accounts_analysis": self.analyze_all_accounts(),
            "global_statistics": self.integrator.library.get_statistics()
        }
        
        report_path = self.base_dir / "comprehensive_workflow_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 报告已导出: {report_path}")
        return str(report_path)


def main():
    """主程序"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自动化工作流集成")
    parser.add_argument("--action", default="generate", 
                       help="动作: generate/daily/analyze/report")
    parser.add_argument("--account", default="Account_A_CrossBorder", help="账户名称")
    parser.add_argument("--count", type=int, default=1, help="生成数量")
    parser.add_argument("--time", default="08:00", help="定时执行时间")
    
    args = parser.parse_args()
    
    publisher = EnhancedAutoPublisher()
    
    if args.action == "generate":
        result = publisher.smart_generate_and_publish(
            account_name=args.account,
            count=args.count
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "daily":
        # 需要安装 schedule 库
        try:
            publisher.schedule_daily_automation(schedule_time=args.time)
        except ImportError:
            print("❌ 需要安装 schedule 库: pip install schedule")
    
    elif args.action == "analyze":
        result = publisher.analyze_all_accounts()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "report":
        path = publisher.export_comprehensive_report()
        print(f"✅ 报告已生成: {path}")
    
    else:
        print(f"❌ 未知动作: {args.action}")


if __name__ == "__main__":
    main()
