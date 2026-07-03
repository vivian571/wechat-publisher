# 📚 内容库管理系统 - 完整使用指南

## 🎯 系统概述

内容库管理系统是 My_Wechat_Matrix 的核心扩展，提供了：

- **内容存储与检索** - SQLite数据库，支持高效搜索和过滤
- **内容推荐引擎** - 基于账户、主题、评分的智能推荐
- **内容改写优化** - AI驱动的扩展、缩减、改写功能
- **工作流集成** - 与现有generator、auto_scheduler无缝集成
- **质量控制** - 发布前自动检查和优化建议

---

## 📦 核心模块

### 1. `content_library.py` - 内容库管理器

**主要功能：**
- 内容的CRUD操作
- 去重和相似度检测
- 模板提取和管理
- 统计和分析

**主要类：**
- `ContentLibrary` - 内容库核心类

**关键方法：**

```python
# 添加文章
article_id = library.add_article(
    title="AI效率提升",
    content="...",
    account_name="Account_A_CrossBorder",
    category="技术",
    tags=["AI", "效率"]
)

# 搜索文章
articles = library.search_articles(
    account_name="Account_A_CrossBorder",
    category="技术",
    min_rating=3.0,
    limit=10
)

# 获取相似文章
similar = library.get_similar_articles(
    article_id=1,
    threshold=0.7,
    limit=5
)

# 更新评分
library.update_article_rating(
    article_id=1,
    views=100,
    likes=20,
    shares=5,
    comments=10
)

# 提取模板
template_id = library.extract_template(
    article_id=1,
    template_name="AI技巧模板"
)

# 获取统计
stats = library.get_statistics("Account_A_CrossBorder")

# 导出库
export_path = library.export_library("backup.json")
```

---

### 2. `content_recommender.py` - 推荐和优化引擎

**主要功能：**
- 智能内容推荐
- 模板推荐
- 内容空缺分析
- 改进建议生成

**主要类：**
- `ContentRecommendationEngine` - 推荐引擎
- `ContentOptimizer` - 优化器

**关键方法：**

```python
recommender = ContentRecommendationEngine()

# 推荐可复用内容
recommendations = recommender.recommend_for_reuse(
    account_name="Account_A_CrossBorder",
    topic="AI效率",
    limit=10
)

# 推荐模板
templates = recommender.recommend_templates(
    account_name="Account_A_CrossBorder"
)

# 查找相似文章用于改写
similar = recommender.find_similar_for_adaptation(
    article_id=1,
    min_similarity=0.6
)

# 获取热门主题趋势
trending = recommender.get_trending_topics(
    account_name="Account_A_CrossBorder",
    days=7,
    limit=10
)

# 分析内容空缺
gap = recommender.analyze_content_gap(
    account_name="Account_A_CrossBorder"
)

# 获取优化建议
optimizer = ContentOptimizer()
suggestions = optimizer.suggest_improvements(article_id=1)

# 批量优化
results = optimizer.batch_optimize_content(
    account_name="Account_A_CrossBorder",
    max_items=10
)
```

---

### 3. `content_rewriter.py` - AI内容改写器

**主要功能：**
- 内容扩展
- 内容缩减
- 风格转换
- 关键点提取
- 标题优化
- 变体生成

**主要类：**
- `ContentRewriter` - 改写器

**关键方法：**

```python
rewriter = ContentRewriter()

# 扩展内容
expanded = rewriter.expand_content(
    content="原始内容",
    target_length=2000,
    style="技术性"
)

# 缩减内容
shrunk = rewriter.shrink_content(
    content="原始内容",
    target_length=500
)

# 转换风格
converted = rewriter.rewrite_for_style(
    content="原始内容",
    source_style="technical",
    target_style="casual"
)

# 生成变体（用于A/B测试）
variations = rewriter.generate_variations(
    content="原始内容",
    num_variations=3
)

# 提取关键点
key_points = rewriter.extract_key_points(
    content="原始内容",
    max_points=5
)

# 优化标题
optimized_title = rewriter.optimize_title(
    title="原始标题",
    for_platform="wechat"
)
```

---

