#!/bin/bash

# 视频发布管理器
# 用于管理和监控自动视频发布系统

set -euo pipefail

SCRIPT_DIR="/Users/ax/wechat-publisher"
VIDEO_DIR="/Users/ax/wechat-publisher/social-auto-upload/videoFile"
LOG_FILE="/Users/ax/wechat-publisher/video_publish.log"
ERROR_LOG="/Users/ax/wechat-publisher/video_publish_error.log"
PUBLISHED_LOG="/Users/ax/wechat-publisher/published_videos.log"

# 颜色配置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [信息]${NC} $1"
}

cyan() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# 显示帮助
show_help() {
    cat << EOF
视频发布管理器

用法: $0 [命令] [选项]

命令:
    status              显示发布系统状态
    start               启动自动发布服务
    stop                停止自动发布服务
    restart             重启自动发布服务
    publish             立即发布所有新视频
    publish-one <文件>  发布指定视频文件
    logs                显示实时日志
    stats               显示发布统计
    cleanup             清理旧日志
    test                测试发布功能
    help                显示此帮助

选项:
    -f, --force         强制操作
    -v, --verbose       详细输出
    -q, --quiet         静默模式

示例:
    $0 status                    # 查看系统状态
    $0 start                     # 启动自动发布
    $0 publish                   # 立即发布新视频
    $0 publish-one video.mp4     # 发布指定视频
    $0 logs                      # 查看实时日志
    $0 stats                     # 查看统计信息

EOF
}

# 检查服务状态
check_service_status() {
    local service_name="com.wechat-publisher.video-auto-publish"
    local is_loaded=$(launchctl list 2>/dev/null | grep "$service_name" | wc -l)
    
    if [[ $is_loaded -gt 0 ]]; then
        echo "运行中"
        return 0
    else
        echo "已停止"
        return 1
    fi
}

