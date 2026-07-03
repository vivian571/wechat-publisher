# 🚀 内容库功能 - 快速启动指南

## 📦 新增文件说明

本次为您的 My_Wechat_Matrix 项目添加了完整的**内容库管理系统**，共4个核心模块 + 3个辅助工具：

### 核心模块

| 文件 | 功能 | 主要特性 |
|------|------|--------|
| `content_library.py` | 内容存储管理 | SQLite数据库、去重、相似度检测、模板提取 |
| `content_recommender.py` | 推荐和优化 | 智能推荐、空缺分析、改进建议 |
| `content_rewriter.py` | AI改写 | 扩展、缩减、风格转换、标题优化、变体生成 |
| `content_workflow.py` | 工作流集成 | 发布前检查、批量处理、库分析 |

### 辅助工具

| 文件 | 用途 |
|------|------|
| `auto_workflow_integration.py` | 自动化工作流集成脚本 |
| `content_library_examples.py` | 交互式示例程序 |
| `CONTENT_LIBRARY_GUIDE.md` | 完整使用文档 |

---

## ⚡ 快速开始（5分钟）

### 1️⃣ 安装依赖
```bash
cd My_Wechat_Matrix
pip install schedule zhipuai  # 已在 requirements.txt 中添加
```

### 2️⃣ 运行示例
```bash
# 选择交互式示例程序
python content_library_examples.py

# 或直接生成内容
python content_workflow.py --account Account_A_CrossBorder --action generate --topic "AI效率提升"
```

### 3️⃣ 主要操作

#### 生成内容并自动入库
```bash
# 单个生成
python content_workflow.py \
  --account Account_A_CrossBorder \
  --action generate \
  --topic "热门话题"

# 批量生成
python content_workflow.py \
  --account Account_A_CrossBorder \
  --action batch \
  --count 5
```

#### 分析内容库
```bash
python content_workflow.py \
  --account Account_A_CrossBorder \
  --action analyze
```

#### 自动化工作流
```bash
# 生成+检查+优化建议
python auto_workflow_integration.py --action generate --account Account_A_CrossBorder

# 分析所有账户
python auto_workflow_integration.py --action analyze

# 生成综合报告
python auto_workflow_integration.py --action report
```

---

## 🎯 核心功能演示

### 功能1: 内容自动入库去重
```python
from content_library import ContentLibrary

library = ContentLibrary()

# 添加文章时自动去重和哈希检测
article_id = library.add_article(
    title="我的文章",
    content="内容...",
    account_name="Account_A_CrossBorder"
)
# ✅ 如果内容重复，自动警告
```

### 功能2: 智能推荐
```python
from content_recommender import ContentRecommendationEngine

recommender = ContentRecommendationEngine()

# 推荐高质量的可复用内容
recommendations = recommender.recommend_for_reuse(
    account_name="Account_A_CrossBorder",
    topic="AI",
    limit=10
)
# 返回评分高、相关性强的内容

# 查找相似文章用于改写
similar = recommender.find_similar_for_adaptation(
    article_id=1,
    min_similarity=0.6
)
```

### 功能3: AI改写和优化
```python
from content_rewriter import ContentRewriter

rewriter = ContentRewriter()

# 扩展内容
expanded = rewriter.expand_content(
    content="原文...",
    target_length=2000
)

# 生成变体（A/B测试）
variations = rewriter.generate_variations(
    content="原文...",
    num_variations=3
)

# 优化标题
title = rewriter.optimize_title("原标题", for_platform="wechat")
```

### 功能4: 发布前自动检查
```python
from content_workflow import ContentWorkflowIntegrator

integrator = ContentWorkflowIntegrator()

# 发布前自动检查
check = integrator.publish_with_content_check(
    article_id=1,
    account_name="Account_A_CrossBorder"
)

# 返回检查结果
# {
#   "can_publish": True/False,
#   "warnings": [...],
#   "recommendations": [...]
# }
```

### 功能5: 完整工作流
```python
# 一行代码，自动完成：生成→入库→推荐→检查→建议
result = integrator.generate_with_library_support(
    account_name="Account_A_CrossBorder",
    topic="热门主题",
    use_template=True,
    use_similar=True
)

# 返回：生成的内容 + 推荐内容 + 相似文章 + 优化建议
```

---

## 📊 数据库结构

系统自动创建 `content_library.db` SQLite数据库，包含：

- **articles** - 文章表（含哈希、评分、状态）
- **paragraphs** - 段落表（用于细粒度复用）
- **templates** - 模板表（提取优质内容作为模板）
- **similarity_cache** - 相似度缓存（提高查询速度）

自动创建索引优化查询效率。

---

## 🔄 与现有系统集成