### 4. `content_workflow.py` - 工作流集成器

**主要功能：**
- 集成所有模块
- 发布前自动检查
- 批量处理
- 库分析报告

**主要类：**
- `ContentWorkflowIntegrator` - 工作流集成器

**关键方法：**

```python
integrator = ContentWorkflowIntegrator()

# 生成内容并自动入库
result = integrator.generate_with_library_support(
    account_name="Account_A_CrossBorder",
    topic="AI效率提升",
    use_template=True,
    use_similar=True
)

# 发布前内容检查
check = integrator.publish_with_content_check(
    article_id=1,
    account_name="Account_A_CrossBorder"
)

# 批量处理
batch = integrator.batch_process_for_publishing(
    account_name="Account_A_CrossBorder",
    topic="AI副业赚钱",
    count=3
)

# 库分析
analysis = integrator.analyze_and_optimize_library(
    account_name="Account_A_CrossBorder"
)

# 导出报告
report_path = integrator.export_report(
    account_name="Account_A_CrossBorder"
)
```

---

## 🚀 快速开始

### 安装依赖

```bash
cd My_Wechat_Matrix
pip install -r requirements.txt
```

### 运行示例

```bash
# 运行交互式示例程序
python content_library_examples.py

# 或者直接使用工作流
python content_workflow.py --account Account_A_CrossBorder --action batch --count 5
```

### 常见用法

#### 1. 为内容自动入库

```python
from content_library import ContentLibrary

library = ContentLibrary()
article_id = library.add_article(
    title="我的新文章",
    content="文章内容...",
    account_name="Account_A_CrossBorder",
    tags=["标签1", "标签2"]
)
```

#### 2. 搜索和推荐内容

```python
from content_recommender import ContentRecommendationEngine

recommender = ContentRecommendationEngine()

# 获取推荐
recs = recommender.recommend_for_reuse(
    account_name="Account_A_CrossBorder",
    topic="AI"
)

# 获取相似文章用于改写
similar = recommender.find_similar_for_adaptation(article_id=1)
```

#### 3. 改写和优化内容

```python
from content_rewriter import ContentRewriter

rewriter = ContentRewriter()

# 扩展文章
expanded = rewriter.expand_content(
    content="原文...",
    target_length=2000
)

# 提取关键点
key_points = rewriter.extract_key_points(content="原文...")

# 优化标题
title = rewriter.optimize_title("原标题")
```

#### 4. 完整工作流

```python
from content_workflow import ContentWorkflowIntegrator

integrator = ContentWorkflowIntegrator()

# 生成 → 检查 → 推荐改进
result = integrator.generate_with_library_support(
    account_name="Account_A_CrossBorder",
    topic="热门主题"
)

# 发布前检查
check = integrator.publish_with_content_check(
    article_id=result['article_id'],
    account_name="Account_A_CrossBorder"
)

# 打印检查结果
print(f"可以发布: {check['can_publish']}")
print(f"建议: {check['recommendations']}")
```

---

## 📊 数据库设计

### 表结构

**articles** - 文章表
```
id: 主键
article_hash: 内容哈希（用于去重）
title: 标题
content: 内容
account_name: 账户名称
category: 分类
tags: 标签（逗号分隔）
source: 来源（generated/manual/imported）
created_at: 创建时间
published_at: 发布时间
views: 浏览数
likes: 点赞数
shares: 分享数
comments: 评论数
rating: 综合评分
status: 状态（draft/published）
```

**paragraphs** - 段落表（用于段落级复用）
```
id: 主键
paragraph_hash: 段落哈希
article_id: 所属文章ID
paragraph_content: 段落内容
paragraph_type: 段落类型
account_name: 账户名称
created_at: 创建时间
usage_count: 使用次数
reuse_times: 复用次数
rating: 评分
```

**templates** - 模板表
```
id: 主键
template_name: 模板名称
template_content: 模板内容
category: 分类
for_accounts: 适用账户
created_at: 创建时间
usage_count: 使用次数
rating: 评分
description: 描述
```

**similarity_cache** - 相似度缓存表
```
id: 主键
article_id1: 文章1
article_id2: 文章2
similarity: 相似度
cached_at: 缓存时间
```

