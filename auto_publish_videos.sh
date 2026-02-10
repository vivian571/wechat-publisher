#!/bin/bash

# 自动视频发布脚本
# 监控指定目录并自动发布新视频到所有支持的平台

set -euo pipefail

# 配置
VIDEO_DIR="/Users/ax/wechat-publisher/social-auto-upload/videoFile"
SCRIPT_DIR="/Users/ax/wechat-publisher/social-auto-upload"
LOG_FILE="/Users/ax/wechat-publisher/auto_publish.log"
PROCESSED_LOG="/Users/ax/wechat-publisher/published_videos.log"
LOCK_FILE="/tmp/auto_publish.lock"

# 颜色配置
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 支持的平台
PLATFORMS=("douyin" "tencent" "kuaishou")
ACCOUNTS=("main" "main" "main")

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [警告]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [错误]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] [信息]${NC} $1" | tee -a "$LOG_FILE"
}

# 检查锁文件
check_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local pid=$(cat "$LOCK_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            warn "另一个发布进程正在运行 (PID: $pid)"
            exit 0
        else
            warn "发现过期锁文件，正在清理..."
            rm -f "$LOCK_FILE"
        fi
    fi
}

# 创建锁文件
create_lock() {
    echo $$ > "$LOCK_FILE"
    trap 'rm -f "$LOCK_FILE"; exit 0' EXIT INT TERM
}

# 检查视频文件是否有效
validate_video() {
    local video_file="$1"
    
    if [[ ! -f "$video_file" ]]; then
        error "视频文件不存在: $video_file"
        return 1
    fi
    
    # 检查文件大小（至少1MB）
    local file_size=$(stat -f%z "$video_file" 2>/dev/null || stat -c%s "$video_file" 2>/dev/null || echo "0")
    if [[ $file_size -lt 1048576 ]]; then
        error "视频文件太小: $video_file ($(($file_size / 1024))KB)"
        return 1
    fi
    
    # 检查文件扩展名
    if [[ ! "$video_file" =~ \.(mp4|mov|avi|mkv)$ ]]; then
        error "不支持的文件格式: $video_file"
        return 1
    fi
    
    return 0
}

# 检查视频是否已经发布过
is_published() {
    local video_name="$1"
    
    if [[ -f "$PROCESSED_LOG" ]] && grep -q "$video_name" "$PROCESSED_LOG"; then
        return 0
    fi
    return 1
}

# 记录已发布的视频
mark_published() {
    local video_name="$1"
    local platforms="$2"
    local status="$3"
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') | $video_name | $platforms | $status" >> "$PROCESSED_LOG"
}

# 发布视频到指定平台
publish_video() {
    local video_file="$1"
    local platform="$2"
    local account="$3"
    
    local video_name=$(basename "$video_file")
    
    log "正在发布到 $platform: $video_name"
    
    cd "$SCRIPT_DIR"
    
    # 运行发布命令
    local output
    local exit_code
    
    output=$(python3 cli_main.py "$platform" "$account" upload "$video_file" 2>&1) && exit_code=0 || exit_code=$?
    
    if [[ $exit_code -eq 0 ]]; then
        log "✅ 成功发布到 $platform: $video_name"
        echo "$output" | grep -E "(成功|success|published)" | head -5 | while read line; do
            info "  ↳ $line"
        done
        return 0
    else
        error "❌ 发布到 $platform 失败: $video_name"
        echo "$output" | grep -E "(错误|error|失败|failed)" | head -3 | while read line; do
            error "  ↳ $line"
        done
        return 1
    fi
}

