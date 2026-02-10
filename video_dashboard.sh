#!/bin/bash

# 视频发布监控仪表板
# 提供实时的发布状态和统计信息

set -euo pipefail

SCRIPT_DIR="/Users/ax/wechat-publisher"
VIDEO_DIR="/Users/ax/wechat-publisher/social-auto-upload/videoFile"
LOG_FILE="/Users/ax/wechat-publisher/video_publish.log"
PUBLISHED_LOG="/Users/ax/wechat-publisher/published_videos.log"

# 颜色配置 - 更丰富的颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'

# 清除屏幕并显示标题
clear_screen() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    🎬 视频发布监控仪表板 v1.0                             ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
}

# 获取服务状态
get_service_status() {
    local service_name="com.wechat-publisher.video-auto-publish"
    if launchctl list 2>/dev/null | grep -q "$service_name"; then
        echo -e "${GREEN}● 运行中${NC}"
        return 0
    else
        echo -e "${RED}● 已停止${NC}"
        return 1
    fi
}

# 获取系统信息
get_system_info() {
    local current_time=$(date '+%Y-%m-%d %H:%M:%S')
    local uptime=$(uptime | awk '{print $3,$4}' | sed 's/,//')
    local load_avg=$(uptime | awk -F'load averages:' '{print $2}' | xargs)
    
    echo -e "${WHITE}系统信息:${NC}"
    echo -e "  ${GRAY}当前时间:${NC} $current_time"
    echo -e "  ${GRAY}运行时间:${NC} $uptime"
    echo -e "  ${GRAY}负载均衡:${NC} $load_avg"
    echo
}

# 获取视频统计
get_video_stats() {
    if [[ ! -d "$VIDEO_DIR" ]]; then
        echo -e "${RED}错误: 视频目录不存在${NC}"
        return 1
    fi
    
    local total_videos=$(find "$VIDEO_DIR" -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" 2>/dev/null | wc -l)
    local total_size=$(du -sh "$VIDEO_DIR" 2>/dev/null | awk '{print $1}')
    
    local new_videos=0
    if [[ -f "$PUBLISHED_LOG" ]]; then
        while IFS= read -r -d '' video; do
            local video_name=$(basename "$video")
            if ! grep -q "$video_name" "$PUBLISHED_LOG" 2>/dev/null; then
                ((new_videos++))
            fi
        done < <(find "$VIDEO_DIR" -name "*.mp4" -o -name "*.mov" -o -name "*.avi" -o -name "*.mkv" -print0 2>/dev/null)
    else
        new_videos=$total_videos
    fi
    
    echo -e "${WHITE}视频统计:${NC}"
    echo -e "  ${GRAY}总视频数:${NC} ${YELLOW}$total_videos${NC}"
    echo -e "  ${GRAY}总大小:${NC} ${YELLOW}$total_size${NC}"
    echo -e "  ${GRAY}待发布:${NC} ${GREEN}$new_videos${NC}"
    echo
}

# 获取发布统计
get_publish_stats() {
    if [[ ! -f "$PUBLISHED_LOG" ]]; then
        echo -e "${GRAY}暂无发布记录${NC}"
        return 0
    fi
    
    local total_published=$(wc -l < "$PUBLISHED_LOG")
    local today_published=$(grep "^$(date '+%Y-%m-%d')" "$PUBLISHED_LOG" | wc -l)
    local this_week=$(grep "^$(date -v-7d '+%Y-%m-%d')" "$PUBLISHED_LOG" 2>/dev/null | wc -l || echo "0")
    
    # 平台统计
    local douyin_count=$(grep "douyin" "$PUBLISHED_LOG" | wc -l)
    local tencent_count=$(grep "tencent" "$PUBLISHED_LOG" | wc -l)
    local kuaishou_count=$(grep "kuaishou" "$PUBLISHED_LOG" | wc -l)
    
    echo -e "${WHITE}发布统计:${NC}"
    echo -e "  ${GRAY}总发布数:${NC} ${GREEN}$total_published${NC}"
    echo -e "  ${GRAY}今日发布:${NC} ${YELLOW}$today_published${NC}"
    echo -e "  ${GRAY}本周发布:${NC} ${YELLOW}$this_week${NC}"
    echo -e "  ${GRAY}平台分布:${NC}"
    echo -e "    ${CYAN}抖音:${NC} $douyin_count"
    echo -e "    ${CYAN}腾讯:${NC} $tencent_count"
    echo -e "    ${CYAN}快手:${NC} $kuaishou_count"
    echo
}

# 获取最近活动
get_recent_activity() {
    if [[ ! -f "$LOG_FILE" ]]; then
        echo -e "${GRAY}暂无活动记录${NC}"
        return 0
    fi
    
    echo -e "${WHITE}最近活动:${NC}"
    
    # 最近5条成功记录
    local success_count=0
    while IFS= read -r line; do
        if [[ "$line" =~ ✅ ]]; then
            echo -e "  ${GREEN}✓${NC} $(echo "$line" | sed 's/.*\] //')"
            ((success_count++))
        fi
        if [[ $success_count -ge 3 ]]; then
            break
        fi
    done < <(tail -20 "$LOG_FILE" 2>/dev/null | tac)
    
    # 最近错误
    local error_count=0
    while IFS= read -r line; do
        if [[ "$line" =~ ❌ ]] || [[ "$line" =~ 错误 ]]; then
            echo -e "  ${RED}✗${NC} $(echo "$line" | sed 's/.*\] //')"
            ((error_count++))
        fi
        if [[ $error_count -ge 2 ]]; then
            break
        fi
    done < <(tail -20 "$LOG_FILE" 2>/dev/null | tac)
    
    echo
}

# 获取平台状态
get_platform_status() {
    echo -e "${WHITE}平台状态:${NC}"
    
    # 检查cookie文件
    local cookie_dir="$SCRIPT_DIR/social-auto-upload/cookies"
    
    for platform in "douyin" "tencent" "kuaishou"; do
        local cookie_file="$cookie_dir/${platform}_main.json"
        local status_color=$RED
        local status_text="未配置"
        
        if [[ -f "$cookie_file" ]]; then
            local file_size=$(stat -f%z "$cookie_file" 2>/dev/null || stat -c%s "$cookie_file" 2>/dev/null || echo "0")
            if [[ $file_size -gt 100 ]]; then
                status_color=$GREEN
                status_text="已配置"
            else
                status_color=$YELLOW
                status_text="配置异常"
            fi
        fi
        
        printf "  ${GRAY}%-8s:${NC} ${status_color}%-12s${NC}\n" "$platform" "$status_text"
    done
    
    echo
}

# 显示快速操作
show_quick_actions() {
    echo -e "${WHITE}快速操作:${NC}"
    echo -e "  ${GRAY}1.${NC} 立即发布新视频"
    echo -e "  ${GRAY}2.${NC} 启动自动发布服务"
    echo -e "  ${GRAY}3.${NC} 停止自动发布服务"
    echo -e "  ${GRAY}4.${NC} 查看详细日志"
    echo -e "  ${GRAY}5.${NC} 刷新仪表板"
    echo -e "  ${GRAY}6.${NC} 退出"
    echo
}

# 处理用户输入
handle_input() {
    read -t 1 -n 10000  # 清空输入缓冲区
    read -p "选择操作 (1-6): " choice
    
    case $choice in
        1)
            echo -e "\n${YELLOW}正在执行立即发布...${NC}"
            "$SCRIPT_DIR/video_manager.sh" publish
            read -p "按回车键继续..."
            ;;
        2)
            echo -e "\n${YELLOW}正在启动服务...${NC}"
            "$SCRIPT_DIR/video_manager.sh" start
            read -p "按回车键继续..."
            ;;
        3)
            echo -e "\n${YELLOW}正在停止服务...${NC}"
            "$SCRIPT_DIR/video_manager.sh" stop
            read -p "按回车键继续..."
            ;;
        4)
            echo -e "\n${YELLOW}显示日志，按 Ctrl+C 返回...${NC}"
            "$SCRIPT_DIR/video_manager.sh" logs
            ;;
        5)
            echo -e "\n${YELLOW}正在刷新...${NC}"
            ;;
        6|q|Q)
            echo -e "\n${GREEN}感谢使用！再见！${NC}"
            exit 0
            ;;
        *)
            if [[ -n "$choice" ]]; then
                echo -e "\n${RED}无效选择: $choice${NC}"
                sleep 1
            fi
            ;;
    esac
}

