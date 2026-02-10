#!/bin/bash

# 国际平台文章自动发布系统管理器
# 管理技术文章到国际平台的自动发布

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="/Users/ax/wechat-publisher/international_auto_publish.py"
ARTICLES_DIR="/Users/ax/wechat-publisher/OmniPublish/articles"
LOG_FILE="/Users/ax/wechat-publisher/international_publish.log"
PID_FILE="/Users/ax/wechat-publisher/international_publish.pid"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo "国际平台文章自动发布系统"
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start     启动自动监控和发布服务"
    echo "  stop      停止自动监控服务"
    echo "  status    显示服务状态"
    echo "  publish   立即发布所有新文章"
    echo "  test      测试发布流程"
    echo "  logs      查看运行日志"
    echo "  config    显示配置信息"
    echo "  help      显示帮助信息"
    echo ""
    echo "选项:"
    echo "  --interval N    设置检查间隔（秒），默认300"
    echo "  --platforms     指定平台（youtube,tiktok,instagram）"
}

# 检查依赖
check_dependencies() {
    local missing_deps=()
    
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi
    
    if ! command -v ffmpeg &> /dev/null; then
        missing_deps+=("ffmpeg")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}缺少依赖: ${missing_deps[*]}${NC}"
        echo "请安装缺失的依赖:"
        echo "  brew install python3 ffmpeg"
        return 1
    fi
    
    return 0
}

# 检查Python库
check_python_dependencies() {
    local python_deps=("cv2" "PIL" "numpy" "aiohttp")
    local missing_python_deps=()
    
    for dep in "${python_deps[@]}"; do
        if ! python3 -c "import $dep" 2>/dev/null; then
            missing_python_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_python_deps[@]} -ne 0 ]; then
        echo -e "${YELLOW}缺少Python依赖: ${missing_python_deps[*]}${NC}"
        echo "正在安装缺失的依赖..."
        pip3 install opencv-python pillow numpy aiohttp
    fi
}

# 获取服务状态
get_service_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            echo "running"
            return 0
        else
            echo "stopped"
            return 1
        fi
    else
        echo "stopped"
        return 1
    fi
}

# 启动服务
start_service() {
    echo -e "${BLUE}启动国际平台文章自动发布服务...${NC}"
    
    if ! check_dependencies; then
        return 1
    fi
    
    check_python_dependencies
    
    # 检查是否已在运行
    if [ "$(get_service_status)" = "running" ]; then
        echo -e "${YELLOW}服务已经在运行中${NC}"
        return 0
    fi
    
    # 获取参数
    local interval="${1:-300}"
    
    echo -e "${YELLOW}配置参数:${NC}"
    echo "  检查间隔: ${interval}秒"
    echo "  文章目录: $ARTICLES_DIR"
    echo "  日志文件: $LOG_FILE"
    
    # 启动后台进程
    nohup python3 "$PYTHON_SCRIPT" --mode monitor --interval "$interval" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    
    # 等待进程启动
    sleep 2
    
    if kill -0 "$pid" 2>/dev/null; then
        echo "$pid" > "$PID_FILE"
        echo -e "${GREEN}✅ 服务启动成功！PID: $pid${NC}"
        echo -e "${BLUE}日志文件: $LOG_FILE${NC}"
        echo -e "${YELLOW}使用 '$0 logs' 查看运行日志${NC}"
    else
        echo -e "${RED}❌ 服务启动失败，请检查日志${NC}"
        return 1
    fi
}

# 停止服务
stop_service() {
    echo -e "${BLUE}停止国际平台文章自动发布服务...${NC}"
    
    if [ "$(get_service_status)" = "stopped" ]; then
        echo -e "${YELLOW}服务未在运行${NC}"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if kill "$pid" 2>/dev/null; then
        rm -f "$PID_FILE"
        echo -e "${GREEN}✅ 服务已停止${NC}"
    else
        echo -e "${RED}❌ 停止服务失败${NC}"
        return 1
    fi
}

# 显示状态
show_status() {
    echo -e "${BLUE}国际平台文章自动发布服务状态${NC}"
    echo "======================================"
    
    local status=$(get_service_status)
    
    if [ "$status" = "running" ]; then
        local pid=$(cat "$PID_FILE")
        echo -e "服务状态: ${GREEN}运行中${NC} (PID: $pid)"
        
        # 显示最近活动
        if [ -f "$LOG_FILE" ]; then
            echo -e "${YELLOW}最近活动:${NC}"
            tail -10 "$LOG_FILE" | grep -E "(发现|处理|发布|成功|失败)" | tail -5
        fi
    else
        echo -e "服务状态: ${RED}已停止${NC}"
    fi
    
    # 显示文章状态
    if [ -d "$ARTICLES_DIR" ]; then
        echo -e "\n${YELLOW}文章状态:${NC}"
        local total_articles=$(find "$ARTICLES_DIR" -name "2026-*.md" 2>/dev/null | wc -l)
        echo "总文章数量: $total_articles"
        
        # 显示处理记录
        local processed_log="/Users/ax/wechat-publisher/international_processed.log"
        if [ -f "$processed_log" ]; then
            local processed_count=$(grep -c "success" "$processed_log" 2>/dev/null || echo "0")
            echo "成功处理: $processed_count"
        fi
    fi
    
    # 显示国际平台配置
    echo -e "\n${YELLOW}国际平台配置:${NC}"
    echo "YouTube: ✅ 启用"
    echo "TikTok: ✅ 启用" 
    echo "Instagram: ✅ 启用"
}

