# WeChat Matrix 自动发布代理使用指南

## 📖 概述

`auto_publish_agent.py` 是一个智能的自动化子代理，用于监控 4 个公众号账号的文章生成，并在检测到新文章后自动触发网页发布流程。

## ✨ 核心功能

1. **实时监控**: 监控 `accounts/` 目录下所有账号的文章文件变化
2. **智能去重**: 基于文件哈希值，避免重复发布同一篇文章
3. **自动发布**: 检测到新文章后自动调用 `wechat_auto_post.py` 发布
4. **发布日志**: 记录所有发布操作，便于追踪和调试
5. **灵活配置**: 支持自定义发布延迟、并发模式等

## 🚀 快速开始

### 1. 安装依赖

```bash
cd My_Wechat_Matrix
pip install watchdog
```

### 2. 启动代理

```bash
# 启动自动发布代理（前台运行）
python auto_publish_agent.py

# 后台运行（macOS/Linux）
nohup python auto_publish_agent.py > agent.log 2>&1 &

# 查看后台进程
ps aux | grep auto_publish_agent
```

### 3. 生成文章并自动发布

代理启动后，只需使用现有的文章生成工具：

```bash
# 方式1: 使用 generator.py 生成单个账号文章
python generator.py --account Account_A_CrossBorder --topic "AI提示词技巧"

# 方式2: 使用 auto_matrix.py 批量生成
python auto_matrix.py --once

# 方式3: 手动创建 output.txt 文件
# 代理会自动检测并发布
```

**代理会自动检测到新文章并在 5 秒后发布！**

## 📋 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│  1. AI 生成文章 (generator.py / auto_matrix.py)            │
│     ↓                                                        │
│  2. 保存到 accounts/Account_X/output.txt                    │
│     ↓                                                        │
│  3. auto_publish_agent.py 检测到文件变化                    │
│     ↓                                                        │
│  4. 计算文件哈希，检查是否已发布                            │
│     ↓                                                        │
│  5. 等待 5 秒（可配置）                                     │
│     ↓                                                        │
│  6. 调用 wechat_auto_post.py --account Account_X            │
│     ↓                                                        │
│  7. 自动打开浏览器，填充内容，等待用户扫码                  │
│     ↓                                                        │
│  8. 发布成功，记录哈希值，写入日志                          │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ 配置说明

编辑 `agent_config.json`（首次运行会自动创建）:

```json
{
  "enabled": true,                    // 是否启用代理
  "auto_publish": true,               // 是否自动发布（false 则只监控不发布）
  "publish_delay_seconds": 5,         // 检测到文章后等待N秒再发布
  "concurrent_publish": false,        // 是否并发发布（建议 false）
  "published_hashes": [],             // 已发布文章的哈希列表（自动维护）
  "excluded_accounts": []             // 排除的账号列表，如 ["Account_C_Life"]
}
```

### 配置项详解

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enabled` | bool | true | 总开关，false 时代理不工作 |
| `auto_publish` | bool | true | 是否自动发布，false 时只监控不发布 |
| `publish_delay_seconds` | int | 5 | 检测到文章后延迟发布的秒数 |
| `concurrent_publish` | bool | false | 是否并发发布多个账号（不推荐） |
| `published_hashes` | array | [] | 已发布文章的 MD5 哈希列表 |
| `excluded_accounts` | array | [] | 不自动发布的账号名称列表 |

## 🎯 使用场景

### 场景 1: 全自动发布（推荐）

```bash
# 终端 1: 启动代理
python auto_publish_agent.py

# 终端 2: 批量生成文章
python auto_matrix.py --once

# 代理会自动依次发布所有账号的文章
```

### 场景 2: 定时生成 + 自动发布

```bash
# 使用 cron 或 launchd 定时运行生成脚本
# 代理持续运行，检测到新文章后自动发布

# macOS launchd 示例
# 创建 ~/Library/LaunchAgents/com.wechat.matrix.agent.plist
```

### 场景 3: 手动生成 + 自动发布

```bash
# 启动代理
python auto_publish_agent.py

# 手动编辑文章
vim accounts/Account_A_CrossBorder/output.txt