---

## 🔄 工作流集成

### 与 generator.py 的集成

```python
# 生成内容时自动入库
from content_workflow import ContentWorkflowIntegrator

integrator = ContentWorkflowIntegrator()
result = integrator.generate_with_library_support(
    account_name="Account_A_CrossBorder",
    topic="用户输入的主题"
)

# 自动获得推荐内容、模板、优化建议
print(result['recommendations'])
print(result['templates'])
print(result['optimization_suggestions'])
```

### 与 auto_scheduler.py 的集成

```python
# 定时任务中使用内容库
from content_workflow import ContentWorkflowIntegrator

integrator = ContentWorkflowIntegrator()

# 每天批量生成和发布
batch_result = integrator.batch_process_for_publishing(
    account_name="Account_A_CrossBorder",
    count=3
)

# 发布前检查
for article in batch_result['articles']:
    if article['can_publish']:
        # 调用发布接口
        publish_article(article['article_id'])
```

---

## 📈 最佳实践

### 1. 定期导出备份
```python
# 每周备份一次
library.export_library(f"backup_{datetime.now().strftime('%Y%m%d')}.json")
```

### 2. 追踪内容效果
```python
# 获取文章发布后的数据并更新评分
library.update_article_rating(
    article_id=article_id,
    views=view_count,
    likes=like_count,
    shares=share_count,
    comments=comment_count
)
```

### 3. 定期分析和优化
```python
# 每月生成分析报告
analysis = integrator.analyze_and_optimize_library("Account_A_CrossBorder")
integrator.export_report("Account_A_CrossBorder")
```

### 4. 提取成功模板
```python
# 高评分文章转化为模板
high_quality = library.get_high_quality_articles("Account_A_CrossBorder")
for article in high_quality:
    library.extract_template(
        article_id=article['id'],
        template_name=f"模板_{article['id']}"
    )
```

### 5. 利用相似度检测避免重复
```python
# 发布前检查相似度
similar = library.get_similar_articles(article_id, threshold=0.8)
if similar:
    print(f"发现{len(similar)}篇高度相似的文章，建议审核")
```

---

## 🛠️ 故障排查

### 问题1: 数据库文件过大

**解决方案:**
```python
# 定期清理和优化数据库
import sqlite3
conn = sqlite3.connect('content_library.db')
cursor = conn.cursor()
cursor.execute('VACUUM')
conn.close()
```

### 问题2: 相似度计算速度慢

**解决方案:**
- 使用缓存表存储已计算的相似度
- 只对新增文章计算相似度
- 增加相似度阈值

### 问题3: AI调用失败

**解决方案:**
```python
# 检查API配置
rewriter = ContentRewriter()
if rewriter.ai_client is None:
    print("❌ AI客户端不可用，请检查配置")
```

---

## 📝 常见问题

**Q: 内容库会自动清理重复内容吗？**
A: 不会自动清理，但系统会检测重复并给出警告。您可以定期使用 `analyze_and_optimize_library()` 来识别重复内容。

**Q: 评分是如何计算的？**
A: 评分 = (点赞*2 + 分享*3 + 评论*1) / 浏览数 * 100

**Q: 可以导入外部文章吗？**
A: 可以，使用 `add_article()` 方法，设置 `source="imported"`。

**Q: 模板有大小限制吗？**
A: 没有硬性限制，但建议模板不超过3000个字符以保持性能。

---

## 📚 完整示例

参见 `content_library_examples.py` 中的8个完整示例:
1. 基础内容库操作
2. 内容推荐
3. 优化建议
4. 内容改写
5. 工作流集成
6. 批量处理
7. 库分析
8. 导出功能

运行: `python content_library_examples.py`

---

## 🎓 更新日志

### v1.0.0 (2024-01-29)
- ✅ 内容库核心功能
- ✅ 推荐引擎
- ✅ AI改写器
- ✅ 工作流集成
- ✅ 文档和示例

---

## 📞 支持

如有问题，请查看代码中的详细注释或运行示例程序了解具体用法。

---

**Happy content management! 🚀**
