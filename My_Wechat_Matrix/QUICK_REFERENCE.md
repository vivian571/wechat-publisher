# 🚀 WeChat Matrix 自动发布 - 快速参考

## 一键启动

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动自动发布代理
./start_agent.sh

# 3. 生成文章（另一个终端）
python auto_matrix.py --once

# 4. 坐等自动发布！🎉
```

## 常用命令

### 代理管理

```bash
# 启动代理（前台）
python auto_publish_agent.py

# 启动代理（后台）
nohup python auto_publish_agent.py > agent.log 2>&1 &

# 停止代理
kill $(cat agent.pid)

# 查看代理状态
ps aux | grep auto_publish_agent

# 查看实时日志
tail -f auto_publish_agent.log
```

### 文章生成

```bash
# 单个账号
python generator.py --account Account_A_CrossBorder --topic "AI提示词"

# 所有账号（一次性）
python auto_matrix.py --once

# 所有账号（循环，每60分钟）
python auto_matrix.py --interval 60

# 只生成不发布（检测模式）
python auto_matrix.py --watch
```

### 手动发布

```bash
# 发布指定账号
python wechat_auto_post.py --account Account_A_CrossBorder

# 发布所有有 output.txt 的账号
for dir in accounts/Account_*; do
  if [ -f "$dir/output.txt" ]; then
    python wechat_auto_post.py --account $(basename $dir)
  fi
done
```

### 测试和调试

```bash
# 测试代理（创建测试文章）
python test_agent.py

# 重置已发布记录
python auto_publish_agent.py --reset

# 查看配置
cat agent_config.json

# 查看发布历史
cat auto_publish_agent.log | grep SUCCESS
```

## 配置速查

### agent_config.json

```json
{
  "enabled": true,              // 总开关
  "auto_publish": true,         // 自动发布
  "publish_delay_seconds": 5,   // 延迟发布（秒）
  "concurrent_publish": false,  // 并发发布（不推荐）
  "excluded_accounts": []       // 排除账号
}
```

### matrix_config.json

```json
{
  "ai_provider": "zhipu",       // AI 提供商
  "api_config": {
    "zhipu": {
      "api_key": "your_key",
      "model": "glm-4-flash"
    }
  }
}
```

## 目录结构

```
My_Wechat_Matrix/
├── accounts/                    # 账号目录
│   ├── Account_A_CrossBorder/
│   │   ├── system_prompt.md    # AI 人设
│   │   ├── style_reference.txt # 风格参考
│   │   ├── account_config.json # 账号配置
│   │   └── output.txt          # 生成的文章（自动发布）
│   ├── Account_B_English/
│   ├── Account_C_Life/
│   └── Account_D_Tech/
├── auto_publish_agent.py       # 🤖 自动发布代理
├── wechat_auto_post.py         # 浏览器发布脚本
├── generator.py                # 单个文章生成
├── auto_matrix.py              # 批量文章生成
├── agent_config.json           # 代理配置
└── matrix_config.json          # AI 配置
```

## 工作流程

```
1. 启动代理
   ./start_agent.sh
   
2. 生成文章
   python auto_matrix.py --once
   
3. 代理检测
   [12:00:01] 检测到新文章
   
4. 自动发布
   [12:00:06] 打开浏览器
   [12:00:10] 填充内容
   [12:00:15] 等待扫码
   
5. 用户确认
   📱 扫码登录
   ✅ 确认发布
   
6. 完成
   ✅ 发布成功
   🧹 清理临时文件
```

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 代理未检测到文章 | 文件路径错误 | 检查 `accounts/Account_X/output.txt` |
| 重复发布 | 哈希记录丢失 | 查看 `agent_config.json` |
| 发布失败 | 浏览器未登录 | 手动运行 `wechat_auto_post.py` |
| 代理崩溃 | 依赖缺失 | `pip install -r requirements.txt` |

## 最佳实践

✅ **推荐做法**:
- 使用串行发布模式（`concurrent_publish: false`）
- 定期备份 `agent_config.json`
- 监控 `auto_publish_agent.log`
- 测试后再启用自动发布

❌ **避免做法**:
- 不要并发发布多个账号
- 不要删除 `published_hashes`
- 不要在代理运行时修改配置
- 不要提交 `agent_config.json` 到 Git

## 性能优化

```bash
# 降低进程优先级
nice -n 10 python auto_publish_agent.py &

# 限制内存使用（Linux）
ulimit -v 1048576  # 1GB

# 查看资源占用
top -p $(cat agent.pid)
```

## 定时任务

### macOS (launchd)

```xml
<!-- ~/Library/LaunchAgents/com.wechat.matrix.agent.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.wechat.matrix.agent</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/path/to/auto_publish_agent.py</string>
  </array>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
</dict>
</plist>
```

```bash
# 加载
launchctl load ~/Library/LaunchAgents/com.wechat.matrix.agent.plist

# 卸载
launchctl unload ~/Library/LaunchAgents/com.wechat.matrix.agent.plist
```

### Linux (systemd)

```ini
# /etc/systemd/system/wechat-matrix-agent.service
[Unit]
Description=WeChat Matrix Auto Publish Agent
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/My_Wechat_Matrix
ExecStart=/usr/bin/python3 auto_publish_agent.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 启动
sudo systemctl start wechat-matrix-agent

# 开机自启
sudo systemctl enable wechat-matrix-agent

# 查看状态
sudo systemctl status wechat-matrix-agent
```

## 高级用法

### 自定义发布延迟

```json
{
  "publish_delay_seconds": 10  // 延迟 10 秒
}
```

### 排除特定账号

```json
{
  "excluded_accounts": ["Account_C_Life"]
}
```

### 只监控不发布

```json
{
  "auto_publish": false
}
```

## 快速链接

- 📖 [完整使用指南](AUTO_PUBLISH_AGENT_GUIDE.md)
- 🏗️ [系统架构文档](ARCHITECTURE.md)
- 📝 [主 README](README.md)

---

**提示**: 首次使用请先阅读 [AUTO_PUBLISH_AGENT_GUIDE.md](AUTO_PUBLISH_AGENT_GUIDE.md)
