#!/bin/bash

# 微信公众号发布器 - 简易代理服务器搭建脚本
# 适用系统: Ubuntu / Debian / CentOS
# 功能: 安装 Gost 并配置 HTTP/SOCKS5 代理（带账号密码认证）

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
PLAIN='\033[0m'

echo -e "${GREEN}=== 开始搭建固定IP代理服务 ===${PLAIN}"

# 1. 检查是否为 root 用户
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}错误: 请使用 root 用户运行此脚本 (sudo bash setup_proxy.sh)${PLAIN}"
   exit 1
fi

# 2. 获取用户输入的配置信息
echo -e "${YELLOW}请设置代理账号和密码（用于保护代理不被他人滥用）${PLAIN}"
read -p "请输入用户名 (默认: wechat): " PROXY_USER
PROXY_USER=${PROXY_USER:-wechat}

read -p "请输入密码 (建议复杂一点): " PROXY_PASS
if [ -z "$PROXY_PASS" ]; then
    echo -e "${RED}错误: 密码不能为空！${PLAIN}"
    exit 1
fi

read -p "请输入端口号 (默认: 3128): " PROXY_PORT
PROXY_PORT=${PROXY_PORT:-3128}

# 3. 下载并安装 Gost (一个简单强大的代理工具)
echo -e "${GREEN}正在下载代理软件...${PLAIN}"
# 检测架构
ARCH=$(uname -m)
if [[ $ARCH == "x86_64" ]]; then
    GOST_URL="https://github.com/ginuerzh/gost/releases/download/v2.11.5/gost-linux-amd64-2.11.5.gz"
elif [[ $ARCH == "aarch64" ]]; then
    GOST_URL="https://github.com/ginuerzh/gost/releases/download/v2.11.5/gost-linux-armv8-2.11.5.gz"
else
    echo -e "${RED}不支持的架构: $ARCH${PLAIN}"
    exit 1
fi

wget -O gost.gz $GOST_URL
if [ $? -ne 0 ]; then
    echo -e "${RED}下载失败，请检查网络连接${PLAIN}"
    exit 1
fi

gzip -d gost.gz
mv gost /usr/local/bin/
chmod +x /usr/local/bin/gost

# 4. 创建系统服务 (Systemd)
echo -e "${GREEN}正在配置系统服务...${PLAIN}"

cat > /etc/systemd/system/wechat-proxy.service <<EOF
[Unit]
Description=WeChat Publisher Proxy Service
After=network.target

[Service]
Type=simple
User=root
ExecStart=/usr/local/bin/gost -L="$PROXY_USER:$PROXY_PASS@:$PROXY_PORT"
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 5. 启动服务
systemctl daemon-reload
systemctl enable wechat-proxy
systemctl restart wechat-proxy

# 6. 获取本机公网 IP
PUBLIC_IP=$(curl -s4 ifconfig.me)

# 7. 输出配置信息
echo -e ""
echo -e "${GREEN}=== 代理搭建成功！ ===${PLAIN}"
echo -e "请在您的本地电脑（运行 wechat_publisher.py 的地方）"
echo -e "修改 .env 文件，添加以下配置："
echo -e ""
echo -e "${YELLOW}WECHAT_PROXY_URL=http://${PROXY_USER}:${PROXY_PASS}@${PUBLIC_IP}:${PROXY_PORT}${PLAIN}"
echo -e ""
echo -e "注意："
echo -e "1. 请确保云服务器的防火墙/安全组已放行 TCP 端口 ${YELLOW}${PROXY_PORT}${PLAIN}"
echo -e "2. 请登录微信公众平台，将 IP ${YELLOW}${PUBLIC_IP}${PLAIN} 添加到白名单"
echo -e ""