# 保存后代理自动发布
```

### 场景 4: 只监控不发布

```json
// agent_config.json
{
  "auto_publish": false
}
```

```bash
# 代理只监控和记录，不自动发布
python auto_publish_agent.py
```

## 📊 日志和监控

### 查看发布日志

```bash
# 实时查看日志
tail -f auto_publish_agent.log

# 查看最近 20 条记录
tail -n 20 auto_publish_agent.log

# 统计发布成功率
grep "SUCCESS" auto_publish_agent.log | wc -l
grep "FAILED" auto_publish_agent.log | wc -l
```

### 日志格式

```json
{
  "timestamp": "2026-02-17 13:30:45",
  "account": "Account_A_CrossBorder",
  "file": "/path/to/output.txt",
  "status": "SUCCESS",
  "error": ""
}
```

## 🔧 高级功能

### 重置已发布记录

如果需要重新发布已发布过的文章：

```bash
# 清空已发布记录
python auto_publish_agent.py --reset

# 或手动编辑 agent_config.json
# 将 "published_hashes": [] 设为空数组
```

### 排除特定账号

```json
// agent_config.json
{
  "excluded_accounts": ["Account_C_Life", "Account_D_Tech"]
}
```

### 调整发布延迟

```json
// agent_config.json
{
  "publish_delay_seconds": 10  // 延迟 10 秒发布
}
```

## 🐛 故障排查

### 问题 1: 代理没有检测到文章

**原因**: 
- 文件路径不正确
- 文件名不是 `output.txt` 或 `.md`
- 文件内容太短（< 100 字符）

**解决**:
```bash
# 检查文件是否存在
ls -la accounts/Account_A_CrossBorder/output.txt

# 查看代理日志
tail -f agent.log
```

### 问题 2: 重复发布同一篇文章

**原因**: 
- 已发布哈希记录丢失
- 文件内容被修改

**解决**:
```bash
# 查看已发布哈希
cat agent_config.json | grep published_hashes

# 如果确实重复，检查文件是否被修改
```

### 问题 3: 发布失败

**原因**: 
- 浏览器未登录
- 网络问题
- wechat_auto_post.py 脚本错误

**解决**:
```bash
# 手动测试发布脚本
python wechat_auto_post.py --account Account_A_CrossBorder

# 查看详细错误日志
cat auto_publish_agent.log | grep FAILED
```

## 🔐 安全建议

1. **不要提交 `agent_config.json`**: 已添加到 `.gitignore`
2. **定期备份日志**: `auto_publish_agent.log` 可能包含敏感信息
3. **限制文件权限**: 
   ```bash
   chmod 600 agent_config.json
   chmod 600 auto_publish_agent.log
   ```

## 🚀 性能优化

### 并发发布（不推荐）

虽然支持并发发布，但由于浏览器资源限制，建议使用串行模式：

```json
{
  "concurrent_publish": false  // 推荐
}
```

### 减少资源占用

```bash
# 使用 nice 降低进程优先级
nice -n 10 python auto_publish_agent.py &
```

## 📝 与现有工具的集成

### 与 auto_matrix.py 集成

```bash
# auto_matrix.py 生成文章
# auto_publish_agent.py 自动发布

# 完美配合，无需修改任何代码
```

### 与 generator.py 集成

```bash
# generator.py 生成单个账号文章
python generator.py --account Account_A_CrossBorder

# 代理自动检测并发布
```

### 与定时任务集成

```bash
# crontab 示例（每天 9:00 生成文章）
0 9 * * * cd /path/to/My_Wechat_Matrix && python auto_matrix.py --once

# 代理持续运行，检测到新文章后自动发布
```

## 🎉 最佳实践

1. **保持代理持续运行**: 使用 `nohup` 或 `systemd`/`launchd`
2. **定期检查日志**: 确保发布成功率
3. **备份配置文件**: `agent_config.json` 包含重要的去重信息
4. **测试后再启用**: 先手动测试发布流程，确认无误后再启用自动发布
5. **监控资源占用**: 使用 `top` 或 `htop` 监控进程

## 📞 支持

如有问题，请查看：
- 代理日志: `auto_publish_agent.log`
- 发布脚本日志: `wechat_auto_post.py` 的输出
- 配置文件: `agent_config.json`

---

**提示**: 首次使用建议先手动测试发布流程，确认浏览器登录状态正常后再启用自动发布！
