#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容库管理系统 - 快速使用指南
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from content_library import ContentLibrary
from content_recommender import ContentRecommendationEngine, ContentOptimizer
from content_rewriter import ContentRewriter
from content_workflow import ContentWorkflowIntegrator


def example_1_basic_library():
    """示例1: 基础内容库操作"""
    print("\n" + "="*60)
    print("示例1: 基础内容库操作")
    print("="*60)
    
    library = ContentLibrary()
    
    # 添加文章
    article_id = library.add_article(
        title="AI效率提升的10个技巧",
        content="""
        1. 使用ChatGPT进行快速信息总结
        AI可以帮助我们快速处理大量信息。通过精心设计提示词，
        我们可以让AI按照我们的需求生成内容。
        
        2. 自动化日常任务
        很多重复的工作都可以通过AI来自动化处理，
        这样可以释放更多时间做更有价值的工作。
        """,
        account_name="Account_A_CrossBorder",
        category="技术",
        tags=["AI", "效率", "ChatGPT"],
        source="generated"
    )
    
    print(f"✅ 文章已添加, ID: {article_id}")
    
    # 搜索文章
    articles = library.search_articles(
        account_name="Account_A_CrossBorder",
        tags=["AI"],
        limit=5
    )
    
    print(f"✅ 找到 {len(articles)} 篇相关文章")
    for article in articles:
        print(f"  - {article['title']} (ID: {article['id']}, 评分: {article['rating']})")


def example_2_recommendation():
    """示例2: 内容推荐"""
    print("\n" + "="*60)
    print("示例2: 内容推荐")
    print("="*60)
    
    library = ContentLibrary()
    recommender = ContentRecommendationEngine(library)
    
    # 为账户推荐可复用内容
    recommendations = recommender.recommend_for_reuse(
        account_name="Account_A_CrossBorder",
        topic="AI效率",
        limit=5
    )
    
    print(f"✅ 推荐了 {len(recommendations)} 篇可复用内容:")
    for rec in recommendations:
        print(f"  - {rec['title']}")
    
    # 推荐模板
    templates = recommender.recommend_templates("Account_A_CrossBorder")
    print(f"\n✅ 推荐了 {len(templates)} 个模板")
    for template in templates:
        print(f"  - {template['name']} (使用{template['usage_count']}次)")


def example_3_content_optimization():
    """示例3: 内容优化建议"""
    print("\n" + "="*60)
    print("示例3: 内容优化建议")
    print("="*60)
    
    library = ContentLibrary()
    optimizer = ContentOptimizer()
    
    # 获取一篇文章并分析
    articles = library.search_articles(
        account_name="Account_A_CrossBorder",
        limit=1
    )
    
    if articles:
        article = articles[0]
        print(f"分析文章: {article['title']}")
        
        suggestions = optimizer.suggest_improvements(article['id'])
        print(f"\n✅ 生成了 {len(suggestions.get('suggestions', []))} 条改进建议:")
        
        for suggestion in suggestions.get('suggestions', []):
            print(f"  - [{suggestion['type']}] {suggestion['issue']}")
            print(f"    建议: {suggestion['suggestion']}")


def example_4_content_rewriting():
    """示例4: 内容改写"""
    print("\n" + "="*60)
    print("示例4: 内容改写和优化")
    print("="*60)
    
    rewriter = ContentRewriter()
    
    original_content = """
    使用AI可以大幅提高工作效率。通过自动化日常任务，
    我们可以将更多时间用于创意工作。AI工具如ChatGPT
    已经被广泛应用于各个领域。
    """
    
    print("原始内容:")
    print(original_content)
    
    # 提取关键点
    print("\n🔍 提取关键点...")
    key_points = rewriter.extract_key_points(original_content, max_points=3)
    if key_points:
        print("关键点:")
        for i, point in enumerate(key_points, 1):
            print(f"  {i}. {point}")
    
    # 优化标题
    print("\n📝 优化标题...")
    optimized_title = rewriter.optimize_title("AI效率提升", for_platform="wechat")
    if optimized_title:
        print(f"优化后的标题: {optimized_title}")


