# 微信公众号草稿箱自动发布工具

这是一个自动检测指定目录中的Markdown文章，将图片上传为永久素材，然后将文章内容发布到微信公众号草稿箱的工具。

## 功能特点

- 自动扫描指定目录中的Markdown文件
- 自动提取文章标题、作者、摘要信息
- 自动上传文章中的图片为微信永久素材
- 自动选择文章封面图片
- 自动将处理后的文章发布到微信公众号草稿箱
- 支持处理单个文件或整个目录
- 支持强制重新处理已发布的文件
- 详细的日志记录

## 安装依赖

```bash
pip install requests markdown beautifulsoup4
```

## 配置说明

在使用前，需要先配置`config.json`文件，填入您的微信公众号AppID和AppSecret：

```json
{
    "app_id": "你的微信公众号AppID",
    "app_secret": "你的微信公众号AppSecret",
    "api_base_url": "https://api.weixin.qq.com",
    "processed_mark": ".published",
    "image_extensions": [".jpg", ".jpeg", ".png", ".gif"],
    "max_title_length": 64,
    "max_retry": 3,
    "retry_interval": 5
}
```

配置项说明：

- `app_id`：微信公众号的AppID
- `app_secret`：微信公众号的AppSecret
- `api_base_url`：微信API的基础URL，一般不需要修改
- `processed_mark`：已处理文件的标记后缀
- `image_extensions`：支持的图片扩展名
- `max_title_length`：标题最大字节长度
- `max_retry`：API请求失败时的最大重试次数
- `retry_interval`：重试间隔（秒）

## 使用方法

### 处理整个目录

```bash
python wechat_draft_publisher.py --dir "文章目录" --config "配置文件路径"
```

### 处理单个文件

```bash
python wechat_draft_publisher.py --file "文章文件路径" --config "配置文件路径"
```

### 强制重新处理已发布的文件

```bash
python wechat_draft_publisher.py --dir "文章目录" --force
```

## Markdown文件格式要求

为了获得最佳效果，建议您的Markdown文件遵循以下格式：

```markdown
# 文章标题

作者：作者名称

摘要：这是文章摘要，会显示在公众号文章列表中

封面：path/to/cover/image.jpg

正文内容...

![图片描述](path/to/image.jpg)

更多内容...
```

您也可以使用YAML前置元数据：

```markdown
---
title: 文章标题
author: 作者名称
summary: 这是文章摘要
cover: path/to/cover/image.jpg
---

正文内容...
```

## 工作原理

1. 扫描指定目录中的所有Markdown文件
2. 解析每个文件，提取标题、作者、摘要等信息
3. 上传文章中的图片到微信公众号永久素材库
4. 将Markdown内容转换为HTML，并替换图片链接为微信素材URL
5. 调用微信公众号API，将文章添加到草稿箱
6. 在成功发布后，创建标记文件避免重复处理

## 注意事项

- 请确保您的微信公众号有足够的API调用次数
- 图片上传有数量和大小限制，请参考微信公众号开发文档
- 文章标题长度不能超过64字节（UTF-8编码），超出会自动截断
- 程序会自动记录日志到`wechat_publisher.log`文件

## 常见问题

**Q: 如何获取微信公众号的AppID和AppSecret？**

A: 登录微信公众平台，在「开发」-「基本配置」中可以查看AppID，点击「重置」可以获取AppSecret。

**Q: 为什么上传图片失败？**

A: 可能是图片格式不支持或图片过大。微信公众号对图片有大小限制，建议压缩图片后再上传。

**Q: 如何查看发布结果？**

A: 程序会在控制台和日志文件中输出详细信息。成功发布后，可以登录微信公众平台查看草稿箱。

## 参考文档

- [微信公众号开发文档 - 添加草稿](https://developers.weixin.qq.com/doc/offiaccount/Draft_Box/Add_draft.html)
- [微信公众号开发文档 - 上传永久素材](https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html)
- [微信公众号开发文档 - 获取素材列表](https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Get_materials_list.html)
- [微信公众号开发文档 - 获取永久素材](https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Getting_Permanent_Assets.html)