### 与 generator.py 集成
```python
# 生成内容时自动获得推荐
from content_workflow import ContentWorkflowIntegrator

integrator = ContentWorkflowIntegrator()
result = integrator.generate_with_library_support(
    account_name="Account_A_CrossBorder",
    topic=user_topic
)

# 获得：推荐模板、相似文章、优化建议
templates = result['templates']
similar = result['similar_articles']
suggestions = result['optimization_suggestions']
```

### 与 auto_scheduler.py 集成
```python
# 定时任务中使用内容库
from auto_workflow_integration import EnhancedAutoPublisher

publisher = EnhancedAutoPublisher()

# 智能生成+检查+优化建议
result = publisher.smart_generate_and_publish(
    account_name="Account_A_CrossBorder",
    count=3
)

# 自动记录到日报
# 生成：daily_reports/report_*.json
```

---

## 📈 最佳实践

### 1. 定期备份
```bash
# 每周备份内容库
python -c "
from content_library import ContentLibrary
library = ContentLibrary()
library.export_library('backup_$(date +%Y%m%d).json')
"
```

### 2. 追踪效果
```python
# 发布后更新评分
library.update_article_rating(
    article_id=1,
    views=1000,
    likes=100,
    shares=50,
    comments=20
)
# 自动计算综合评分
```

### 3. 定期分析
```bash
# 每月分析一次
python auto_workflow_integration.py --action report
```

### 4. 提取成功模板
```python
# 高评分文章转化为模板
high_quality = library.get_high_quality_articles("Account_A_CrossBorder")
for article in high_quality:
    library.extract_template(
        article_id=article['id'],
        template_name=f"成功模板_{article['id']}"
    )
```

---

## 📝 常用命令

```bash
# 生成单篇内容
python content_workflow.py --account Account_A_CrossBorder --action generate

# 批量生成5篇
python content_workflow.py --account Account_A_CrossBorder --action batch --count 5

# 分析账户
python content_workflow.py --account Account_A_CrossBorder --action analyze

# 发布前检查
python content_workflow.py --account Account_A_CrossBorder --action publish --topic 1

# 智能发布流程
python auto_workflow_integration.py --action generate --account Account_A_CrossBorder

# 所有账户分析
python auto_workflow_integration.py --action analyze

# 生成综合报告
python auto_workflow_integration.py --action report

# 配置每日定时任务
python auto_workflow_integration.py --action daily --time 08:00
```

---

## 🎓 详细文档

完整的API文档和高级用法请查看：
- 📖 [CONTENT_LIBRARY_GUIDE.md](CONTENT_LIBRARY_GUIDE.md) - 完整使用指南
- 💡 [content_library_examples.py](content_library_examples.py) - 8个完整示例

运行示例程序：
```bash
python content_library_examples.py
# 交互式菜单，选择要运行的示例
```

---

## 🔧 配置说明

系统使用 `matrix_config.json` 中的配置：

```json
{
    "ai_provider": "zhipu",  // 选择AI服务商
    "api_config": {
        "zhipu": {
            "api_key": "...",
            "model": "glm-4-flash"
        }
    }
}
```

支持的AI服务：OpenAI、Google Gemini、智谱清言

---

## 🐛 故障排查

### 问题：数据库被锁
**解决：** 关闭其他访问该数据库的进程，或重启Python程序

### 问题：AI调用失败
**解决：** 检查 `matrix_config.json` 中的API密钥和网络连接

### 问题：相似度计算慢
**解决：** 使用缓存表，或增加相似度阈值

查看详细文档中的[故障排查章节](CONTENT_LIBRARY_GUIDE.md#-故障排查)

---

## 💡 创意用途

这个内容库系统支持：

✅ **内容复用** - 识别可复用的段落和模板
✅ **质量控制** - 发布前自动检查和建议
✅ **去重管理** - 避免发布重复内容
✅ **效果追踪** - 建立内容评分系统
✅ **批量处理** - 3篇内容一键生成→检查→优化
✅ **定时发布** - 每日自动化工作流
✅ **数据分析** - 内容覆盖率、空缺分析、热门话题

---

## 🚀 下一步

### 立即体验
```bash
python content_library_examples.py
# 选择示例1：基础操作，查看效果
```

### 集成到项目
1. 修改 `generator.py`，调用 `content_workflow.generate_with_library_support()`
2. 修改 `auto_scheduler.py`，使用 `EnhancedAutoPublisher` 替代原有发布逻辑
3. 配置定时任务：`auto_workflow_integration.py --action daily`

### 监控和优化
```bash
# 每周运行分析
python auto_workflow_integration.py --action analyze | tee analysis_$(date +%Y%m%d).txt
```

---

## 📞 支持

有任何问题，请：
1. 查看 [CONTENT_LIBRARY_GUIDE.md](CONTENT_LIBRARY_GUIDE.md) 的详细文档
2. 运行 `content_library_examples.py` 查看具体用法
3. 查看各模块的源代码注释

---

**系统已准备就绪！🎉 开始使用内容库吧！**

```bash
# 一键启动
python content_library_examples.py
```