# 主循环
main_loop() {
    while true; do
        clear_screen
        
        # 服务状态
        local service_status
        service_status=$(get_service_status)
        echo -e "${WHITE}服务状态:${NC} $service_status"
        echo -e "${CYAN}┌────────────────────────────────────────────────────────────────────────────┐${NC}"
        
        # 系统信息
        get_system_info
        
        # 视频统计
        get_video_stats
        
        # 发布统计
        get_publish_stats
        
        # 最近活动
        get_recent_activity
        
        # 平台状态
        get_platform_status
        
        echo -e "${CYAN}└────────────────────────────────────────────────────────────────────────────┘${NC}"
        
        # 快速操作
        show_quick_actions
        
        # 处理用户输入
        handle_input
        
        # 自动刷新（如果没有用户输入）
        sleep 2
    done
}

# 单次显示模式
single_display() {
    clear_screen
    
    local service_status
    service_status=$(get_service_status)
    echo -e "${WHITE}服务状态:${NC} $service_status"
    echo -e "${CYAN}┌────────────────────────────────────────────────────────────────────────────┐${NC}"
    
    get_system_info
    get_video_stats
    get_publish_stats
    get_recent_activity
    get_platform_status
    
    echo -e "${CYAN}└────────────────────────────────────────────────────────────────────────────┘${NC}"
}

# 显示帮助
show_help() {
    cat << EOF
视频发布监控仪表板

用法: $0 [选项]

选项:
    -h, --help      显示此帮助信息
    -s, --single    单次显示模式（不进入循环）
    -r, --refresh   刷新间隔（秒，默认2秒）
    -q, --quiet     静默模式

示例:
    $0              # 启动交互式仪表板
    $0 --single     # 单次显示模式
    $0 -s -r 5      # 单次显示，5秒刷新一次

操作说明:
    在交互模式下，使用数字键选择操作:
    1 - 立即发布新视频
    2 - 启动自动发布服务  
    3 - 停止自动发布服务
    4 - 查看详细日志
    5 - 刷新仪表板
    6 - 退出

EOF
}

# 主函数
main() {
    local single_mode=false
    local refresh_interval=2
    local quiet_mode=false
    
    # 解析参数
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -s|--single)
                single_mode=true
                ;;
            -r|--refresh)
                refresh_interval="${2:-2}"
                shift
                ;;
            -q|--quiet)
                quiet_mode=true
                ;;
            *)
                error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
    
    if [[ "$quiet_mode" == true ]]; then
        exec > /dev/null 2>&1
    fi
    
    if [[ "$single_mode" == true ]]; then
        # 单次显示模式
        while true; do
            single_display
            sleep "$refresh_interval"
        done
    else
        # 交互式模式
        main_loop
    fi
}

# 捕获中断信号
trap 'echo -e "\n${GREEN}感谢使用！再见！${NC}"; exit 0' INT TERM

# 运行主函数
main "$@"