# 发布视频到所有平台
publish_to_all_platforms() {
    local video_file="$1"
    local video_name=$(basename "$video_file")
    
    log "开始发布到所有平台: $video_name"
    
    local success_count=0
    local total_count=${#PLATFORMS[@]}
    local success_platforms=()
    local failed_platforms=()
    
    for i in "${!PLATFORMS[@]}"; do
        local platform="${PLATFORMS[$i]}"
        local account="${ACCOUNTS[$i]}"
        
        if publish_video "$video_file" "$platform" "$account"; then
            ((success_count++))
            success_platforms+=("$platform")
        else
            failed_platforms+=("$platform")
        fi
        
        # 平台间短暂延迟
        sleep 5
    done
    
    # 记录发布结果
    local status="部分成功"
    if [[ $success_count -eq $total_count ]]; then
        status="全部成功"
    elif [[ $success_count -eq 0 ]]; then
        status="全部失败"
    fi
    
    mark_published "$video_name" "$(IFS=,; echo "${success_platforms[*]}")" "$status"
    
    log "发布完成: $video_name"
    log "成功: $success_count/$total_count"
    
    if [[ ${#success_platforms[@]} -gt 0 ]]; then
        info "成功平台: $(IFS=,; echo "${success_platforms[*]}")"
    fi
    
    if [[ ${#failed_platforms[@]} -gt 0 ]]; then
        warn "失败平台: $(IFS=,; echo "${failed_platforms[*]}")"
    fi
    
    return $((total_count - success_count))
}

# 扫描并发布新视频
scan_and_publish() {
    log "开始扫描视频目录: $VIDEO_DIR"
    
    local new_videos=()
    local processed_count=0
    local error_count=0
    
    # 查找所有视频文件
    while IFS= read -r -d '' video_file; do
        local video_name=$(basename "$video_file")
        
        # 跳过已发布的视频
        if is_published "$video_name"; then
            continue
        fi
        
        # 验证视频文件
        if validate_video "$video_file"; then
            new_videos+=("$video_file")
            info "发现新视频: $video_name"
        fi
    done < <(find "$VIDEO_DIR" -type f \( -iname "*.mp4" -o -iname "*.mov" -o -iname "*.avi" -o -iname "*.mkv" \) -print0)
    
    local total_new=${#new_videos[@]}
    
    if [[ $total_new -eq 0 ]]; then
        info "未发现新视频需要发布"
        return 0
    fi
    
    log "发现 $total_new 个新视频，开始发布..."
    
    # 发布每个新视频
    for video_file in "${new_videos[@]}"; do
        if publish_to_all_platforms "$video_file"; then
            ((processed_count++))
        else
            ((error_count++))
        fi
        
        # 视频间延迟
        sleep 10
    done
    
    log "发布任务完成"
    log "处理: $processed_count, 错误: $error_count, 总计: $total_new"
    
    return $error_count
}

# 显示统计信息
show_stats() {
    log "发布统计信息"
    
    if [[ -f "$PROCESSED_LOG" ]]; then
        local total_published=$(wc -l < "$PROCESSED_LOG")
        local today_published=$(grep "^$(date '+%Y-%m-%d')" "$PROCESSED_LOG" | wc -l)
        
        info "总发布数: $total_published"
        info "今日发布: $today_published"
        
        # 显示最近发布
        if [[ $total_published -gt 0 ]]; then
            info "最近发布记录:"
            tail -5 "$PROCESSED_LOG" | while IFS='|' read -r date video platforms status; do
                info "  $date | $(basename "$video") | $platforms | $status"
            done
        fi
    else
        info "暂无发布记录"
    fi
}

# 清理旧日志
cleanup_logs() {
    local max_log_size=10485760  # 10MB
    
    if [[ -f "$LOG_FILE" ]] && [[ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo "0") -gt $max_log_size ]]; then
        mv "$LOG_FILE" "${LOG_FILE}.old"
        log "日志文件已轮转"
    fi
}

# 显示帮助
show_help() {
    cat << EOF
自动视频发布脚本

用法: $0 [选项]

选项:
    -h, --help      显示此帮助信息
    -s, --stats     显示发布统计信息
    -t, --test      测试模式（不实际发布）
    -f, --force     强制重新发布已发布的视频
    -c, --cleanup   清理旧日志文件

功能:
    自动监控指定目录中的新视频文件
    将新视频发布到所有支持的平台（抖音、腾讯、快手）
    记录发布历史和统计信息
    支持错误处理和重试机制

示例:
    $0              # 正常运行，发布新视频
    $0 --stats      # 显示统计信息
    $0 --cleanup    # 清理日志文件

配置文件:
    视频目录: $VIDEO_DIR
    日志文件: $LOG_FILE
    发布记录: $PROCESSED_LOG

EOF
}

# 主函数
main() {
    local test_mode=false
    local force_mode=false
    local show_stats_only=false
    local cleanup_mode=false
    
    # 解析命令行参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--stats)
                show_stats_only=true
                ;;
            -t|--test)
                test_mode=true
                ;;
            -f|--force)
                force_mode=true
                ;;
            -c|--cleanup)
                cleanup_mode=true
                ;;
            *)
                error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
    
    # 创建必要的目录和文件
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$PROCESSED_LOG")"
    touch "$LOG_FILE" "$PROCESSED_LOG"
    
    log "自动视频发布脚本启动"
    
    # 检查锁文件
    check_lock
    create_lock
    
    # 清理模式
    if [[ "$cleanup_mode" == true ]]; then
        cleanup_logs
        log "清理完成"
        exit 0
    fi
    
    # 统计模式
    if [[ "$show_stats_only" == true ]]; then
        show_stats
        exit 0
    fi
    
    # 测试模式警告
    if [[ "$test_mode" == true ]]; then
        warn "测试模式：不会实际发布视频"
    fi
    
    # 检查必要目录
    if [[ ! -d "$VIDEO_DIR" ]]; then
        error "视频目录不存在: $VIDEO_DIR"
        exit 1
    fi
    
    if [[ ! -d "$SCRIPT_DIR" ]]; then
        error "脚本目录不存在: $SCRIPT_DIR"
        exit 1
    fi
    
    # 执行主要任务
    scan_and_publish
    
    # 显示统计信息
    show_stats
    
    # 清理日志
    cleanup_logs
    
    log "自动视频发布脚本完成"
}

# 运行主函数
main "$@"