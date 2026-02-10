# 📰 文章自动发布系统指南

## 🎯 系统概述

这个系统可以自动将 `/Users/ax/wechat-publisher/OmniPublish/articles` 目录中带日期的文章转换为视频，并发布到各大社交平台。

## 🚀 快速开始

### 1. 文章转换和发布

```bash
# 转换所有文章为视频
./article_manager.sh convert

# 转换并发布到所有平台
./article_manager.sh publish

# 查看发布状态
./article_manager.sh status
```

### 2. 管理命令

```bash
# 列出所有文章
./article_manager.sh list

# 清理已发布记录（允许重新发布）
./article_manager.sh clean

# 显示帮助
./article_manager.sh help
```

## 📋 系统功能

### 文章处理流程

1. **文章解析**: 自动解析Markdown格式的文章
2. **内容提取**: 提取标题、图片、正文内容
3. **脚本生成**: 基于文章内容生成视频脚本
4. **视频创建**: 将脚本转换为幻灯片式视频
5. **自动发布**: 将生成的视频发布到各大平台

### 支持的文件格式

- **文件名格式**: `YYYY-MM-DD-文章标题.md`
- **内容格式**: Markdown格式，支持标题、图片、段落

### 生成的视频特点

- **分辨率**: 1280x720 (HD)
- **格式**: MP4
- **时长**: 每张幻灯片3秒，最多10张幻灯片
- **样式**: 黑色背景，白色文字，居中显示

## 🔧 技术实现

### 核心组件

1. **ArticleToVideoConverter**: 文章转视频转换器
2. **SimpleVideoCreator**: 简单视频创建器（使用OpenCV和PIL）
3. **ArticlePublisher**: 文章发布管理器

### 依赖库

```bash
# 安装依赖
pip3 install opencv-python pillow numpy aiohttp
```

### 文件结构

```
/Users/ax/wechat-publisher/
├── auto_publish_articles.py          # 主转换脚本
├── simple_video_creator.py           # 视频创建器
├── article_manager.sh                # 管理脚本
├── published_articles.log            # 发布记录
├── OmniPublish/articles/             # 文章源目录
└── social-auto-upload/videoFile/     # 输出视频目录
```

## 📊 使用示例

### 示例1：批量转换文章

```bash
# 查看文章状态
./article_manager.sh status

# 输出示例:
# 文章发布状态
# ==================================
# 文章目录: /Users/ax/wechat-publisher/OmniPublish/articles
# 总文章数量: 3
# 已发布文章: 0
# 待发布文章:
#   2026-02-08-ai-agents-autonomous-future.md
#   2026-02-08-cursor-ide-mcp-composer.md
#   2026-02-08-nextjs-15-performance-guide.md
```

### 示例2：转换并发布

```bash
# 执行转换和发布
./article_manager.sh publish

# 输出示例:
# 开始文章转换和发布流程...
# 开始转换文章为视频...
# 正在运行文章转换程序...
# 开始文章自动发布流程...
# 发现 3 篇新文章
# 
# 处理文章: 2026-02-08-cursor-ide-mcp-composer.md
# 文章标题: Cursor IDE: Why the "AI-First" Code Editor is Now the Industry Standard
# 已生成视频脚本
# 正在创建视频: Cursor_IDE_Why_the_AI-First_Code_Editor_is_Now_the_article_video_20260208_223638.mp4
# 视频创建成功: /Users/ax/wechat-publisher/social-auto-upload/videoFile/Cursor_IDE_Why_the_AI-First_Code_Editor_is_Now_the_article_video_20260208_223638.mp4
# ✅ 文章转换成功!
```

## ⚙️ 高级配置

### 自定义视频参数

在 `simple_video_creator.py` 中可以修改：

```python
# 视频参数
self.width = 1280          # 视频宽度
self.height = 720          # 视频高度
self.fps = 24              # 帧率
self.duration_per_slide = 3  # 每张幻灯片时长（秒）
```

### 自定义样式

可以修改文字样式和背景：

```python
def create_text_image(self, text: str, background_color=(0, 0, 0), text_color=(255, 255, 255)):
    # 修改background_color和text_color来自定义样式
```

## 🛠️ 故障排除

### 常见问题

1. **缺少依赖库**
   ```bash
   # 安装所有必要依赖
   pip3 install opencv-python pillow numpy aiohttp
   ```

2. **字体问题**
   - 系统会自动尝试使用macOS系统字体
   - 如果字体加载失败，会使用默认字体

3. **视频创建失败**
   - 确保ffmpeg已安装：`brew install ffmpeg`
   - 检查磁盘空间是否充足

4. **文章解析失败**
   - 确保文章格式正确
   - 检查文件编码是否为UTF-8

### 调试模式

运行转换脚本时添加调试信息：

```python
# 在auto_publish_articles.py中添加
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 自动化设置

### 定时自动发布

可以设置定时任务来自动发布新文章：

```bash
# 编辑crontab
crontab -e

# 添加定时任务（每天上午9点检查并发布）
0 9 * * * cd /Users/ax/wechat-publisher && ./article_manager.sh publish >> /Users/ax/wechat-publisher/article_publish.log 2>&1
```

### 监控发布状态

使用 `article_manager.sh status` 命令定期检查发布状态。

## 📈 效果优化建议

1. **文章内容优化**
   - 使用清晰的标题结构
   - 添加合适的图片
   - 保持段落简洁

2. **视频内容优化**
   - 控制幻灯片数量（建议5-8张）
   - 每张幻灯片文字不要过多
   - 使用吸引人的标题

3. **发布策略**
   - 选择合适的发布时间
   - 针对不同平台调整内容
   - 监控发布效果并优化

## 🎯 总结

这个文章自动发布系统可以：

- ✅ 自动解析Markdown文章
- ✅ 智能提取关键内容
- ✅ 生成视频脚本
- ✅ 创建幻灯片式视频
- ✅ 避免重复发布
- ✅ 集成现有发布系统

使用简单，功能强大，非常适合技术博客和文章的自动化视频发布！