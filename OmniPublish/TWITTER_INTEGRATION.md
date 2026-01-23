# Twitter/X 平台集成说明

## 功能特性

OmniPublish 现已支持 Twitter/X 平台的自动发布功能:

- ✅ 使用 Twitter API v2 发布推文
- ✅ 自动将长文章分割为推文线程 (最多 25 条)
- ✅ 智能分割:优先在句号、换行处分割
- ✅ 自动添加线程编号 (1/10, 2/10, ...)
- ✅ 支持代理配置
- ⚠️ 不支持编辑已发布的推文 (Twitter API 限制)

## 配置步骤

### 1. 申请 Twitter Developer Account

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. 申请开发者账号 (需要说明使用目的)
3. 创建一个新的 App

### 2. 获取 API 凭证

在 Twitter Developer Portal 中:

1. 进入你的 App 设置
2. 找到 **Keys and tokens** 页面
3. 获取以下凭证:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**

⚠️ **重要**: 确保你的 App 权限设置为 **Read and Write**,否则无法发布推文。

### 3. 配置环境变量

在 `.env` 文件中添加:

```bash
# Twitter/X API Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
```

### 4. 启用 Twitter 平台

在 `config.yaml` 中:

```yaml
platforms:
  twitter:
    enabled: true  # 改为 true
    api_key: "${TWITTER_API_KEY}"
    api_secret: "${TWITTER_API_SECRET}"
    access_token: "${TWITTER_ACCESS_TOKEN}"
    access_token_secret: "${TWITTER_ACCESS_TOKEN_SECRET}"
    priority: 4
```

### 5. 安装依赖

```bash
pip install tweepy==4.14.0
```

或者重新安装所有依赖:

```bash
pip install -r requirements.txt
```

## 使用方法

### 发布文章到 Twitter

```bash
python main.py --file articles/your-article.md
```

### 仅发布到 Twitter

在文章的 frontmatter 中指定:

```yaml
---
title: "Your Article Title"
platforms:
  - twitter
---
```

## 工作原理

### 推文线程生成

1. **第一条推文**: 包含标题 + 文章摘要 + 线程标记 (🧵 1/N 👇)
2. **后续推文**: 自动分割文章内容,每条推文最多 280 字符
3. **智能分割**: 优先在句号、换行符处分割,避免截断句子
4. **线程编号**: 自动添加 "2/N", "3/N" 等编号

### 示例

假设文章标题为 "AI 技术趋势",内容较长:

```
推文 1/5:
📝 AI 技术趋势

2026年,AI技术正在快速发展。大语言模型的能力不断提升...

🧵 1/5 👇

推文 2/5:
2/5 深度学习框架也在不断演进。PyTorch 和 TensorFlow...

推文 3/5:
3/5 AI 在各行业的应用越来越广泛...

...
```

## 限制说明

1. **推文长度**: 每条推文最多 280 字符
2. **线程长度**: 最多 25 条推文
3. **不支持编辑**: Twitter API 不支持编辑已发布的推文
4. **速率限制**: Twitter API 有速率限制,频繁发布可能被限制

## 验证配置

测试 Twitter 适配器:

```bash
cd adapters
python twitter_adapter.py
```

如果配置正确,会显示:
```
✅ Twitter API 验证成功，当前用户: @your_username
✅ TwitterAdapter 配置有效
```

## 故障排除

### 401 Unauthorized

- 检查 API Key 和 Secret 是否正确
- 确认 Access Token 和 Secret 是否正确
- 验证 App 权限是否为 "Read and Write"

### 403 Forbidden

- 检查 Twitter Developer Account 是否被暂停
- 确认 App 是否被禁用

### 429 Too Many Requests

- 触发了速率限制,等待一段时间后重试
- 考虑减少发布频率

## 最佳实践

1. **文章长度**: 建议文章不要太长,避免生成过多推文
2. **标题简洁**: 第一条推文包含标题,建议标题简短有力
3. **内容优化**: 考虑为 Twitter 优化内容,使用短句和段落
4. **测试先行**: 首次使用建议先用测试账号验证

## 相关资源

- [Twitter API v2 文档](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy 文档](https://docs.tweepy.org/)
- [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
