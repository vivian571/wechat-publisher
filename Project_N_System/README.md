# Project N - 智能手机自动化系统

> 基于 ADB 的手机自动化控制系统,实现智能刷视频、内容分析和决策

## ✨ 特性

- 🎬 **自动刷视频**: 模拟人类操作,自动浏览短视频
- 🧠 **智能决策**: 根据内容质量智能调整观看时长
- 📸 **视觉识别**: 截图分析,支持扩展 OCR 和 AI 识别
- 🤖 **模块化设计**: Eye-Brain-Hand 架构,易于扩展

## 🚀 快速开始

### 1. 安装 ADB 工具

参考项目文档中的 ADB 安装指南,或访问:
https://developer.android.com/tools/releases/platform-tools

### 2. 配置手机

- 开启开发者模式
- 启用 USB 调试
- USB 连接电脑并授权

### 3. 运行系统

```bash
# 测试模式
python main.py --mode test

# 自动刷视频 (10 分钟)
python main.py --mode auto

# 自定义时长 (30 分钟)
python main.py --mode auto --duration 30
```

## 📁 项目结构

```
Project_N_System/
├── main.py              # 主程序
├── skills/              # 核心模块
│   ├── hand_v2.py       # 手部操作
│   ├── eye_v2.py        # 视觉模块
│   ├── brain_v2.py      # 决策模块
│   └── video_v2.py      # 视频感知
├── configs/             # 配置文件
└── logs/                # 日志和截图
```

## 📖 文档

完整使用指南请查看项目文档。

## ⚠️ 免责声明

本项目仅供学习和研究使用,请遵守相关平台的使用条款。

## 📄 许可证

MIT License
