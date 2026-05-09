# Unsplash API 配置指南

## 当前状态

### ❌ 不可用的 API
- **随机图片 API**: `source.unsplash.com`
- **状态**: 已弃用，返回 503 错误
- **原因**: Unsplash 官方停止支持

### ✅ 可用的 API
- **官方 API**: `api.unsplash.com`
- **状态**: 正常工作
- **需要**: Access Key 和 Secret Key

## 配置方法

### 方法 1：使用 Pexels（当前方案，推荐）

**优势**：
- ✅ 已配置完成
- ✅ 工作稳定
- ✅ 免费额度充足

**配置**：
```env
PEXELS_API_KEY=你的Pexels密钥
```

### 方法 2：切换到 Unsplash 官方 API

**优势**：
- ✅ 图片质量高
- ✅ 图片库丰富
- ✅ 你已有 API Key

**配置**：
```env
# Unsplash API
UNSPLASH_ACCESS_KEY=z4cqLDkRry8Skq...
UNSPLASH_SECRET_KEY=T0v0asvQt_ysY6...
```

**需要修改代码**：
- 修改 `wechat_publisher.py` 中的图片获取逻辑
- 使用 `pyunsplash` 或 `requests` 调用官方 API
- 处理 API 限流（每小时 50 次请求）

## 推荐方案

### 🎯 最佳实践：混合使用

1. **封面图**：使用 Pexels（已配置）
2. **文章图片**：使用 GitHub 图片（开源智核）
3. **备用**：使用文字描述（AI流习社）

这样可以：
- ✅ 避免单一 API 失效
- ✅ 充分利用免费额度
- ✅ 提升文章质量

## 如果你想使用 Unsplash

我可以帮你：
1. 修改代码以支持 Unsplash 官方 API
2. 添加 API 限流处理
3. 实现 Pexels + Unsplash 双备份

**需要吗？** 如果需要，我会立即开始修改代码。

## 当前建议

**保持现状**：
- Pexels 用于封面图（已工作）
- GitHub 图片用于开源项目文章
- 文字描述用于其他场景

这样最稳定，也最省事！

---

**你的选择**：
1. 保持当前配置（Pexels）✅
2. 切换到 Unsplash 官方 API
3. 同时支持 Pexels + Unsplash
