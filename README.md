# 微信公众号 Markdown 自动发布脚本

本脚本用于监控指定文件夹中的新 Markdown 文件，将其转换为适合微信公众号排版的 HTML 格式，并自动上传到微信公众号后台作为草稿。

## 功能

- 监控指定文件夹的新增 Markdown 文件 (.md)。
- 将 Markdown 文件内容转换为 HTML。
- （可选）根据微信公众号的样式要求对 HTML 进行优化。
- 调用微信公众号 API 将转换后的 HTML 上传为草稿。

## 配置

1.  **安装依赖**: 
    ```bash
    pip install -r requirements.txt
    ```
2.  **配置微信公众号信息**: 
    在 `config.ini` 文件（如果创建）或脚本中直接修改以下信息：
    - `APP_ID`: 你的微信公众号 AppID。
    - `APP_SECRET`: 你的微信公众号 AppSecret。
    - `IP_WHITELIST`: 允许访问API的IP地址列表，多个IP用逗号分隔。请在微信公众平台的开发配置中添加这些IP到白名单。
    - `MONITOR_FOLDER`: 需要监控的 Markdown 文件所在的文件夹路径。
    - `CHECK_INTERVAL`: 监控文件夹的检查间隔时间（秒）。

3.  **获取 Access Token**: 脚本会自动处理 Access Token 的获取和刷新。

## 使用

```bash
python main.py
```

脚本启动后将持续监控指定文件夹。当有新的 Markdown 文件保存到该文件夹时，脚本会自动处理并上传。

## 注意事项

- 确保提供的 AppID 和 AppSecret 是正确的，并且具有上传草稿的权限。
- 微信公众号的接口有调用频率限制，请合理设置 `CHECK_INTERVAL`。
- Markdown 到 HTML 的转换样式可能需要根据具体需求进行调整。
- 错误处理：脚本包含基本的错误处理，但建议根据实际情况进行完善。