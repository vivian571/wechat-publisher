# WeChat Matrix 集成指南

## 🎯 两种使用方式

### 方式 1: 通过主 Agent (Moltbot) 使用

已创建 Moltbot skill，可以直接对主 Agent 说：

#### 基本命令

```
"为 4 个公众号生成今天的文章"
"启动微信公众号自动发布代理"
"为跨境电商账号写一篇关于 AI 提示词的文章"
"查看公众号发布状态"
"停止发布代理"
```

#### Skill 位置

```
/Users/ax/公众号写作/moltbot/.agents/skills/wechat-matrix/SKILL.md
```

主 Agent 会自动识别这个 skill 并在需要时使用。

### 方式 2: 通过 WhatsApp 使用

已创建 WhatsApp 集成机器人，可以通过 WhatsApp 消息控制：

#### 可用命令

```
公众号生成全部
公众号生成 Account_A_CrossBorder AI提示词技巧
启动发布代理
停止发布代理
公众号状态
查看日志
帮助
```

#### 测试 WhatsApp 机器人

```bash
cd /Users/ax/wechat-publisher/My_Wechat_Matrix
python whatsapp_bot.py
```

然后输入测试消息，例如：
```
>>> 公众号生成全部
>>> 公众号状态
>>> 帮助
```

## 🚀 快速开始

### 1. 首次设置

```bash
# 进入项目目录
cd /Users/ax/wechat-publisher/My_Wechat_Matrix

# 安装依赖（如果还没安装）
pip install -r requirements.txt

# 配置 AI API 密钥
# 编辑 matrix_config.json，填入你的 API 密钥
```

### 2. 启动自动发布代理

**方式 A: 通过主 Agent**
```
对主 Agent 说: "启动微信公众号自动发布代理"
```

**方式 B: 通过 WhatsApp**
```
发送消息: "启动发布代理"
```

**方式 C: 直接命令行**
```bash
cd /Users/ax/wechat-publisher/My_Wechat_Matrix
./scripts/wechat-matrix start-agent
```

### 3. 生成文章

**方式 A: 通过主 Agent**
```
对主 Agent 说: "为 4 个公众号生成今天的文章"
```

**方式 B: 通过 WhatsApp**
```
发送消息: "公众号生成全部"
```

**方式 C: 直接命令行**
```bash
./scripts/wechat-matrix generate-all
```

### 4. 查看状态

**方式 A: 通过主 Agent**
```
对主 Agent 说: "查看公众号发布状态"
```

**方式 B: 通过 WhatsApp**
```
发送消息: "公众号状态"
```

**方式 C: 直接命令行**
```bash
./scripts/wechat-matrix status
```

## 📋 CLI 工具使用

已创建统一的 CLI 工具: `scripts/wechat-matrix`

### 可用命令

```bash
# 生成文章
./scripts/wechat-matrix generate-all
./scripts/wechat-matrix generate --account Account_A_CrossBorder --topic "AI提示词"

# 代理管理
./scripts/wechat-matrix start-agent
./scripts/wechat-matrix stop-agent
./scripts/wechat-matrix restart-agent

# 查看信息
./scripts/wechat-matrix status
./scripts/wechat-matrix logs

# 其他
./scripts/wechat-matrix test
./scripts/wechat-matrix reset
./scripts/wechat-matrix help
```

## 🔗 集成到主 Agent

主 Agent (Moltbot) 已经可以识别 WeChat Matrix skill。

### 示例对话

**用户**: "为 4 个公众号生成今天的文章"

**主 Agent**:
1. 识别到 wechat-matrix skill
2. 执行 `generate-all` 命令
3. 等待生成完成
4. 报告结果

**用户**: "为跨境电商账号写一篇关于 Shopee 选品的文章"

**主 Agent**:
1. 识别账号: Account_A_CrossBorder
2. 执行 `generate --account Account_A_CrossBorder --topic "Shopee选品技巧"`
3. 等待生成完成
4. 如果代理在运行，文章会自动发布

## 🎭 4 个账号说明

1. **Account_A_CrossBorder** - AI 提示词教学专家
   - 风格：开门见炸、案例对比、金句密集
   - 适合主题：AI 提示词、ChatGPT 使用技巧

2. **Account_B_English** - 英语学习
   - 风格：轻松活泼、互动性强
   - 适合主题：英语学习方法、口语技巧

3. **Account_C_Life** - 生活感悟
   - 风格：温暖治愈、细腻感性
   - 适合主题：季节食材、生活感悟

4. **Account_D_Tech** - 编程技术
   - 风格：专业深度、通俗易懂
   - 适合主题：编程教程、技术分享

## 🔧 配置文件

### matrix_config.json (AI 配置)

```json
{
  "ai_provider": "zhipu",
  "api_config": {
    "zhipu": {
      "api_key": "your_key_here",
      "model": "glm-4-flash"
    }
  }
}
```

### agent_config.json (代理配置)

```json
{
  "enabled": true,
  "auto_publish": true,
  "publish_delay_seconds": 5,
  "concurrent_publish": false,
  "excluded_accounts": []
}
```

## 📊 工作流程

```
用户请求 (主 Agent / WhatsApp / CLI)
    ↓
AI 生成文章 (generator.py / auto_matrix.py)
    ↓
保存到 accounts/Account_X/output.txt
    ↓
自动发布代理检测到文件变化
    ↓
等待 5 秒
    ↓
调用 wechat_auto_post.py
    ↓
打开浏览器，填充内容
    ↓
等待用户扫码确认
    ↓
发布成功，记录日志
```

## 🐛 故障排查

### 主 Agent 无法识别 skill

检查 skill 文件是否存在：
```bash
ls -la /Users/ax/公众号写作/moltbot/.agents/skills/wechat-matrix/SKILL.md
```

### WhatsApp 机器人无响应

测试机器人：
```bash
cd /Users/ax/wechat-publisher/My_Wechat_Matrix
python whatsapp_bot.py
```

### 代理未启动

手动启动：
```bash
cd /Users/ax/wechat-publisher/My_Wechat_Matrix
./scripts/wechat-matrix start-agent
```

## 📚 相关文档

- [完整使用指南](AUTO_PUBLISH_AGENT_GUIDE.md)
- [系统架构](ARCHITECTURE.md)
- [快速参考](QUICK_REFERENCE.md)
- [Moltbot Skill](file:///Users/ax/公众号写作/moltbot/.agents/skills/wechat-matrix/SKILL.md)

## 🎉 总结

现在你有 **3 种方式** 控制公众号文章生成和发布：

1. **主 Agent (Moltbot)** - 最方便，直接对话
2. **WhatsApp** - 远程控制，随时随地
3. **CLI 工具** - 命令行，适合脚本和自动化

所有方式都会触发相同的自动化流程，选择最适合你的方式即可！
