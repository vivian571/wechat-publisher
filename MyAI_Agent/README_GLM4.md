# Open Interpreter GLM-4 配置指南

## 快速启动

### 方法 1：使用启动脚本（推荐）

```powershell
# 在 PowerShell 中运行
.\start_interpreter.ps1
```

脚本会自动：
- 激活虚拟环境
- 检查 API Key
- 提供两种启动方式选择

### 方法 2：手动启动

#### 2.1 使用 Profile 文件

```powershell
# 1. 激活虚拟环境
.\venv\Scripts\activate

# 2. 设置 API Key（如果还没设置）
$env:GLM_API_KEY = "your-glm-4-api-key-here"

# 3. 启动 interpreter
interpreter --profile glm4.yaml
```

#### 2.2 使用命令行参数

```powershell
# 1. 激活虚拟环境
.\venv\Scripts\activate

# 2. 直接启动
interpreter `
  --model "glm-4" `
  --api_base "https://open.bigmodel.cn/api/paas/v4/" `
  --api_key "your-glm-4-api-key-here" `
  --context_window 128000 `
  --max_tokens 1000
```

## 配置说明

### glm4.yaml 配置文件

```yaml
model: "glm-4"                                      # 模型名称
api_base: "https://open.bigmodel.cn/api/paas/v4/"  # 智谱 API 地址
api_key: ""                                         # API Key（建议用环境变量）
context_window: 128000                              # 上下文窗口大小
max_tokens: 1000                                    # 最大输出 token 数
auto_run: false                                     # 是否自动运行代码
safe_mode: "ask"                                    # 安全模式：ask/auto/off
temperature: 0.7                                    # 温度参数
```

## 获取 API Key

1. 访问智谱 AI 开放平台：https://open.bigmodel.cn/
2. 注册/登录账号
3. 在控制台创建 API Key
4. 复制 API Key 并设置到环境变量

## 环境变量设置

### 临时设置（当前会话）

```powershell
$env:GLM_API_KEY = "your-api-key-here"
```

### 永久设置（推荐）

```powershell
# 添加到用户环境变量
[System.Environment]::SetEnvironmentVariable('GLM_API_KEY', 'your-api-key-here', 'User')
```

## 常见问题

### Q: 提示 "Unrecognized argument(s): ['--config_file']"
A: Open Interpreter 不支持 `--config_file` 参数，请使用 `--profile` 参数。

### Q: 如何验证配置是否正确？
A: 启动后，interpreter 会显示当前使用的模型和配置信息。

### Q: 可以使用其他模型吗？
A: 可以，修改 `glm4.yaml` 中的 `model` 字段，或使用不同的 profile 文件。

## 使用示例

启动后，你可以直接与 AI 对话：

```
> 帮我写一个 Python 脚本，读取 CSV 文件并生成统计报告

> 分析这个项目的代码结构

> 帮我调试这段代码的错误
```

Open Interpreter 会自动执行代码并返回结果。

## 注意事项

1. **API Key 安全**：不要将 API Key 直接写入配置文件并提交到 Git
2. **Token 消耗**：注意监控 API 调用量，避免超出配额
3. **安全模式**：建议保持 `safe_mode: "ask"`，避免自动执行危险代码
