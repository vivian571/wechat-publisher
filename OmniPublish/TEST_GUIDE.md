# 🚀 快速测试指南 (绕过图床配置)

## ✅ 已完成的修改

1. **图床配置变为可选**: 如果没有配置 R2,系统会跳过图片处理
2. **测试文章已简化**: 移除了本地图片引用
3. **代码已优化**: 添加了完善的错误处理

## 📝 现在请执行以下步骤

### 步骤 1: 填入 API Keys

编辑 `.env` 文件,填入你的 API Keys:

```bash
# 必填 - Dev.to API Key
DEVTO_API_KEY=你的_devto_api_key

# 可选 - Hashnode (如果要测试 Hashnode)
HASHNODE_TOKEN=你的_hashnode_token
HASHNODE_PUBLICATION_ID=你的_publication_id

# 其他配置可以留空
MEDIUM_TOKEN=
R2_ACCOUNT_ID=
R2_ACCESS_KEY=
R2_SECRET_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=
CANONICAL_BASE_URL=
LOG_LEVEL=INFO
```

### 步骤 2: 测试发布到 Dev.to

```powershell
python main.py --file articles/test-article.md
```

**预期输出**:
```
🚀 OmniPublish 启动
📅 版本: 1.0.0
⚠️ R2 配置不完整,将跳过图片处理
✅ Dev.to 适配器已启用
✅ 已启用 1 个平台适配器

============================================================
📝 处理文章: test-article.md
============================================================

📝 解析文章: test-article.md
⚠️ 未配置图床,跳过图片处理 (本地图片链接可能无法在平台显示)

🚀 发布到 Dev.to...
✅ Dev.to 发布成功: https://dev.to/你的用户名/omnipublish-test-article

============================================================
📊 发布完成! 成功: 1, 失败: 0
============================================================
```

### 步骤 3: 查看发布结果

1. **访问 Dev.to**: 打开输出的 URL,查看发布的文章
2. **查看状态文件**: `cat .omnipublish/state.json`
3. **查看日志**: `cat .omnipublish/logs/publish_*.log`

## 🎯 如何获取 API Keys

### Dev.to API Key
1. 登录 Dev.to
2. 访问: https://dev.to/settings/extensions
3. 在 "DEV Community API Keys" 部分
4. 点击 "Generate API Key"
5. 输入描述 (如 "OmniPublish")
6. 复制生成的 API Key

### Hashnode Token (可选)
1. 登录 Hashnode
2. 访问: https://hashnode.com/settings/developer
3. 点击 "Generate New Token"
4. 复制 Personal Access Token
5. 获取 Publication ID:
   - 访问你的博客设置
   - 在 URL 中找到 Publication ID
   - 或者使用 GraphQL 查询获取

## ⚠️ 注意事项

1. **图片处理**: 当前跳过图片处理,所以文章中不要包含本地图片路径
2. **外链图片**: 可以使用 `https://` 开头的外链图片,这些会正常显示
3. **首次发布**: 第一次发布可能需要几秒钟,请耐心等待

## 🐛 如果遇到错误

### 错误: "❌ Dev.to API Key 无效"
- 检查 API Key 是否正确复制
- 确认 API Key 没有过期
- 重新生成一个新的 API Key

### 错误: "❌ 文章元数据验证失败"
- 检查 `test-article.md` 的 Frontmatter 格式
- 确保 `title` 和 `tags` 字段存在

### 错误: "FileNotFoundError: 配置文件不存在"
- 确认 `.env` 文件已创建
- 确认文件在项目根目录

## ✅ 测试成功后

如果 Dev.to 发布成功,你可以:
1. 继续测试 Hashnode (需要配置 Token)
2. 配置 Medium (可选)
3. 后续配置 R2 图床,支持本地图片上传

祝测试顺利! 🎉
