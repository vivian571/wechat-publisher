#!/bin/bash

# 自动Git同步定时任务设置脚本
# 该脚本会配置cron任务来定期运行Git同步

set -euo pipefail

SCRIPT_PATH="/Users/ax/wechat-publisher/auto_git_sync.sh"
CRON_LOG="/Users/ax/wechat-publisher/cron.log"

# 颜色配置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [警告]${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [错误]${NC} $1"
}

# 检查脚本是否存在
if [[ ! -f "$SCRIPT_PATH" ]]; then
    error "同步脚本不存在: $SCRIPT_PATH"
    exit 1
fi

# 检查脚本是否有执行权限
if [[ ! -x "$SCRIPT_PATH" ]]; then
    warn "脚本没有执行权限，正在添加..."
    chmod +x "$SCRIPT_PATH"
fi

log "正在配置Git自动同步定时任务..."

# 获取当前用户的crontab
current_cron=$(crontab -l 2>/dev/null || echo "")

# 检查是否已存在相同的定时任务
if echo "$current_cron" | grep -q "auto_git_sync.sh"; then
    warn "检测到已存在的Git同步定时任务"
    echo "当前定时任务:"
    echo "$current_cron" | grep "auto_git_sync.sh"
    
    read -p "是否更新定时任务配置? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "取消配置更新"
        exit 0
    fi
fi

# 配置选项
echo "请选择同步频率:"
echo "1) 每5分钟 (开发模式)"
echo "2) 每15分钟"
echo "3) 每30分钟"
echo "4) 每小时 (推荐)"
echo "5) 每2小时"
echo "6) 每天4次 (6小时间隔)"
echo "7) 每天2次 (12小时间隔)"
echo "8) 自定义"

read -p "请选择 (1-8): " choice

case $choice in
    1) cron_schedule="*/5 * * * *" ;;
    2) cron_schedule="*/15 * * * *" ;;
    3) cron_schedule="*/30 * * * *" ;;
    4) cron_schedule="0 * * * *" ;;
    5) cron_schedule="0 */2 * * *" ;;
    6) cron_schedule="0 */6 * * *" ;;
    7) cron_schedule="0 */12 * * *" ;;
    8) 
        read -p "请输入自定义cron表达式 (例如: 0 * * * * 表示每小时): " cron_schedule
        ;;
    *)
        error "无效选择，使用默认设置 (每小时)"
        cron_schedule="0 * * * *"
        ;;
esac

# 创建新的crontab配置
new_cron="$current_cron"

# 移除旧的同步任务
new_cron=$(echo "$new_cron" | grep -v "auto_git_sync.sh" || echo "")

# 添加新的同步任务
cron_entry="$cron_schedule $SCRIPT_PATH >> $CRON_LOG 2>&1"
new_cron="$new_cron
# Git自动同步任务 - 由设置脚本创建
cron_entry"

# 安装新的crontab
echo "$new_cron" | crontab -

log "定时任务配置完成!"
log "同步频率: $cron_schedule"
log "脚本路径: $SCRIPT_PATH"
log "日志文件: $CRON_LOG"

# 显示当前crontab
echo
echo "当前定时任务列表:"
crontab -l

echo
log "配置摘要:"
echo "- 同步频率: $cron_schedule"
echo "- 监控项目:"
for project in "/Users/ax/wechat-publisher" "/Users/ax/wechat-publisher/social-auto-upload"; do
    echo "  * $(basename "$project")"
done
echo "- 日志文件: $CRON_LOG"

# 提供管理命令
echo
log "管理命令:"
echo "  查看日志:    tail -f $CRON_LOG"
echo "  查看任务:    crontab -l"
echo "  移除任务:    crontab -r"
echo "  手动同步:    $SCRIPT_PATH"

# 测试运行
read -p "是否立即测试运行同步脚本? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log "正在测试运行同步脚本..."
    "$SCRIPT_PATH"
    log "测试完成!"
fi

log "Git自动同步配置完成!"