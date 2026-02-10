#!/bin/bash
echo "🎬 Starting Viral Video Machine Engine..."
echo "📂 Watch Folder: /Users/ax/wechat-publisher/video_tasks"
echo "📂 Output Folder: /Users/ax/wechat-publisher/social-auto-upload/videoFile"
echo "---------------------------------------------------"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found!"
    exit 1
fi

# Run the watcher
cd /Users/ax/wechat-publisher
python3 video_watcher.py
