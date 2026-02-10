#!/bin/bash

# WeChat Publisher 启动脚本
# 用于自动启动和管理微信公众号发布工具

SCRIPT_DIR="/Users/ax/wechat-publisher"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/wechat_publisher.pid"
CONFIG_FILE="$SCRIPT_DIR/config.ini"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 检查配置文件是否存在
if [ ! -f "$CONFIG_FILE" ]; then
    echo "错误: 配置文件 $CONFIG_FILE 不存在！"
    echo "请复制 config.example.ini 为 config.ini 并配置相关参数"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: Python3 未安装！"
    exit 1
fi

# 安装依赖
echo "正在检查依赖项..."
cd "$SCRIPT_DIR"
pip3 install -q -r requirements.txt 2>/dev/null

start_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "服务已经在运行中 (PID: $PID)"
            return 0
        fi
    fi
    
    echo "正在启动 WeChat Publisher 服务..."
    nohup python3 wechat_publisher.py > "$LOG_DIR/wechat_publisher.log" 2>&1 &
    echo $! > "$PID_FILE"
    echo "服务已启动 (PID: $!)"
}

stop_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "正在停止服务 (PID: $PID)..."
            kill "$PID"
            rm -f "$PID_FILE"
            echo "服务已停止"
        else
            echo "服务未运行"
            rm -f "$PID_FILE"
        fi
    else
        echo "服务未运行"
    fi
}

restart_service() {
    stop_service
    sleep 2
    start_service
}

status_service() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "服务正在运行 (PID: $PID)"
            echo "日志文件: $LOG_DIR/wechat_publisher.log"
        else
            echo "服务未运行 (PID文件存在但进程不存在)"
        fi
    else
        echo "服务未运行"
    fi
}

case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac