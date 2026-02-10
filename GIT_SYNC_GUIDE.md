# Git自动同步配置指南

## 概述

本项目已经配置了智能Git自动同步系统，可以自动检测代码更改、提交并推送到GitHub。以下是完整的配置和使用指南。

## 🚀 快速开始

### 1. 手动运行同步
```bash
cd /Users/ax/wechat-publisher
./auto_git_sync.sh
```

### 2. 设置自动定时同步（推荐）

由于macOS系统的安全限制，我们需要使用LaunchAgent来设置定时任务：

#### 安装LaunchAgent（需要管理员权限）
```bash
# 1. 复制配置文件到LaunchAgents目录
sudo cp com.wechat-publisher.git-sync.plist ~/Library/LaunchAgents/

# 2. 加载定时任务
launchctl load ~/Library/LaunchAgents/com.wechat-publisher.git-sync.plist

# 3. 验证任务已加载
launchctl list | grep com.wechat-publisher.git-sync
```

#### 卸载LaunchAgent
```bash
launchctl unload ~/Library/LaunchAgents/com.wechat-publisher.git-sync.plist
rm ~/Library/LaunchAgents/com.wechat-publisher.git-sync.plist
```

## 📋 功能特性

### 自动同步脚本 (`auto_git_sync.sh`)
- ✅ 智能检测代码更改
- ✅ 自动提交和推送
- ✅ 多项目支持
- ✅ 详细的日志记录
- ✅ 错误处理和恢复
- ✅ 网络连接检查
- ✅ 统计信息报告

### 监控的项目
1. **主项目**: `/Users/ax/wechat-publisher`
   - GitHub远程: https://github.com/vivian571/wechat-publisher.git
   
2. **子项目**: `/Users/ax/wechat-publisher/social-auto-upload`
   - 继承主项目的Git配置

## 📊 日志文件

### 主要日志
- **同步日志**: `/Users/ax/wechat-publisher/git_sync.log`
- **定时任务日志**: `/Users/ax/wechat-publisher/launchd.log`
- **错误日志**: `/Users/ax/wechat-publisher/launchd_error.log`

### 查看日志命令
```bash
# 实时查看同步日志
tail -f /Users/ax/wechat-publisher/git_sync.log

# 查看定时任务日志
tail -f /Users/ax/wechat-publisher/launchd.log

# 查看错误日志
tail -f /Users/ax/wechat-publisher/launchd_error.log
```

## ⚙️ 配置选项

### 同步频率
当前配置为**每小时同步一次**（3600秒）。如需修改：

1. 编辑 `com.wechat-publisher.git-sync.plist`
2. 修改 `<integer>3600</integer>` 为你需要的秒数
3. 重新加载配置

### 常用时间间隔
- 每15分钟: 900
- 每30分钟: 1800
- 每小时: 3600（当前设置）
- 每2小时: 7200
- 每6小时: 21600
- 每12小时: 43200

## 🔧 管理命令

### LaunchAgent管理
```bash
# 查看所有定时任务
launchctl list

# 查看特定任务状态
launchctl list | grep com.wechat-publisher.git-sync

# 停止任务
launchctl unload ~/Library/LaunchAgents/com.wechat-publisher.git-sync.plist

# 启动任务
launchctl load ~/Library/LaunchAgents/com.wechat-publisher.git-sync.plist
```

### Git同步管理
```bash
# 手动运行同步
cd /Users/ax/wechat-publisher
./auto_git_sync.sh

# 查看同步脚本帮助
./auto_git_sync.sh --help

# 查看版本
./auto_git_sync.sh --version
```

## 📈 监控和调试

### 检查同步状态
```bash
# 查看最近同步记录
tail -20 /Users/ax/wechat-publisher/git_sync.log

# 检查是否有错误
grep -i error /Users/ax/wechat-publisher/git_sync.log

# 查看Git状态
cd /Users/ax/wechat-publisher
git status
git remote -v
```

### 测试同步功能
```bash
# 创建一个测试文件来验证同步
echo "测试同步 - $(date)" > /Users/ax/wechat-publisher/test_sync.txt

# 手动运行同步
./auto_git_sync.sh

# 检查GitHub是否收到更新
curl -s https://api.github.com/repos/vivian571/wechat-publisher/commits | head -20
```

## 🚨 故障排除

### 常见问题

#### 1. 权限问题
```bash
# 确保脚本有执行权限
chmod +x /Users/ax/wechat-publisher/auto_git_sync.sh
```

#### 2. 网络连接问题
- 检查网络连接
- 验证GitHub访问权限
- 查看错误日志获取详细信息

#### 3. Git配置问题
```bash
# 验证Git配置
git config --list
git remote -v
```

#### 4. LaunchAgent未运行
```bash
# 检查任务状态
launchctl list | grep com.wechat-publisher.git-sync

# 重新加载配置
launchctl unload ~/Library/LaunchAgents/com.wechat-publisher.git-sync.plist
launchctl load ~/Library/LaunchAgents/com.wechat-publisher.git-sync.plist
```

## 📚 高级配置

### 添加更多项目
编辑 `auto_git_sync.sh`，在 `PROJECTS` 数组中添加新路径：

```bash
PROJECTS=(
    "/Users/ax/wechat-publisher"
    "/Users/ax/wechat-publisher/social-auto-upload"
    "/path/to/your/new/project"  # 添加新项目
)
```

### 自定义提交消息
修改 `auto_git_sync.sh` 中的 `commit_msg` 变量：

```bash
local commit_msg="自定义提交消息 - $(date '+%Y-%m-%d %H:%M:%S')"
```

## 📞 支持

如果遇到问题：
1. 查看日志文件获取错误信息
2. 检查网络连接和Git配置
3. 验证GitHub仓库权限
4. 手动运行脚本测试

## 🎯 总结

✅ **已完成配置**:
- GitHub远程仓库已设置
- 自动同步脚本已创建
- LaunchAgent配置文件已准备
- 详细的日志和监控已配置

🔄 **自动同步流程**:
1. 每小时自动检测代码更改
2. 自动提交检测到的新文件和修改
3. 推送到GitHub远程仓库
4. 记录详细的同步日志

现在您的项目将自动保持与GitHub同步！