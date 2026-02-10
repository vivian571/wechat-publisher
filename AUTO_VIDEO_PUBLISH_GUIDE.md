# 🎬 自动视频发布系统

## 系统概述

我已经为您创建了一个完整的自动视频发布系统，可以自动监控 `/Users/ax/wechat-publisher/social-auto-upload/videoFile` 目录中的新视频文件，并自动发布到所有支持的平台（抖音、腾讯、快手）。

## 📁 创建的文件

### 核心脚本
1. **`auto_publish_videos.sh`** - 自动发布脚本
   - 监控视频目录中的新文件
   - 自动发布到所有平台
   - 智能去重和错误处理

2. **`video_manager.sh`** - 发布管理器
   - 服务状态管理
   - 手动发布控制
   - 统计信息查看

3. **`video_dashboard.sh`** - 监控仪表板
   - 实时状态监控
   - 交互式操作界面
   - 可视化统计信息

### 配置文件
4. **`com.wechat-publisher.video-auto-publish.plist`** - macOS定时任务配置
   - 每30分钟自动检查新视频
   - 自动启动和运行管理

## 🚀 快速开始

### 1. 立即测试发布
```bash
cd /Users/ax/wechat-publisher
./video_manager.sh test      # 测试系统状态
./video_manager.sh publish   # 立即发布新视频
```

### 2. 启动自动发布服务
```bash
# 安装并启动服务
sudo cp com.wechat-publisher.video-auto-publish.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.wechat-publisher.video-auto-publish.plist

# 验证服务状态
./video_manager.sh status
```

### 3. 使用监控仪表板
```bash
# 启动交互式监控界面
./video_dashboard.sh

# 或者单次显示模式
./video_dashboard.sh --single
```

## 📊 功能特性

### 🎯 自动发布功能
- ✅ **智能监控**: 自动检测新视频文件
- ✅ **多平台发布**: 同时发布到抖音、腾讯、快手
- ✅ **去重机制**: 避免重复发布同一视频
- ✅ **错误处理**: 智能重试和错误恢复
- ✅ **发布记录**: 完整的发布历史记录

### 🔧 管理功能
- ✅ **服务管理**: 启动/停止自动发布服务
- ✅ **手动控制**: 手动发布指定视频
- ✅ **状态监控**: 实时查看系统状态
- ✅ **统计信息**: 详细的发布统计
- ✅ **日志管理**: 完整的日志记录和轮转

### 📈 监控功能
- ✅ **实时仪表板**: 可视化状态监控
- ✅ **平台状态**: 各平台连接状态
- ✅ **活动日志**: 最近发布活动
- ✅ **统计图表**: 发布趋势和分布

## 🎮 使用指南

### 基本命令

#### 服务管理
```bash
./video_manager.sh status      # 查看系统状态
./video_manager.sh start       # 启动自动发布服务
./video_manager.sh stop        # 停止自动发布服务
./video_manager.sh restart      # 重启服务
```

#### 发布控制
```bash
./video_manager.sh publish      # 立即发布所有新视频
./video_manager.sh publish-one video.mp4  # 发布指定视频
./video_manager.sh stats        # 查看发布统计
```

#### 日志和监控
```bash
./video_manager.sh logs         # 查看实时日志
./video_manager.sh error-logs   # 查看错误日志
./video_dashboard.sh          # 启动监控仪表板
```

### 监控仪表板操作

启动仪表板后，您可以使用以下操作：
- **1**: 立即发布新视频
- **2**: 启动自动发布服务
- **3**: 停止自动发布服务
- **4**: 查看详细日志
- **5**: 刷新仪表板
- **6**: 退出仪表板

## 📁 文件和日志

### 重要文件
- **视频目录**: `/Users/ax/wechat-publisher/social-auto-upload/videoFile`
- **发布脚本**: `/Users/ax/wechat-publisher/auto_publish_videos.sh`
- **管理脚本**: `/Users/ax/wechat-publisher/video_manager.sh`
- **监控脚本**: `/Users/ax/wechat-publisher/video_dashboard.sh`

### 日志文件
- **主日志**: `/Users/ax/wechat-publisher/video_publish.log`
- **错误日志**: `/Users/ax/wechat-publisher/video_publish_error.log`
- **发布记录**: `/Users/ax/wechat-publisher/published_videos.log`
- **定时任务日志**: `/Users/ax/wechat-publisher/launchd.log`

## ⚙️ 配置选项

### 发布频率
默认每30分钟检查一次新视频。如需修改：
1. 编辑 `com.wechat-publisher.video-auto-publish.plist`
2. 修改 `<integer>1800</integer>`（秒为单位）
3. 重新加载服务配置

### 支持的视频格式
- MP4 (推荐)
- MOV
- AVI
- MKV

### 平台配置
确保以下cookie文件存在：
- 抖音: `social-auto-upload/cookies/douyin_main.json`
- 腾讯: `social-auto-upload/cookies/tencent_main.json`
- 快手: `social-auto-upload/cookies/kuaishou_main.json`

## 🔍 故障排除

### 常见问题

#### 1. 服务无法启动
```bash
# 检查权限
chmod +x *.sh

# 检查配置文件
ls -la ~/Library/LaunchAgents/com.wechat-publisher.video-auto-publish.plist

# 手动检查服务
launchctl list | grep video-auto-publish
```

#### 2. 视频无法发布
```bash
# 测试单个视频发布
./video_manager.sh publish-one video.mp4

# 检查cookie文件
ls -la social-auto-upload/cookies/

# 查看错误日志
tail -f video_publish_error.log
```

#### 3. 监控仪表板无法显示
```bash
# 检查终端颜色支持
echo $TERM

# 使用简化模式
./video_dashboard.sh --single
```

### 调试命令
```bash
# 查看服务状态
launchctl list | grep video-auto-publish

# 查看最近日志
tail -f video_publish.log

# 测试发布功能
./auto_publish_videos.sh --test

# 检查视频文件
ls -la social-auto-upload/videoFile/
```

## 📊 监控和报告

### 每日报告
系统会自动记录所有发布活动，您可以：
- 查看发布成功率
- 分析平台表现
- 监控错误频率
- 跟踪发布趋势

### 性能指标
- 平均发布时间
- 各平台成功率
- 错误类型分布
- 系统资源使用

## 🚀 高级功能

### 批量处理
系统支持批量发布多个视频，会自动：
- 按顺序处理每个视频
- 平台间添加适当延迟
- 记录详细的处理日志
- 提供失败重试机制

### 智能去重
通过发布记录避免重复发布：
- 基于文件名识别
- 支持强制重新发布
- 记录发布状态
- 提供发布历史查询

## 📞 支持

如果您遇到问题：

1. **查看日志**: 检查相关日志文件
2. **运行测试**: 使用 `./video_manager.sh test`
3. **检查配置**: 验证cookie文件和路径
4. **手动测试**: 尝试手动发布单个视频
5. **联系支持**: 提供相关日志和错误信息

---

🎉 **恭喜！** 您现在拥有了一个完整的自动视频发布系统。系统会自动监控您的新视频并发布到所有平台，同时提供完整的监控和管理功能。

系统已准备就绪，可以开始使用了！