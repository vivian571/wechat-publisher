#!/bin/bash
# 一人公司：小说自动化生成流水线 (基于 OpenClaw v0.13.0)

export WORKSPACE_DIR="/Users/ax/wechat-publisher/wechat/documents/小说/连载输出"
mkdir -p "$WORKSPACE_DIR"

echo "🚀 启动 OpenClaw (Tenacity) 自动化创作流..."
echo "正在调用 scrapling 抓取趋势，并锁定目标进行创作..."

cd "/Volumes/Crucial X9/openclaw"
source venv_mythos/bin/activate

# 核心命令：加载 scrapling 技能，并通过 -z 实现静默/一次性执行，同时利用 /goal 锁定目标
hermes -s scrapling -z "/goal 结合最新的 GitHub Trending，使用 scrapling 抓取今天热榜项目信息作为素材。提取技术细节后，生成一部带有极强现实恐惧感的‘技术现实主义’科幻小说大纲和第一章正文。完成后把内容保存到 $WORKSPACE_DIR/今日生成_连载小说.md 目录下。注意：务必使用代码、命令等真实的极客元素来营造氛围。"

echo "✅ 任务结束。你可以前往 $WORKSPACE_DIR 查看最新连载内容。"
