#!/bin/bash

# 定义颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}      Mac GitHub 一键配置助手 v1.0       ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 1. 获取用户信息
echo ""
echo -e "请按照提示输入信息："
read -p "1. 请输入你的 GitHub 用户名 (User Name): " git_user
read -p "2. 请输入你的 GitHub 邮箱 (Email): " git_email

if [ -z "$git_user" ] || [ -z "$git_email" ]; then
    echo -e "${RED}错误：用户名或邮箱不能为空！请重新运行脚本。${NC}"
    exit 1
fi

# 2. 配置 Git 全局信息
echo ""
echo -e "${GREEN}正在配置 Git 全局信息...${NC}"
git config --global user.name "$git_user"
git config --global user.email "$git_email"
echo "Git 用户名已设置为: $git_user"
echo "Git 邮箱已设置为: $git_email"

# 3. 生成 SSH 密钥
echo ""
echo -e "${GREEN}正在检查 SSH 密钥...${NC}"
SSH_KEY_PATH="$HOME/.ssh/id_ed25519"

if [ -f "$SSH_KEY_PATH" ]; then
    echo -e "${BLUE}检测到已存在 SSH 密钥，跳过生成步骤。${NC}"
else
    echo -e "正在生成新的 SSH 密钥（算法：ed25519）..."
    # -N "" 表示空密码，-f 指定路径
    ssh-keygen -t ed25519 -C "$git_email" -f "$SSH_KEY_PATH" -N ""
    echo -e "${GREEN}SSH 密钥生成成功！${NC}"
fi

# 4. 自动复制到剪切板
echo ""
echo -e "${GREEN}正在读取公钥...${NC}"
if [ -f "$SSH_KEY_PATH.pub" ]; then
    cat "$SSH_KEY_PATH.pub" | pbcopy
    echo -e "${BLUE}★★★★★ 成功！公钥已自动复制到你的剪切板！ ★★★★★${NC}"
else
    echo -e "${RED}错误：未找到公钥文件，请检查生成步骤。${NC}"
    exit 1
fi

# 5. 打开 GitHub 网页并提示
echo ""
echo -e "${BLUE}>>> 下一步操作指南 <<<${NC}"
echo "1. 脚本将自动为您打开 GitHub SSH 设置页面..."
echo "2. 点击页面上的绿色按钮 'New SSH key'"
echo "3. 在 'Title' 栏输入：MacBook"
echo "4. 在 'Key' 栏直接按下 'Command + V' (粘贴)"
echo "5. 点击 'Add SSH key' 保存"
echo ""
read -p "按回车键打开浏览器并继续..."

# 打开网页
open "https://github.com/settings/ssh/new"

echo ""
echo -e "${BLUE}>>> 最后的验证 <<<${NC}"
read -p "在网页上添加完成后，请回到这里按回车键进行连接测试..."

echo ""
echo -e "正在尝试连接 GitHub..."
ssh -T git@github.com

echo ""
echo -e "${GREEN}脚本运行结束。如果上面显示 'Hi $git_user! ...' 则表示配置成功！${NC}"
