# OmniPublish 快速开始指南

## ✅ 已完成
- [x] 项目代码已创建
- [x] Python 依赖已安装

## 📝 下一步操作

### 1. 配置环境变量

复制 `.env.example` 为 `.env`:

```powershell
Copy-Item .env.example .env
```

然后编辑 `.env` 文件,填入你的 API Keys:

```bash
# 必填 - Dev.to API Key
DEVTO_API_KEY=your_devto_api_key_here

# 可选 - Hashnode (如果要发布到 Hashnode)
HASHNODE_TOKEN=your_hashnode_token_here
HASHNODE_PUBLICATION_ID=your_publication_id_here

# 可选 - Medium (如果要发布到 Medium)
MEDIUM_TOKEN=your_medium_token_here

# 必填 - Cloudflare R2 图床配置
R2_ACCOUNT_ID=your_r2_account_id
R2_ACCESS_KEY=your_r2_access_key
R2_SECRET_KEY=your_r2_secret_key
R2_BUCKET_NAME=omnipublish-assets
R2_PUBLIC_URL=https://assets.yourdomain.com

# 可选 - 主站地址 (用于 SEO)
CANONICAL_BASE_URL=https://myblog.com
```

### 2. 获取 API Keys

#### Dev.to API Key
1. 访问: https://dev.to/settings/extensions
2. 生成新的 API Key
3. 复制到 `.env` 文件的 `DEVTO_API_KEY`

#### Hashnode Token (可选)
1. 访问: https://hashnode.com/settings/developer
2. 生成 Personal Access Token
3. 复制到 `.env` 文件的 `HASHNODE_TOKEN`
4. 获取 Publication ID (在你的博客设置中)

#### Medium Token (可选)
1. 访问: https://medium.com/me/settings
2. 找到 Integration tokens
3. 生成新 Token
4. 复制到 `.env` 文件的 `MEDIUM_TOKEN`

#### Cloudflare R2 (图床)
1. 访问: https://dash.cloudflare.com/
2. 创建 R2 存储桶
3. 生成 API Token
4. 配置自定义域名 (可选,用于公共访问)

### 3. 测试发布

#### 方法 1: 使用测试文章
```powershell
python main.py --file articles/test-article.md
```

#### 方法 2: 创建自己的文章
在 `articles/` 目录创建新文章:

```markdown
---
title: "我的第一篇文章"
tags: ["test", "automation"]
published: true
description: "测试 OmniPublish"
---

# 我的第一篇文章

这是正文内容。
```

然后发布:
```powershell
python main.py --file articles/my-first-article.md
```

### 4. 查看发布结果

发布完成后,查看:
- 控制台输出 (显示发布状态和 URL)
- `.omnipublish/state.json` (发布状态记录)
- `.omnipublish/logs/` (详细日志)

### 5. 配置 GitHub Actions (可选)

如果要启用自动发布:

1. 将代码推送到 GitHub
2. 在仓库设置中添加 Secrets:
   - `DEVTO_API_KEY`
   - `HASHNODE_TOKEN`
   - `HASHNODE_PUBLICATION_ID`
   - `MEDIUM_TOKEN`
   - `R2_ACCOUNT_ID`
   - `R2_ACCESS_KEY`
   - `R2_SECRET_KEY`
   - `R2_BUCKET_NAME`
   - `R2_PUBLIC_URL`
   - `CANONICAL_BASE_URL`

3. 每次推送 `articles/*.md` 文件时,GitHub Actions 会自动发布

## 🐛 常见问题

### Q: 图片上传失败?
A: 检查 R2 配置是否正确,确保 Access Key 有写入权限

### Q: Dev.to 发布失败 (401)?
A: API Key 无效或过期,重新生成

### Q: 依赖冲突警告?
A: 可以忽略,这些是其他项目的依赖冲突,不影响 OmniPublish

## 📚 更多文档

- [技术架构文档](./01_技术架构文档.md)
- [API 集成规范](./03_API集成规范.md)
- [部署运维文档](./04_部署运维文档.md)

## 🎉 开始使用

现在你可以开始使用 OmniPublish 了!

```powershell
# 1. 配置 .env
Copy-Item .env.example .env
notepad .env  # 填入你的 API Keys

# 2. 测试发布
python main.py --file articles/test-article.md

# 3. 查看结果
cat .omnipublish/state.json
```

祝你使用愉快! 🚀
