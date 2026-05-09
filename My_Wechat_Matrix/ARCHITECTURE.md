# 🤖 自动发布代理系统架构

## 系统概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                     WeChat Matrix 自动化系统                         │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  AI 内容生成层  │ ───▶ │  自动发布代理层  │ ───▶ │  浏览器发布层   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                         │                         │
        ▼                         ▼                         ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ generator.py    │      │auto_publish_     │      │wechat_auto_     │
│ auto_matrix.py  │      │agent.py          │      │post.py          │
│                 │      │                  │      │                 │
│ • 生成文章      │      │ • 监控文件变化   │      │ • 打开浏览器    │
│ • 保存到账号    │      │ • 智能去重       │      │ • 填充内容      │
│   目录          │      │ • 自动触发发布   │      │ • 等待扫码      │
└─────────────────┘      └──────────────────┘      └─────────────────┘
        │                         │                         │
        ▼                         ▼                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          4 个公众号账号                              │
│  Account_A_CrossBorder │ Account_B_English │ Account_C_Life │       │
│  Account_D_Tech                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 工作流程详解

### 1️⃣ 文章生成阶段

```bash
# 方式 A: 单个账号生成
python generator.py --account Account_A_CrossBorder --topic "AI提示词技巧"
  ↓
保存到: accounts/Account_A_CrossBorder/output.txt

# 方式 B: 批量生成所有账号
python auto_matrix.py --once
  ↓
为每个账号生成文章并保存
```

### 2️⃣ 自动检测阶段

```
auto_publish_agent.py (持续运行)
  ↓
监控 accounts/ 目录
  ↓
检测到 output.txt 文件变化
  ↓
计算文件哈希值
  ↓
检查是否已发布（去重）
  ↓
等待 5 秒（可配置）
```

### 3️⃣ 自动发布阶段

```
调用: python wechat_auto_post.py --account Account_X
  ↓
打开浏览器（使用独立的用户数据目录）
  ↓
检查登录状态
  ├─ 已登录 → 直接进入编辑器
  └─ 未登录 → 显示二维码，等待扫码
  ↓
创建新草稿
  ↓
填充标题和正文
  ↓
上传封面图片（如果有）
  ↓
设置原创声明
  ↓
等待用户确认发布
  ↓
发布成功 → 记录哈希值 → 清理临时文件
```

## 核心组件说明

### 📄 auto_publish_agent.py

**职责**: 文件监控和发布调度

**核心功能**:
- 使用 `watchdog` 库监控文件系统
- 基于 MD5 哈希的去重机制
- 串行/并发发布模式
- 发布日志记录

**配置文件**: `agent_config.json`

```json
{
  "enabled": true,
  "auto_publish": true,
  "publish_delay_seconds": 5,
  "concurrent_publish": false,
  "published_hashes": ["abc123...", "def456..."],
  "excluded_accounts": []
}
```

### 📄 wechat_auto_post.py

**职责**: 浏览器自动化发布

**核心功能**:
- 使用 `DrissionPage` 控制浏览器
- 智能登录检测
- 内容填充和格式化
- 封面图片处理
- 原创声明设置

**独立浏览器数据**: 每个账号使用独立的 `.browser_data/Account_X/` 目录

### 📄 generator.py / auto_matrix.py

**职责**: AI 内容生成

**支持的 AI 提供商**:
- OpenAI (GPT-4, GPT-3.5)
- Gemini (Google)
- 智谱 AI (GLM-4)

## 数据流图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户操作                                  │
│  python auto_matrix.py --once                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI 生成 4 篇文章                              │
│  Account_A: "AI提示词技巧.txt"                                   │
│  Account_B: "英语学习方法.txt"                                   │
│  Account_C: "冬季养生食谱.txt"                                   │
│  Account_D: "Python装饰器.txt"                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              auto_publish_agent.py 检测到 4 个新文件             │
│  [12:00:01] 检测到: Account_A/output.txt                        │
│  [12:00:02] 检测到: Account_B/output.txt                        │
│  [12:00:03] 检测到: Account_C/output.txt                        │
│  [12:00:04] 检测到: Account_D/output.txt                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   串行发布（每个间隔 30 秒）                     │
│  [12:00:06] 发布 Account_A → 成功 ✅                            │
│  [12:00:36] 发布 Account_B → 成功 ✅                            │
│  [12:01:06] 发布 Account_C → 成功 ✅                            │
│  [12:01:36] 发布 Account_D → 成功 ✅                            │
└─────────────────────────────────────────────────────────────────┘
```

## 去重机制

```
文章内容 → MD5 哈希 → 存储到 agent_config.json
                    ↓
            下次检测到同一文件
                    ↓
            计算哈希并比对
                    ↓
            ┌───────┴───────┐
            │               │
         已存在          不存在
            │               │
         跳过发布        正常发布
```

## 容错机制

### 1. 发布失败重试

```python
# agent_config.json
{
  "retry": {
    "enabled": true,
    "max_attempts": 3,
    "delay_seconds": 60
  }
}
```

### 2. 浏览器状态恢复

每个账号使用独立的浏览器数据目录，登录状态持久化：

```
.browser_data/
├── Account_A_CrossBorder/
│   ├── Default/
│   │   ├── Cookies
│   │   └── Local Storage
├── Account_B_English/
├── Account_C_Life/
└── Account_D_Tech/
```

### 3. 日志追踪

```bash
# 代理日志
auto_publish_agent.log

# 发布脚本输出
agent.log (后台模式)
```

## 性能优化

### 并发 vs 串行

| 模式 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| 串行 | 稳定，资源占用低 | 速度较慢 | ✅ 推荐 |
| 并发 | 速度快 | 可能冲突，资源占用高 | ❌ 不推荐 |

### 资源占用

```bash
# 监控进程
ps aux | grep auto_publish_agent

# 降低优先级
nice -n 10 python auto_publish_agent.py &
```

## 安全考虑

1. **配置文件加密**: `agent_config.json` 包含已发布记录，不应提交到 Git
2. **浏览器数据隔离**: 每个账号独立的浏览器数据目录
3. **日志脱敏**: 发布日志不包含敏感信息

## 扩展性

### 添加新账号

```bash
# 1. 创建账号目录
python create_account.py

# 2. 配置提示词
vim accounts/Account_E_NewAccount/system_prompt.md

# 3. 代理自动识别并发布
# 无需修改代理代码
```

### 自定义发布逻辑

```python
# 继承 ArticlePublishAgent 类
class CustomAgent(ArticlePublishAgent):
    def _publish_article(self, account_name, file_path):
        # 自定义发布逻辑
        pass
```

## 故障恢复

### 场景 1: 代理崩溃

```bash
# 检查 PID 文件
cat agent.pid

# 重启代理
./start_agent.sh
```

### 场景 2: 发布失败

```bash
# 查看日志
tail -f auto_publish_agent.log

# 手动重试
python wechat_auto_post.py --account Account_A_CrossBorder
```

### 场景 3: 重复发布

```bash
# 重置已发布记录
python auto_publish_agent.py --reset
```

---

**设计原则**: 松耦合、高内聚、易扩展、可监控
