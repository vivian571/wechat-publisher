#!/bin/bash
# WeChat Matrix 快速演示脚本

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║        WeChat Matrix 自动化系统 - 快速演示              ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}📖 本演示将展示 3 种使用方式:${NC}"
echo ""
echo "  1️⃣  通过主 Agent (Moltbot) 使用"
echo "  2️⃣  通过 WhatsApp 使用"
echo "  3️⃣  通过 CLI 工具使用"
echo ""
echo -e "${YELLOW}按 Enter 继续...${NC}"
read

# ============================================
# 方式 1: 主 Agent
# ============================================
clear
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  方式 1: 通过主 Agent (Moltbot) 使用${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✨ 主 Agent 已集成 wechat-matrix skill${NC}"
echo ""
echo -e "${BLUE}📍 Skill 位置:${NC}"
echo "   /Users/ax/公众号写作/moltbot/.agents/skills/wechat-matrix/SKILL.md"
echo ""
echo -e "${BLUE}💬 示例对话:${NC}"
echo ""
echo -e "${YELLOW}用户:${NC} \"为 4 个公众号生成今天的文章\""
echo -e "${GREEN}Agent:${NC} 正在为所有账号生成文章..."
echo "       ✅ 已为 Account_A_CrossBorder 生成文章"
echo "       ✅ 已为 Account_B_English 生成文章"
echo "       ✅ 已为 Account_C_Life 生成文章"
echo "       ✅ 已为 Account_D_Tech 生成文章"
echo ""
echo -e "${YELLOW}用户:${NC} \"启动自动发布代理\""
echo -e "${GREEN}Agent:${NC} ✅ 自动发布代理已启动 (PID: 12345)"
echo ""
echo -e "${YELLOW}用户:${NC} \"为跨境电商账号写一篇关于 Shopee 选品的文章\""
echo -e "${GREEN}Agent:${NC} ✅ 已为 Account_A_CrossBorder 生成文章"
echo "       主题: Shopee选品技巧"
echo "       代理将在 5 秒后自动发布"
echo ""
echo -e "${BLUE}📝 可用命令:${NC}"
echo "   • 为 4 个公众号生成今天的文章"
echo "   • 启动微信公众号自动发布代理"
echo "   • 查看公众号发布状态"
echo "   • 停止发布代理"
echo "   • 为 [账号] 写一篇关于 [主题] 的文章"
echo ""
echo -e "${YELLOW}按 Enter 继续...${NC}"
read

# ============================================
# 方式 2: WhatsApp
# ============================================
clear
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  方式 2: 通过 WhatsApp 使用${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✨ WhatsApp 机器人已创建${NC}"
echo ""
echo -e "${BLUE}📍 机器人位置:${NC}"
echo "   /Users/ax/wechat-publisher/My_Wechat_Matrix/whatsapp_bot.py"
echo ""
echo -e "${BLUE}💬 示例对话:${NC}"
echo ""
echo -e "${YELLOW}你:${NC} 公众号生成全部"
echo -e "${GREEN}Bot:${NC} ✅ 已为所有 4 个账号生成文章！"
echo ""
echo -e "${YELLOW}你:${NC} 启动发布代理"
echo -e "${GREEN}Bot:${NC} ✅ 自动发布代理已启动！"
echo ""
echo -e "${YELLOW}你:${NC} 公众号生成 Account_A_CrossBorder AI提示词技巧"
echo -e "${GREEN}Bot:${NC} ✅ 已为账号 Account_A_CrossBorder 生成文章！"
echo "     主题: AI提示词技巧"
echo ""
echo -e "${YELLOW}你:${NC} 公众号状态"
echo -e "${GREEN}Bot:${NC} 📊 WeChat Matrix 状态"
echo "     ✅ 代理状态: 运行中 (PID: 12345)"
echo "     📋 最近的发布记录: ..."
echo ""
echo -e "${BLUE}📝 可用命令:${NC}"
echo "   • 公众号生成全部"
echo "   • 公众号生成 <账号名> <主题>"
echo "   • 启动发布代理"
echo "   • 停止发布代理"
echo "   • 公众号状态"
echo "   • 查看日志"
echo "   • 帮助"
echo ""
echo -e "${BLUE}🧪 测试机器人:${NC}"
echo "   cd /Users/ax/wechat-publisher/My_Wechat_Matrix"
echo "   python whatsapp_bot.py"
echo ""
echo -e "${YELLOW}按 Enter 继续...${NC}"
read

# ============================================
# 方式 3: CLI
# ============================================
clear
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  方式 3: 通过 CLI 工具使用${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}✨ CLI 工具已创建${NC}"
echo ""
echo -e "${BLUE}📍 工具位置:${NC}"
echo "   /Users/ax/wechat-publisher/My_Wechat_Matrix/scripts/wechat-matrix"
echo ""
echo -e "${BLUE}💻 示例命令:${NC}"
echo ""
echo -e "${YELLOW}\$ ./scripts/wechat-matrix generate-all${NC}"
echo "📝 正在为所有账号生成文章..."
echo "✅ 文章生成完成"
echo ""
echo -e "${YELLOW}\$ ./scripts/wechat-matrix start-agent${NC}"
echo "🚀 正在启动自动发布代理..."
echo "✅ 代理已启动 (PID: 12345)"
echo ""
echo -e "${YELLOW}\$ ./scripts/wechat-matrix status${NC}"
echo "📊 WeChat Matrix 状态"
echo "================================"
echo "✅ 代理状态: 运行中 (PID: 12345)"
echo "📋 最近的发布记录: ..."
echo "📝 待发布文章: 无"
echo ""
echo -e "${BLUE}📝 可用命令:${NC}"
echo "   • generate-all                  为所有账号生成文章"
echo "   • generate --account <name>     为指定账号生成文章"
echo "   • start-agent                   启动自动发布代理"
echo "   • stop-agent                    停止代理"
echo "   • status                        查看状态"
echo "   • logs                          查看日志"
echo "   • test                          创建测试文章"
echo "   • help                          显示帮助"
echo ""
echo -e "${YELLOW}按 Enter 继续...${NC}"
read

# ============================================
# 完整工作流程
# ============================================
clear
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  完整自动化工作流程${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}步骤 1: 启动代理${NC}"
echo "   ./scripts/wechat-matrix start-agent"
echo "   或对主 Agent 说: \"启动微信公众号自动发布代理\""
echo ""
echo -e "${BLUE}步骤 2: 生成文章${NC}"
echo "   ./scripts/wechat-matrix generate-all"
echo "   或对主 Agent 说: \"为 4 个公众号生成今天的文章\""
echo ""
echo -e "${BLUE}步骤 3: 自动发布 (无需人工干预)${NC}"
echo "   ✅ 代理检测到新文章"
echo "   ✅ 等待 5 秒"
echo "   ✅ 自动打开浏览器"
echo "   ✅ 填充文章内容"
echo "   ⏳ 等待用户扫码确认"
echo "   ✅ 发布成功"
echo "   ✅ 记录日志"
echo "   ✅ 清理临时文件"
echo ""
echo -e "${BLUE}步骤 4: 查看结果${NC}"
echo "   ./scripts/wechat-matrix status"
echo "   或对主 Agent 说: \"查看公众号发布状态\""
echo ""
echo -e "${GREEN}🎉 完全自动化！${NC}"
echo ""
echo -e "${YELLOW}按 Enter 继续...${NC}"
read

# ============================================
# 4 个账号介绍
# ============================================
clear
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo -e "${CYAN}  4 个公众号账号${NC}"
echo -e "${CYAN}═══════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}1️⃣  Account_A_CrossBorder${NC}"
echo "   📝 定位: AI 提示词教学专家"
echo "   🎨 风格: 开门见炸、案例对比、金句密集"
echo "   💡 适合: AI 提示词、ChatGPT 使用技巧"
echo ""
echo -e "${BLUE}2️⃣  Account_B_English${NC}"
echo "   📝 定位: 英语学习"
echo "   🎨 风格: 轻松活泼、互动性强"
echo "   💡 适合: 英语学习方法、口语技巧"
echo ""
echo -e "${BLUE}3️⃣  Account_C_Life${NC}"
echo "   📝 定位: 生活感悟"
echo "   🎨 风格: 温暖治愈、细腻感性"
echo "   💡 适合: 季节食材、生活感悟"
echo ""
echo -e "${BLUE}4️⃣  Account_D_Tech${NC}"
echo "   📝 定位: 编程技术"
echo "   🎨 风格: 专业深度、通俗易懂"
echo "   💡 适合: 编程教程、技术分享"
echo ""
echo -e "${YELLOW}按 Enter 继续...${NC}"
read

# ============================================
# 总结
# ============================================
clear
echo -e "${CYAN}"
cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║                    🎉 演示完成！                         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""
echo -e "${GREEN}✨ 你现在有 3 种方式控制公众号自动化:${NC}"
echo ""
echo "  1️⃣  ${BLUE}主 Agent (Moltbot)${NC} - 最方便，直接对话"
echo "      对主 Agent 说: \"为 4 个公众号生成今天的文章\""
echo ""
echo "  2️⃣  ${BLUE}WhatsApp${NC} - 远程控制，随时随地"
echo "      发送消息: \"公众号生成全部\""
echo ""
echo "  3️⃣  ${BLUE}CLI 工具${NC} - 命令行，适合脚本和自动化"
echo "      运行: ./scripts/wechat-matrix generate-all"
echo ""
echo -e "${YELLOW}📚 相关文档:${NC}"
echo "   • INTEGRATION_GUIDE.md - 集成指南"
echo "   • AUTO_PUBLISH_AGENT_GUIDE.md - 完整使用指南"
echo "   • ARCHITECTURE.md - 系统架构"
echo "   • QUICK_REFERENCE.md - 快速参考"
echo ""
echo -e "${BLUE}🚀 快速开始:${NC}"
echo "   1. cd /Users/ax/wechat-publisher/My_Wechat_Matrix"
echo "   2. ./scripts/wechat-matrix start-agent"
echo "   3. ./scripts/wechat-matrix generate-all"
echo "   4. 坐等自动发布！"
echo ""
echo -e "${GREEN}祝你使用愉快！🎊${NC}"
echo ""
