# 多平台内容发布工具

一个用于将内容发布到多个平台（如微信公众号、头条号、知乎等）的自动化工具。

## 功能特点

- 支持多平台内容发布（目前已支持微信公众号）
- 监控指定目录，自动检测并发布新增或修改的Markdown文件
- 支持图片自动上传
- 灵活的配置系统，支持环境变量
- 详细的日志记录

## 安装

1. 克隆仓库：
   ```bash
   git clone https://github.com/yourusername/multi-platform-publisher.git
   cd multi-platform-publisher
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 复制示例配置文件：
   ```bash
   cp config.yaml.example config.yaml
   cp .env.example .env
   ```

4. 编辑配置文件：
   - 修改 `config.yaml` 配置发布平台和监控目录
   - 修改 `.env` 文件添加各平台的认证信息

## 使用方法

### 基本使用

```bash
# 启动监控
python main.py

# 使用自定义配置文件
python main.py --config path/to/config.yaml --env path/to/.env

# 调试模式（显示详细日志）
python main.py --debug
```

### 目录结构

```
.
├── documents/           # 监控的文档目录
│   └── 技术博客/        # 账户名对应的目录
│       └── 文章1.md
├── images/              # 图片目录
├── publishers/          # 发布器实现
│   ├── __init__.py
│   ├── base_publisher.py
│   ├── wechat_publisher.py
│   └── ...
├── utils/               # 工具类
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   └── file_utils.py
├── config.yaml          # 配置文件
├── .env                 # 环境变量
├── requirements.txt     # 依赖列表
└── README.md            # 说明文档
```

### Markdown 文件格式

Markdown 文件支持以下元数据（YAML front matter）：

```markdown
---
title: 文章标题
date: 2023-01-01
author: 作者名
description: 文章摘要
cover: cover.jpg  # 封面图片
---

# 文章标题

这里是文章内容...
```

## 配置说明

### 配置文件 (config.yaml)

```yaml
# 路径配置
paths:
  watch_dir: ./documents  # 监控的文档目录
  image_dir: ./images     # 图片目录

# 账户配置
accounts:
  技术博客:  # 账户名
    type: wechat  # 平台类型
    app_id: ${WECHAT_APP_ID}  # 从环境变量读取
    app_secret: ${WECHAT_APP_SECRET}
    author: "默认作者"

# 监控配置
watch:
  recursive: true
  file_types: [".md", ".markdown"]
```

### 环境变量 (.env)

```
# 微信公众号
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret

# 路径配置
WATCH_DIR=./documents
IMAGE_DIR=./images
```

## 开发

### 添加新平台

1. 在 `publishers/` 目录下创建新的发布器类，继承 `BasePublisher`
2. 实现必要的接口方法
3. 在 `PUBLISHER_REGISTRY` 中注册新发布器

### 运行测试

```bash
pytest
```

## 许可证

MIT

## 贡献

欢迎提交 Issue 和 Pull Request
