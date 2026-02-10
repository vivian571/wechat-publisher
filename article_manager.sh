#!/bin/bash

# 文章自动发布管理器
# 管理文章的自动转换和发布流程

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTICLES_DIR="/Users/ax/wechat-publisher/OmniPublish/articles"
VIDEO_DIR="/Users/ax/wechat-publisher/social-auto-upload/videoFile"
PYTHON_SCRIPT="/Users/ax/wechat-publisher/auto_publish_articles.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo "文章自动发布管理器"
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  convert    转换文章为视频"
    echo "  publish    转换并发布文章到所有平台"
    echo "  status     显示文章发布状态"
    echo "  list       列出所有待发布的文章"
    echo "  clean      清理已发布记录"
    echo "  help       显示帮助信息"
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

# 转换文章为视频
convert_articles() {
    echo -e "${BLUE}开始转换文章为视频...${NC}"
    
    if ! check_dependencies; then
        return 1
    fi
    
    cd "$SCRIPT_DIR"
    
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        echo -e "${RED}找不到文章转换脚本: $PYTHON_SCRIPT${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}正在运行文章转换程序...${NC}"
    python3 "$PYTHON_SCRIPT"
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}文章转换完成！${NC}"
        echo -e "${BLUE}生成的视频保存在: $VIDEO_DIR${NC}"
        
        # 显示生成的视频文件
        if [ -d "$VIDEO_DIR" ]; then
            echo -e "${YELLOW}生成的视频文件:${NC}"
            ls -la "$VIDEO_DIR"/*.mp4 2>/dev/null | head -10
        fi
    else
        echo -e "${RED}文章转换失败，退出码: $exit_code${NC}"
        return 1
    fi
}

# 转换并发布文章
publish_articles() {
    echo -e "${BLUE}开始文章转换和发布流程...${NC}"
    
    # 第一步：转换文章
    if ! convert_articles; then
        return 1
    fi
    
    # 第二步：发布生成的视频
    echo -e "${YELLOW}开始发布生成的视频...${NC}"
    
    if [ -f "$SCRIPT_DIR/video_manager.sh" ]; then
        "$SCRIPT_DIR/video_manager.sh" publish
    else
        echo -e "${RED}找不到视频发布管理器${NC}"
        echo "请手动发布视频文件:"
        echo "  cd $SCRIPT_DIR"
        echo "  ./video_manager.sh publish"
    fi
}

# 显示文章状态
show_status() {
    echo -e "${BLUE}文章发布状态${NC}"
    echo "=================================="
    
    if [ -d "$ARTICLES_DIR" ]; then
        echo -e "${YELLOW}文章目录: $ARTICLES_DIR${NC}"
        
        # 统计文章数量
        total_articles=$(find "$ARTICLES_DIR" -name "2026-*.md" | wc -l)
        echo -e "总文章数量: ${GREEN}$total_articles${NC}"
        
        # 检查已发布记录
        published_log="/Users/ax/wechat-publisher/published_articles.log"
        if [ -f "$published_log" ]; then
            published_count=$(wc -l < "$published_log")
            echo -e "已发布文章: ${GREEN}$published_count${NC}"
            
            # 显示最近发布的文章
            echo -e "${YELLOW}最近发布的文章:${NC}"
            tail -5 "$published_log" | sed 's/^/  /'
        else
            echo -e "已发布文章: ${RED}0${NC}"
        fi
        
        # 显示待发布文章
        echo -e "${YELLOW}待发布文章:${NC}"
        find "$ARTICLES_DIR" -name "2026-*.md" | head -5 | sed 's|^.*/||' | sed 's/^/  /'
        
    else
        echo -e "${RED}文章目录不存在: $ARTICLES_DIR${NC}"
    fi
    
    # 显示视频目录状态
    if [ -d "$VIDEO_DIR" ]; then
        echo -e "\n${YELLOW}视频目录: $VIDEO_DIR${NC}"
        video_count=$(find "$VIDEO_DIR" -name "*.mp4" | wc -l)
        echo -e "视频文件数量: ${GREEN}$video_count${NC}"
    fi
}

# 列出所有文章
list_articles() {
    echo -e "${BLUE}所有文章列表:${NC}"
    echo "=================================="
    
    if [ -d "$ARTICLES_DIR" ]; then
        find "$ARTICLES_DIR" -name "2026-*.md" -exec basename {} \; | sort
    else
        echo -e "${RED}文章目录不存在: $ARTICLES_DIR${NC}"
    fi
}

# 清理已发布记录
clean_published() {
    echo -e "${YELLOW}清理已发布记录...${NC}"
    
    published_log="/Users/ax/wechat-publisher/published_articles.log"
    
    if [ -f "$published_log" ]; then
        echo -e "${RED}确定要清理已发布记录吗？这将允许重新发布所有文章。${NC}"
        read -p "输入 'yes' 确认清理: " confirm
        
        if [ "$confirm" = "yes" ]; then
            rm -f "$published_log"
            echo -e "${GREEN}已清理已发布记录${NC}"
            echo "现在可以重新发布所有文章了"
        else
            echo "取消清理操作"
        fi
    else
        echo "没有找到已发布记录文件"
    fi
}

# 主函数
main() {
    case "${1:-help}" in
        "convert")
            convert_articles
            ;;
        "publish")
            publish_articles
            ;;
        "status")
            show_status
            ;;
        "list")
            list_articles
            ;;
        "clean")
            clean_published
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