#!/bin/bash
# WeChat Matrix 自动发布代理启动脚本

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}WeChat Matrix 自动发布代理启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    exit 1
fi

# 检查依赖
echo -e "\n${YELLOW}📦 检查依赖...${NC}"
if ! python3 -c "import watchdog" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  watchdog 未安装，正在安装...${NC}"
    pip3 install watchdog
fi

# 检查是否已在运行
PID_FILE="agent.pid"
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  代理已在运行 (PID: $OLD_PID)${NC}"
        echo -e "${YELLOW}是否停止旧进程并重新启动？ (y/n)${NC}"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            kill "$OLD_PID"
            echo -e "${GREEN}✅ 已停止旧进程${NC}"
            sleep 2
        else
            echo -e "${YELLOW}取消启动${NC}"
            exit 0
        fi
    fi
fi

# 启动模式选择
echo -e "\n${YELLOW}请选择启动模式:${NC}"
echo "1) 前台运行（可看到实时日志）"
echo "2) 后台运行（推荐用于长期运行）"
echo "3) 测试模式（不自动发布，只监控）"
read -p "请输入选项 (1/2/3): " mode

case $mode in
    1)
        echo -e "\n${GREEN}🚀 启动前台模式...${NC}"
        echo -e "${YELLOW}按 Ctrl+C 停止${NC}\n"
        python3 auto_publish_agent.py
        ;;
    2)
        echo -e "\n${GREEN}🚀 启动后台模式...${NC}"
        nohup python3 auto_publish_agent.py > agent.log 2>&1 &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        echo -e "${GREEN}✅ 代理已启动 (PID: $NEW_PID)${NC}"
        echo -e "${YELLOW}查看日志: tail -f agent.log${NC}"
        echo -e "${YELLOW}停止代理: kill $NEW_PID${NC}"
        ;;
    3)
        echo -e "\n${GREEN}🧪 启动测试模式...${NC}"
        # 临时修改配置
        if [ -f "agent_config.json" ]; then
            cp agent_config.json agent_config.json.bak
            python3 -c "import json; c=json.load(open('agent_config.json')); c['auto_publish']=False; json.dump(c, open('agent_config.json','w'), indent=2)"
        fi
        echo -e "${YELLOW}按 Ctrl+C 停止${NC}\n"
        python3 auto_publish_agent.py
        # 恢复配置
        if [ -f "agent_config.json.bak" ]; then
            mv agent_config.json.bak agent_config.json
        fi
        ;;
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

echo -e "\n${GREEN}========================================${NC}"