# 立即发布
publish_now() {
    echo -e "${BLUE}立即发布所有新文章到国际平台...${NC}"
    
    if ! check_dependencies; then
        return 1
    fi
    
    check_python_dependencies
    
    cd "$SCRIPT_DIR"
    
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        echo -e "${RED}找不到发布脚本: $PYTHON_SCRIPT${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}开始处理文章...${NC}"
    python3 "$PYTHON_SCRIPT" --mode once
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ 发布完成！${NC}"
    else
        echo -e "${RED}❌ 发布失败，退出码: $exit_code${NC}"
        echo -e "${YELLOW}查看日志: $LOG_FILE${NC}"
        return 1
    fi
}

# 测试发布流程
test_publish() {
    echo -e "${BLUE}测试国际平台发布流程...${NC}"
    
    echo -e "${YELLOW}1. 检查依赖...${NC}"
    if ! check_dependencies; then
        return 1
    fi
    
    echo -e "${YELLOW}2. 检查Python依赖...${NC}"
    check_python_dependencies
    
    echo -e "${YELLOW}3. 检查文章目录...${NC}"
    if [ ! -d "$ARTICLES_DIR" ]; then
        echo -e "${RED}文章目录不存在: $ARTICLES_DIR${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}4. 检查发布脚本...${NC}"
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        echo -e "${RED}发布脚本不存在: $PYTHON_SCRIPT${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}5. 测试文章转换...${NC}"
    # 创建测试文章
    local test_article="$ARTICLES_DIR/2026-02-08-test-international.md"
    cat > "$test_article" << 'EOF'
# [Test Article: International Platform Publishing]

![Test Image](https://images.pexels.com/photos/546819/pexels-photo-546819.jpeg)

This is a test article for international platform publishing system.

## Key Features

- Automatic article to video conversion
- Multi-platform publishing
- International audience targeting

## Technical Details

The system supports:
- YouTube publishing
- TikTok content creation
- Instagram video posts

## Conclusion

This test article demonstrates the international publishing capabilities.
EOF
    
    echo -e "${YELLOW}6. 运行测试发布...${NC}"
    cd "$SCRIPT_DIR"
    python3 "$PYTHON_SCRIPT" --mode once
    
    local exit_code=$?
    
    # 清理测试文件
    rm -f "$test_article"
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ 测试通过！系统运行正常${NC}"
    else
        echo -e "${RED}❌ 测试失败，请检查配置${NC}"
        return 1
    fi
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo -e "${BLUE}国际平台发布日志 (最近50行):${NC}"
        echo "======================================"
        tail -50 "$LOG_FILE"
    else
        echo -e "${YELLOW}日志文件不存在: $LOG_FILE${NC}"
    fi
}

# 显示配置
show_config() {
    echo -e "${BLUE}国际平台文章自动发布系统配置${NC}"
    echo "======================================"
    echo -e "${YELLOW}基本配置:${NC}"
    echo "  脚本目录: $SCRIPT_DIR"
    echo "  Python脚本: $PYTHON_SCRIPT"
    echo "  文章目录: $ARTICLES_DIR"
    echo "  日志文件: $LOG_FILE"
    echo "  PID文件: $PID_FILE"
    
    echo -e "\n${YELLOW}国际平台支持:${NC}"
    echo "  YouTube: ✅ 启用"
    echo "  TikTok: ✅ 启用"
    echo "  Instagram: ✅ 启用"
    
    echo -e "\n${YELLOW}监控配置:${NC}"
    echo "  默认检查间隔: 300秒 (5分钟)"
    echo "  最大重试次数: 3次"
    echo "  重试延迟: 60秒"
}

# 主函数
main() {
    case "${1:-help}" in
        "start")
            shift
            local interval="300"
            while [[ $# -gt 0 ]]; do
                case $1 in
                    --interval)
                        interval="$2"
                        shift 2
                        ;;
                    *)
                        shift
                        ;;
                esac
            done
            start_service "$interval"
            ;;
        "stop")
            stop_service
            ;;
        "status")
            show_status
            ;;
        "publish")
            publish_now
            ;;
        "test")
            test_publish
            ;;
        "logs")
            show_logs
            ;;
        "config")
            show_config
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}未知命令: $1${NC}"
            show_help
            return 1
            ;;
    esac
}

# 运行主函数
main "$@"