def example_5_workflow_integration():
    """示例5: 完整工作流集成"""
    print("\n" + "="*60)
    print("示例5: 完整工作流集成")
    print("="*60)
    
    integrator = ContentWorkflowIntegrator()
    
    # 生成内容并自动入库
    print("生成并入库内容...")
    result = integrator.generate_with_library_support(
        account_name="Account_A_CrossBorder",
        topic="AI时代的变现机会",
        use_template=True,
        use_similar=True
    )
    
    print(f"✅ 内容已生成 (ID: {result.get('article_id')})")
    print(f"   找到 {len(result.get('templates', []))} 个可用模板")
    print(f"   找到 {len(result.get('similar_articles', []))} 篇相似文章")
    
    # 发布前检查
    if result.get('article_id'):
        print("\n检查发布前的内容...")
        check = integrator.publish_with_content_check(
            article_id=result['article_id'],
            account_name="Account_A_CrossBorder"
        )
        
        print(f"检查状态: {check['status']}")
        if check['warnings']:
            print("⚠️ 警告:")
            for warning in check['warnings']:
                print(f"  - {warning}")


def example_6_batch_processing():
    """示例6: 批量处理"""
    print("\n" + "="*60)
    print("示例6: 批量生成和处理内容")
    print("="*60)
    
    integrator = ContentWorkflowIntegrator()
    
    # 批量生成内容
    print("批量生成3篇内容...")
    result = integrator.batch_process_for_publishing(
        account_name="Account_A_CrossBorder",
        topic="AI副业赚钱",
        count=3
    )
    
    print(f"✅ 批处理完成")
    print(f"   总数: {result['processed']}")
    print(f"   成功: {result['success']}")
    print(f"   库统计:")
    stats = result['statistics']
    print(f"     - 总文章数: {stats['total_articles']}")
    print(f"     - 总浏览: {stats['total_views']}")
    print(f"     - 平均评分: {stats['avg_rating']}")


def example_7_library_analysis():
    """示例7: 库分析"""
    print("\n" + "="*60)
    print("示例7: 内容库分析")
    print("="*60)
    
    library = ContentLibrary()
    
    # 全局统计
    print("📊 全局统计:")
    stats = library.get_statistics()
    print(f"  - 总文章数: {stats['total_articles']}")
    print(f"  - 总模板数: {stats['total_templates']}")
    print(f"  - 总段落数: {stats['total_paragraphs']}")
    print(f"  - 平均评分: {stats['avg_rating']}")
    
    # 账户统计
    print("\n📊 账户统计 (Account_A_CrossBorder):")
    account_stats = library.get_statistics("Account_A_CrossBorder")
    print(f"  - 文章数: {account_stats['total_articles']}")
    print(f"  - 浏览数: {account_stats['total_views']}")
    print(f"  - 点赞数: {account_stats['total_likes']}")


def example_8_export():
    """示例8: 导出内容库"""
    print("\n" + "="*60)
    print("示例8: 导出内容库")
    print("="*60)
    
    library = ContentLibrary()
    
    # 导出为JSON
    export_path = library.export_library("content_library_backup.json")
    print(f"✅ 内容库已导出到: {export_path}")
    
    integrator = ContentWorkflowIntegrator()
    report_path = integrator.export_report(
        account_name="Account_A_CrossBorder",
        export_path="workflow_analysis.json"
    )
    print(f"✅ 分析报告已导出到: {report_path}")


def show_menu():
    """显示菜单"""
    print("\n" + "="*60)
    print("内容库管理系统 - 示例程序")
    print("="*60)
    print("\n请选择要运行的示例:")
    print("1. 基础内容库操作")
    print("2. 内容推荐")
    print("3. 内容优化建议")
    print("4. 内容改写和优化")
    print("5. 完整工作流集成")
    print("6. 批量处理")
    print("7. 库分析和统计")
    print("8. 导出内容库")
    print("9. 运行所有示例")
    print("0. 退出")
    print("="*60)


if __name__ == "__main__":
    while True:
        show_menu()
        choice = input("\n请输入选择 (0-9): ").strip()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            example_1_basic_library()
        elif choice == "2":
            example_2_recommendation()
        elif choice == "3":
            example_3_content_optimization()
        elif choice == "4":
            example_4_content_rewriting()
        elif choice == "5":
            example_5_workflow_integration()
        elif choice == "6":
            example_6_batch_processing()
        elif choice == "7":
            example_7_library_analysis()
        elif choice == "8":
            example_8_export()
        elif choice == "9":
            example_1_basic_library()
            example_2_recommendation()
            example_3_content_optimization()
            example_4_content_rewriting()
            example_5_workflow_integration()
            example_6_batch_processing()
            example_7_library_analysis()
            example_8_export()
        else:
            print("❌ 无效的选择，请重试")
