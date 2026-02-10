#!/bin/bash

# WeChat Publisher 自动启动安装脚本 (macOS)
# 这个脚本会将服务设置为开机自动启动

SCRIPT_DIR="/Users/ax/wechat-publisher"
PLIST_NAME="com.wechat.publisher.plist"
PLIST_SOURCE="$SCRIPT_DIR/$PLIST_NAME"
PLIST_DEST="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== WeChat Publisher 自动启动设置 ==="

# 检查配置文件是否存在
if [ ! -f "$SCRIPT_DIR/config.ini" ]; then
    echo "错误: 配置文件 config.ini 不存在！"
    echo "请复制 config.example.ini 为 config.ini 并配置相关参数"
    exit 1
fi

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"

# 复制plist文件到LaunchAgents目录
echo "正在安装启动配置..."
cp "$PLIST_SOURCE" "$PLIST_DEST"

# 加载服务
echo "正在加载服务..."
launchctl load "$PLIST_DEST"

# 立即启动服务
echo "正在启动服务..."
launchctl start com.wechat.publisher

# 检查服务状态
echo ""
echo "=== 服务状态 ==="
if launchctl list | grep -q "com.wechat.publisher"; then
    echo "✅ 服务已成功安装并启动！"
    echo "日志文件位置: $SCRIPT_DIR/logs/wechat_publisher.log"
    echo "错误日志: $SCRIPT_DIR/logs/wechat_publisher_error.log"
else
    echo "❌ 服务安装失败，请检查日志文件"
fi

echo ""
echo "=== 管理命令 ==="
echo "查看服务状态: launchctl list | grep com.wechat.publisher"
echo "停止服务: launchctl stop com.wechat.publisher"
echo "启动服务: launchctl start com.wechat.publisher"
echo "卸载服务: launchctl unload $PLIST_DEST"
echo "查看日志: tail -f $SCRIPT_DIR/logs/wechat_publisher.log"

echo ""
echo "安装完成！服务将在系统启动时自动运行。"