# 显示系统状态
show_status() {
    cyan "=== 视频发布系统状态 ==="
    
    # 服务状态
    local service_status
    service_status=$(check_service_status)
    
    if [[ "$service_status" == "运行中" ]]; then
        log "自动发布服务: ✅ 运行中"
    else
        warn "自动发布服务: ❌ 已停止"
    fi
    
    # 视频目录状态
    if [[ -d "$VIDEO_DIR" ]]; then
        local video_count=$(find "$VIDEO_DIR" -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" | wc -l)
        info "视频目录: $VIDEO_DIR ($video_count 个视频文件)"
    else
        error "视频目录不存在: $VIDEO_DIR"
    fi
    
    # 日志文件状态
    if [[ -f "$LOG_FILE" ]]; then
        local log_size=$(ls -lh "$LOG_FILE" | awk '{print $5}')
        info "主日志文件: $LOG_FILE ($log_size)"
    else
        warn "主日志文件不存在"
    fi
    
    if [[ -f "$PUBLISHED_LOG" ]]; then
        local published_count=$(wc -l < "$PUBLISHED_LOG")
        info "发布记录: $published_count 条记录"
    else
        info "发布记录: 暂无记录"
    fi
    
    # 最近活动
    if [[ -f "$LOG_FILE" ]]; then
        local last_activity=$(tail -1 "$LOG_FILE" 2>/dev/null | cut -d']' -f2 | cut -d'[' -f2 | xargs || echo "无记录")
        info "最近活动: $last_activity"
    fi
    
    cyan "======================"
}

# 启动服务
start_service() {
    log "正在启动自动发布服务..."
    
    local service_file="$SCRIPT_DIR/com.wechat-publisher.video-auto-publish.plist"
    
    if [[ ! -f "$service_file" ]]; then
        error "服务配置文件不存在: $service_file"
        return 1
    fi
    
    # 检查是否已运行
    if check_service_status > /dev/null; then
        warn "服务已经在运行中"
        return 0
    fi
    
    # 复制到LaunchAgents目录
    if [[ ! -f "$HOME/Library/LaunchAgents/com.wechat-publisher.video-auto-publish.plist" ]]; then
        info "正在安装服务配置..."
        cp "$service_file" "$HOME/Library/LaunchAgents/" || {
            error "需要管理员权限来安装服务配置"
            return 1
        }
    fi
    
    # 加载服务
    launchctl load "$HOME/Library/LaunchAgents/com.wechat-publisher.video-auto-publish.plist" || {
        error "启动服务失败"
        return 1
    }
    
    log "✅ 自动发布服务已启动"
    log "服务将每30分钟检查一次新视频"
}

# 停止服务
stop_service() {
    log "正在停止自动发布服务..."
    
    local service_name="com.wechat-publisher.video-auto-publish"
    
    if ! check_service_status > /dev/null; then
        warn "服务已经停止"
        return 0
    fi
    
    launchctl unload "$HOME/Library/LaunchAgents/com.wechat-publisher.video-auto-publish.plist" || {
        error "停止服务失败"
        return 1
    }
    
    log "✅ 自动发布服务已停止"
}

# 重启服务
restart_service() {
    info "正在重启自动发布服务..."
    stop_service
    sleep 2
    start_service
}

# 立即发布
publish_now() {
    log "正在执行立即发布..."
    
    local script_path="$SCRIPT_DIR/auto_publish_videos.sh"
    
    if [[ ! -f "$script_path" ]]; then
        error "发布脚本不存在: $script_path"
        return 1
    fi
    
    if [[ ! -x "$script_path" ]]; then
        chmod +x "$script_path"
    fi
    
    log "开始发布新视频..."
    "$script_path"
    
    log "立即发布完成"
}

# 发布单个视频
publish_single() {
    local video_file="$1"
    
    if [[ ! -f "$video_file" ]]; then
        error "视频文件不存在: $video_file"
        return 1
    fi
    
    log "正在发布单个视频: $(basename "$video_file")"
    
    # 这里可以添加具体的发布逻辑
    # 由于需要与现有的cli_main.py集成，我们先显示信息
    info "视频文件: $video_file"
    info "文件大小: $(ls -lh "$video_file" | awk '{print $5}')"
    info "修改时间: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$video_file" 2>/dev/null || stat -c %y "$video_file" 2>/dev/null)"
    
    # 显示发布命令示例
    cyan "发布命令示例:"
    for platform in "douyin" "tencent" "kuaishou"; do
        info "  python3 $SCRIPT_DIR/social-auto-upload/cli_main.py $platform main upload \"$video_file\""
    done
    
    warn "请手动运行上述命令来发布此视频"
}

# 显示日志
show_logs() {
    local log_file="$1"
    
    if [[ ! -f "$log_file" ]]; then
        error "日志文件不存在: $log_file"
        return 1
    fi
    
    info "正在显示实时日志，按 Ctrl+C 退出..."
    tail -f "$log_file"
}

