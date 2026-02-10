# 国际平台文章自动发布系统指南

## 系统概述

本系统实现了技术文章到国际平台的自动发布功能，支持：
- 文章到视频的自动转换
- 多平台同步发布（TikTok、YouTube、Instagram）
- 文件监控和自动触发
- 智能去重和重试机制

## 主要功能

### 🎯 核心功能
- **自动文章转换**: 将Markdown文章转换为视频格式
- **国际平台发布**: 支持TikTok、YouTube、Instagram等平台
- **智能监控**: 实时监控文章更新，自动触发发布
- **多语言支持**: 自动生成适合国际观众的标题和描述

### 🔧 技术特点
- 基于Python的异步处理架构
- 使用OpenCV和PIL进行视频生成
- 支持Playwright浏览器自动化
- 智能错误处理和重试机制

## 快速开始

### 1. 基本命令

```bash
# 查看系统状态
./international_manager.sh status

# 立即发布所有新文章
./international_manager.sh publish

# 启动自动监控服务
./international_manager.sh start

# 停止监控服务
./international_manager.sh stop

# 查看运行日志
./international_manager.sh logs

# 系统配置信息
./international_manager.sh config
```

### 2. 启动自动监控

```bash
# 启动默认监控（每10分钟检查一次）
./international_manager.sh start

# 自定义检查间隔（每5分钟）
./international_manager.sh start --interval 300
```

### 3. 测试系统

```bash
# 运行完整测试流程
./international_manager.sh test
```

## 系统配置

### 平台配置

系统支持以下国际平台：

| 平台 | 状态 | 描述 |
|------|------|------|
| TikTok | ✅ 启用 | 短视频平台，适合技术快讯 |
| YouTube | ✅ 启用 | 长视频平台，适合深度内容 |
| Instagram | ✅ 启用 | 视觉内容平台，适合技术展示 |

### 监控配置

- **检查间隔**: 默认600秒（10分钟）
- **重试次数**: 最大3次
- **重试延迟**: 60秒
- **平台延迟**: 30秒（避免触发限制）

### 文件结构

```
/Users/ax/wechat-publisher/
├── international_auto_publish.py    # 核心发布脚本
├── international_manager.sh         # 管理界面
├── international_published.log    # 发布记录
├── international_processed.log      # 处理记录
├── international_publish.log        # 运行日志
└── OmniPublish/articles/            # 文章目录
    └── 2026-02-08-*.md             # 文章文件
```

## 使用说明

### 文章格式要求

文章文件命名格式：
```
2026-02-08-article-title.md
```

文章内容格式：
```markdown
# [文章标题]

![封面图片](image-url)

文章内容...

## 小节标题

详细内容...

## 结论

总结内容...
```

### 自动标题生成

系统会根据文章内容自动生成适合国际平台的标题：

- **AI相关**: "🔥 {标题} - Must Watch for Tech Enthusiasts!"
- **编程相关**: "💻 {标题} - Essential Developer Guide"
- **性能相关**: "⚡ {标题} - Optimization Tips Inside"
- **其他**: "📈 {标题} - Latest Tech Insights"

### 自动描述生成

不同平台有不同的描述模板：

**YouTube**: 详细描述 + 订阅提醒 + 标签
**TikTok**: 简洁描述 + 热门标签
**Instagram**: 视觉导向 + 互动元素

## 高级配置

### 自定义平台配置

编辑 `international_auto_publish.py` 中的 `international_platforms` 配置：

```python
self.international_platforms = {
    'tiktok': {
        'enabled': True,
        'account': 'main',
        'description': 'Quick tech tips',
        'real_platform': 'tiktok'  # 实际使用的平台
    }
}
```

### 修改检查间隔

在启动时指定自定义间隔：
```bash
./international_manager.sh start --interval 1800  # 30分钟
```

### 添加新平台

1. 在配置中添加新平台
2. 实现对应的发布逻辑
3. 更新管理脚本

## 故障排除

### 常见问题

**Q: 文章转换失败**
- 检查文章格式是否正确
- 确认图片链接可访问
- 查看转换日志获取详细信息

**Q: 发布失败**
- 检查网络连接
- 验证平台Cookie是否有效
- 确认视频文件格式正确

**Q: 监控服务异常停止**
- 查看服务日志：`./international_manager.sh logs`
- 检查系统资源使用情况
- 重启服务：`./international_manager.sh start`

### 日志文件

- **international_publish.log**: 主要运行日志
- **international_processed.log**: 文章处理记录
- **international_published.log**: 发布成功记录
- **international_service_error.log**: 服务错误日志

### 调试模式

运行单次模式进行调试：
```bash
python3 international_auto_publish.py --mode once
```

## 性能优化

### 批量处理
- 支持多篇文章批量处理
- 平台间延迟避免触发限制
- 智能重试机制

### 资源管理
- 异步处理架构
- 内存优化
- 错误恢复机制

## 安全考虑

### 数据安全
- 本地日志存储
- 无敏感信息泄露
- 安全的文件处理

### 平台合规
- 遵守各平台使用条款
- 合理发布频率
- 内容原创性要求

## 更新和维护

### 系统更新
```bash
# 检查系统状态
./international_manager.sh status

# 清理旧日志
echo "" > international_publish.log
```

### 备份建议
- 定期备份发布记录
- 保存重要文章文件
- 备份配置文件

## 技术支持

如遇到问题，请检查：
1. 系统日志文件
2. 网络连接状态
3. 平台配置正确性
4. 文章格式规范

## 总结

本系统提供了完整的技术文章到国际平台的自动发布解决方案，支持：

✅ **自动化流程**: 文章→视频→发布全流程自动化
✅ **多平台支持**: TikTok、YouTube、Instagram等
✅ **智能监控**: 实时文件监控和自动触发
✅ **国际化**: 自动生成适合国际观众的内容
✅ **稳定性**: 完善的错误处理和重试机制

通过本系统，您可以专注于内容创作，让技术文章自动触达全球观众！