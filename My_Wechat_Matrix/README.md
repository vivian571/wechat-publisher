# WeChat Matrix 公众号矩阵自动化系统

一个强大的多账号公众号内容生成和发布系统，支持为不同账号生成个性化内容。

## ✨ 核心特性

- 🤖 **AI驱动**: 支持 OpenAI、Gemini 等多种AI模型
- 🎭 **多账号管理**: 每个账号独立的人设、风格和内容方向
- 🎨 **精美样式**: Mac风格代码块、微信优化的CSS样式
- 🚀 **批量生成**: 一键为所有账号生成内容
- 📝 **Markdown支持**: 自动转换为带样式的HTML

## 📁 项目结构

```
My_Wechat_Matrix/
├── accounts/                    # 账号配置目录
│   ├── Account_A_CrossBorder/   # 跨境电商账号
│   ├── Account_B_English/       # 英语学习账号
│   ├── Account_C_Life/          # 生活感悟账号
│   └── Account_D_Tech/          # 编程技术账号
├── templates/
│   └── wechat_style.css         # 微信样式模板
├── generator.py                 # 核心生成脚本
├── wechat_auto_post.py          # 自动发布工具
├── create_account.py            # 快速创建账号工具
├── matrix_config.json           # 全局配置
└── requirements.txt             # Python依赖
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd My_Wechat_Matrix
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `matrix_config.json`，填入你的AI API密钥：

```json
{
    "ai_provider": "openai",
    "api_config": {
        "openai": {
            "api_key": "your_api_key_here",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-4o"
        }
    }
}
```

### 3. 生成内容

```bash
# 为所有账号生成内容
python generator.py --all

# 为指定账号生成内容
python generator.py --account Account_A_CrossBorder

# 指定主题生成
python generator.py --account Account_A_CrossBorder --topic "Shopee选品技巧"
```

### 4. 查看生成结果

生成的HTML文件保存在各账号目录下的 `output.html`，可以：
- 在浏览器中预览
- 复制粘贴到微信公众号编辑器

### 5. 自动发布 (无需管理员权限)

系统提供 `wechat_auto_post.py` 工具，模拟浏览器操作进行发布，**无需** 微信认证或 AppID。

```bash
# 发布指定账号的内容
python wechat_auto_post.py --account Account_A_CrossBorder
```

流程说明：
1. 首次运行时会自动打开浏览器
2. 使用微信扫码登录公众号后台
3. 脚本会自动创建草稿并填充内容
4. 你只需确认无误后点击保存/发布

## 📝 创建新账号

使用交互式工具快速创建新账号：

```bash
python create_account.py
```

按提示输入账号信息，系统会自动生成配置文件。

## 🎨 自定义账号

每个账号包含3个核心文件：

### 1. `system_prompt.md` - AI人设
定义账号的角色、语气、风格等：

```markdown
# Role
你是一位资深的跨境电商卖家...

# Persona Traits
- 语气: 专业但不失亲切
- 风格: 数据驱动，案例丰富
```

### 2. `style_reference.txt` - 风格参考
粘贴2-3篇你喜欢的同类文章，AI会学习其风格。

### 3. `account_config.json` - 账号配置
```json
{
    "account_name": "跨境电商实战",
    "enabled": true,
    "preferred_topics": ["选品策略", "市场分析"],
    "target_word_count": 1800
}
```

## 🎯 使用场景

### 场景1: 每日批量生成
```bash
# 设置定时任务，每天早上9点生成所有账号的内容
python generator.py --all
```

### 场景2: 应急内容生成
```bash
# 临时需要一篇关于特定主题的文章
python generator.py --account Account_D_Tech --topic "Python装饰器详解"
```

### 场景3: A/B测试
创建多个相似账号，测试不同的内容风格和定位。

## 🔧 高级配置

### 切换AI提供商

在 `matrix_config.json` 中修改：

```json
{
    "ai_provider": "gemini",  // 或 "openai"
    "api_config": {
        "gemini": {
            "api_key": "your_gemini_key",
            "model": "gemini-2.0-flash-exp"
        }
    }
}
```

### 调整生成参数

```json
{
    "generation_settings": {
        "temperature": 0.7,    // 创造性 (0-1)
        "max_tokens": 2000     // 最大长度
    }
}
```

## 📊 账号示例

系统预置了4个示例账号：

| 账号 | 定位 | 风格 | 字数 |
|------|------|------|------|
| Account_A_CrossBorder | 跨境电商 | 数据驱动、实战经验 | 1800 |
| Account_B_English | 英语学习 | 轻松活泼、互动性强 | 1400 |
| Account_C_Life | 生活感悟 | 温暖治愈、细腻感性 | 1200 |
| Account_D_Tech | 编程技术 | 专业深度、通俗易懂 | 1600 |

## 🎨 样式特性

- ✅ Mac风格代码块（带红黄绿按钮）
- ✅ 微信公众号优化的字体和行距
- ✅ 响应式表格和图片
- ✅ 优雅的引用块和分隔线
- ✅ 代码高亮支持

## 🔐 隐私保护

**重要**: `matrix_config.json` 包含API密钥，已添加到 `.gitignore`。

如需分享项目，请：
1. 复制 `matrix_config.json` 为 `matrix_config.example.json`
2. 删除其中的真实密钥
3. 只提交示例文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可

MIT License

---

**提示**: 首次使用前，请务必编辑各账号的 `style_reference.txt`，添加真实的参考文章，这样生成的内容才会更符合预期！
