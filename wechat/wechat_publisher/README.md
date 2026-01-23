# 微信公众号自动发布工具

这是一个自动将本地 Markdown 文档发布到微信公众号草稿箱的工具。

## 功能特点

- 自动监控指定目录下的 Markdown 文件变更
- 支持 Markdown 语法转换为微信公众号格式
- 自动上传图片到微信素材库
- 支持自定义样式和配置
- 简单的命令行界面

## 安装

1. 克隆仓库或下载代码
2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 复制 `.env.example` 为 `.env` 并填写你的微信公众平台 AppID 和 AppSecret
4. 修改 `config.yaml` 文件，配置监控目录和其他选项

## 使用方法

1. 将 Markdown 文档放入 `documents` 目录
2. 运行程序：

```bash
python wechat_publisher.py
```

3. 程序会自动监控 `documents` 目录下的文件变更
4. 当检测到 `.md` 文件修改时，会自动将其发布到微信公众号草稿箱

## 文档格式要求

- 第一行作为文章标题（以 `# ` 开头）
- 支持标准的 Markdown 语法
- 图片会自动上传到微信素材库

## 配置说明

编辑 `config.yaml` 文件可以修改以下配置：

- `wechat.app_id`: 微信公众平台 AppID
- `wechat.app_secret`: 微信公众平台 AppSecret
- `paths.watch_dir`: 监控的文档目录
- `paths.image_dir`: 图片目录
- `publish.default_author`: 默认作者名称
- `publish.show_cover`: 是否显示封面图
- `watch.recursive`: 是否监控子目录
- `watch.file_types`: 监控的文件类型

## 注意事项

1. 确保你的 IP 地址已添加到微信公众平台的 IP 白名单中
2. 图片上传需要网络连接
3. 程序会定期刷新 access_token
4. 建议先在测试公众号上测试

## 许可证

MIT
