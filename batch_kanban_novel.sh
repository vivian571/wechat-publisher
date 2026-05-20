#!/bin/bash
# 批量小说矩阵生成器 (基于 OpenClaw v0.13.0 Kanban 架构)

NOVEL_DIR="/Users/ax/公众号写作/小说"
OUTPUT_DIR="$NOVEL_DIR/连载输出"
mkdir -p "$OUTPUT_DIR"

cd "/Volumes/Crucial X9/openclaw"
source venv_mythos/bin/activate

echo "正在切换至专门的【公众号矩阵工厂】看板..."
hermes kanban boards switch wechat-matrix

echo "开始扫描未写的小说坑位..."

# 遍历目录
for dir in "$NOVEL_DIR"/*/; do
    dir_name=$(basename "$dir")
    
    # 排除输出目录本身
    if [ "$dir_name" == "连载输出" ]; then
        continue
    fi
    
    # 如果有 README.md (即大纲设定)
    if [ -f "$dir/README.md" ]; then
        # 检查是否已经生成过（简单判断目录下是否有多余的 md 文件，或直接盲推任务）
        echo "📌 发现待写大纲: $dir_name"
        
        TITLE="连载创作: $dir_name"
        BODY="/goal 请阅读 $dir/README.md 中的核心设定，并使用 scrapling 抓取相关领域的最新科技新闻作为灵感。你需要撰写一部硬核且具有现实恐惧感的小说大纲及第一章正文，排版后直接保存到 $OUTPUT_DIR/${dir_name}_第1章.md。注意氛围必须沉重克制。"
        
        # 将任务推送入 Kanban 队列
        hermes kanban create "$TITLE" --body "$BODY"
        echo "  ↳ 已成功派发任务给数字员工"
    fi
done

echo ""
echo "🎉 所有的催更任务已全部加入【wechat-matrix】工厂！"
echo "你可以随时输入以下命令启动你的数字打工团队进行并发创作："
echo "source venv_mythos/bin/activate && hermes gateway start"