# 显示统计
show_stats() {
    cyan "=== 视频发布统计 ==="
    
    # 总体统计
    if [[ -f "$PUBLISHED_LOG" ]]; then
        local total_published=$(wc -l < "$PUBLISHED_LOG")
        local today_published=$(grep "^$(date '+%Y-%m-%d')" "$PUBLISHED_LOG" | wc -l)
        local this_week=$(grep "^$(date -v-7d '+%Y-%m-%d')" "$PUBLISHED_LOG" | wc -l)
        
        log "总发布数: $total_published"
        log "今日发布: $today_published"
        log "本周发布: $this_week"
        
        # 平台统计
        if [[ $total_published -gt 0 ]]; then
            cyan "平台发布统计:"
            for platform in "douyin" "tencent" "kuaishou"; do
                local platform_count=$(grep "$platform" "$PUBLISHED_LOG" | wc -l)
                info "  $platform: $platform_count"
            done
        fi
        
        # 最近发布
        if [[ $total_published -gt 0 ]]; then
            cyan "最近发布记录:"
            tail -5 "$PUBLISHED_LOG" | nl | while IFS='|' read -r date video platforms status; do
                info "  $date | $(basename "$video") | $platforms | $status"
            done
        fi
    else
        warn "暂无发布记录"
    fi
    
    # 视频目录统计
    if [[ -d "$VIDEO_DIR" ]]; then
        local total_videos=$(find "$VIDEO_DIR" -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" | wc -l)
        local new_videos=0
        
        if [[ -f "$PUBLISHED_LOG" ]]; then
            while IFS= read -r -d '' video; do
                local video_name=$(basename "$video")
                if ! grep -q "$video_name" "$PUBLISHED_LOG"; then
                    ((new_videos++))
                fi
            done < <(find "$VIDEO_DIR" -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" -print0)
        else
            new_videos=$total_videos
        fi
        
        cyan "视频目录状态:"
        info "  总视频数: $total_videos"
        info "  待发布: $new_videos"
    fi
    
    cyan "=================="
}

# 测试功能
test_function() {
    log "正在测试发布功能..."
    
    # 检查依赖
    local deps_ok=true
    
    # 检查Python
    if ! command -v python3 > /dev/null; then
        error "Python3 未安装"
        deps_ok=false
    else
        info "✅ Python3: $(python3 --version)"
    fi
    
    # 检查发布脚本
    if [[ -f "$SCRIPT_DIR/auto_publish_videos.sh" ]]; then
        info "✅ 自动发布脚本: 存在"
    else
        error "❌ 自动发布脚本: 不存在"
        deps_ok=false
    fi
    
    # 检查视频目录
    if [[ -d "$VIDEO_DIR" ]]; then
        info "✅ 视频目录: 存在"
    else
        error "❌ 视频目录: 不存在"
        deps_ok=false
    fi
    
    # 检查cookie文件
    local cookie_dir="$SCRIPT_DIR/social-auto-upload/cookies"
    if [[ -d "$cookie_dir" ]]; then
        for platform in "douyin" "tencent" "kuaishou"; do
            if [[ -f "$cookie_dir/${platform}_main.json" ]]; then
                info "✅ $platform Cookie: 存在"
            else
                warn "⚠️  $platform Cookie: 不存在"
            fi
        done
    fi
    
    if [[ "$deps_ok" == true ]]; then
        log "✅ 基础测试通过"
    else
        error "❌ 基础测试失败"
        return 1
    fi
}

# 清理日志
cleanup_logs() {
    log "正在清理旧日志..."
    
    local logs=("$LOG_FILE" "$ERROR_LOG")
    
    for log_file in "${logs[@]}"; do
        if [[ -f "$log_file" ]]; then
            local size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
            local max_size=10485760  # 10MB
            
            if [[ $size -gt $max_size ]]; then
                mv "$log_file" "${log_file}.old"
                info "已轮转日志: $(basename "$log_file") ($(($size / 1024))KB)"
            fi
        fi
    done
    
    log "日志清理完成"
}

# 主函数
main() {
    local command="${1:-status}"
    local verbose=false
    local force=false
    
    # 解析选项
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                verbose=true
                ;;
            -f|--force)
                force=true
                ;;
            -q|--quiet)
                exec > /dev/null 2>&1
                ;;
            *)
                if [[ "$1" != "$command" ]]; then
                    command="$1"
                fi
                ;;
        esac
        shift
    done
    
    case "$command" in
        status|s)
            show_status
            ;;
        start|begin)
            start_service
            ;;
        stop|end)
            stop_service
            ;;
        restart|reload)
            restart_service
            ;;
        publish|p)
            publish_now
            ;;
        publish-one|single)
            if [[ -z "${2:-}" ]]; then
                error "请指定视频文件路径"
                exit 1
            fi
            publish_single "$2"
            ;;
        logs|log)
            show_logs "$LOG_FILE"
            ;;
        error-logs|errors)
            show_logs "$ERROR_LOG"
            ;;
        stats|stat)
            show_stats
            ;;
        test|check)
            test_function
            ;;
        cleanup|clean)
            cleanup_logs
            ;;
        help|h|*)
            show_help
            ;;
    esac
}

# 运行主函数
main "$@"