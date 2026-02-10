#!/bin/bash

# 智能Git自动同步脚本
# 支持自动提交、推送、错误处理和日志记录

set -euo pipefail

# 配置
PROJECTS=(
    "/Users/ax/wechat-publisher"
    "/Users/ax/wechat-publisher/social-auto-upload"
)

LOG_FILE="/Users/ax/wechat-publisher/git_sync.log"
MAX_LOG_SIZE=10485760  # 10MB

# 颜色配置
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${GREEN}[$timestamp] [INFO]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] [WARN]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] [ERROR]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "DEBUG")
            echo -e "${BLUE}[$timestamp] [DEBUG]${NC} $message" >> "$LOG_FILE"
            ;;
    esac
}

# 检查日志文件大小并轮转
rotate_log() {
    if [[ -f "$LOG_FILE" ]] && [[ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt $MAX_LOG_SIZE ]]; then
        mv "$LOG_FILE" "${LOG_FILE}.old"
        log "INFO" "日志文件已轮转"
    fi
}

# 获取当前分支
get_current_branch() {
    git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"
}

# 检查是否有未提交的更改
has_changes() {
    [[ -n $(git status --porcelain 2>/dev/null) ]]
}

# 检查是否有未推送的提交
has_unpushed_commits() {
    local branch=$(get_current_branch)
    [[ -n "$(git rev-list origin/$branch..HEAD 2>/dev/null)" ]]
}

# 同步单个项目的函数
sync_project() {
    local project_path="$1"
    local project_name=$(basename "$project_path")
    
    log "INFO" "开始同步项目: $project_name"
    
    cd "$project_path"
    
    # 获取当前分支
    local current_branch=$(get_current_branch)
    log "DEBUG" "当前分支: $current_branch"
    
    # 检查是否是Git仓库
    if [[ ! -d ".git" ]]; then
        log "WARN" "$project_name 不是Git仓库，跳过"
        return 1
    fi
    
    # 检查远程仓库
    if ! git remote get-url origin >/dev/null 2>&1; then
        log "WARN" "$project_name 没有配置远程仓库，跳过"
        return 1
    fi
    
    # 获取远程更新
    log "DEBUG" "获取远程更新..."
    git fetch origin 2>/dev/null || {
        log "WARN" "无法获取远程更新，继续本地操作"
    }
    
    local changes_made=false
    
    # 处理未提交的更改
    if has_changes; then
        log "INFO" "检测到未提交的更改"
        
        # 获取更改统计
        local changes=$(git diff --stat 2>/dev/null || echo "文件更改")
        local untracked=$(git ls-files --others --exclude-standard | wc -l)
        
        # 添加所有更改
        git add -A
        
        # 创建提交信息
        local commit_msg="自动同步: $(date '+%Y-%m-%d %H:%M:%S')\n\n"
        commit_msg+="更改统计:\n$changes\n"
        [[ $untracked -gt 0 ]] && commit_msg+="\n新增文件: $untracked 个"
        
        # 提交更改
        if git commit -m "$commit_msg"; then
            log "INFO" "更改已提交"
            changes_made=true
        else
            log "ERROR" "提交失败"
            return 1
        fi
    fi
    
    # 检查是否有未推送的提交
    if has_unpushed_commits; then
        log "INFO" "检测到未推送的提交"
        
        # 推送到远程仓库
        if git push origin "$current_branch"; then
            log "INFO" "提交已推送到远程仓库"
            changes_made=true
        else
            log "ERROR" "推送失败"
            return 1
        fi
    fi
    
    if [[ "$changes_made" == true ]]; then
        log "INFO" "项目 $project_name 同步完成 ✓"
    else
        log "INFO" "项目 $project_name 没有需要同步的更改"
    fi
}

# 显示同步统计
show_sync_stats() {
    local total_projects="${#PROJECTS[@]}"
    local successful_syncs=0
    
    for project in "${PROJECTS[@]}"; do
        if [[ -d "$project/.git" ]]; then
            ((successful_syncs++))
        fi
    done
    
    log "INFO" "同步统计: $successful_syncs/$total_projects 个项目已同步"
}

# 主函数
main() {
    log "INFO" "=== 开始智能Git自动同步 ==="
    
    # 轮转日志文件
    rotate_log
    
    # 检查网络连接
    if ! ping -c 1 github.com >/dev/null 2>&1; then
        log "WARN" "网络连接可能有问题，继续尝试同步..."
    fi
    
    local sync_success=true
    
    for project in "${PROJECTS[@]}"; do
        if [[ -d "$project" ]]; then
            if ! sync_project "$project"; then
                sync_success=false
            fi
        else
            log "WARN" "项目路径不存在: $project"
        fi
    done
    
    # 显示统计信息
    show_sync_stats
    
    if [[ "$sync_success" == true ]]; then
        log "INFO" "=== 自动Git同步完成 ✓ ==="
    else
        log "ERROR" "=== 自动Git同步完成，但有错误发生 ✗ ==="
        return 1
    fi
}

# 处理脚本参数
case "${1:-}" in
    "--help"|"-h")
        echo "用法: $0 [选项]"
        echo "选项:"
        echo "  --help, -h     显示帮助信息"
        echo "  --version, -v  显示版本信息"
        echo "  --dry-run      模拟运行，不执行实际同步"
        exit 0
        ;;
    "--version"|"-v")
        echo "智能Git自动同步脚本 v1.0"
        exit 0
        ;;
    "--dry-run")
        echo "模拟运行模式 - 不执行实际同步"
        # 这里可以添加模拟逻辑
        exit 0
        ;;
esac

# 运行主函数
main "$@"