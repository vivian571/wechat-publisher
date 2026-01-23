# Project N 快速启动指南

## 🚀 最简单的使用方法

由于环境变量需要重启 PowerShell 才能生效,我已经为你创建了便捷的启动脚本!

### 方法 1: 使用启动脚本 (推荐)

```bash
# PowerShell 用户
.\start.ps1 --mode test          # 测试模式
.\start.ps1 --mode auto          # 自动刷视频 10 分钟
.\start.ps1 --mode auto --duration 30  # 自动刷视频 30 分钟

# CMD 用户
start.bat test                   # 测试模式
start.bat auto                   # 自动刷视频 10 分钟
start.bat auto 30                # 自动刷视频 30 分钟
```

### 方法 2: 手动配置环境变量

每次打开新的 PowerShell 时运行:

```powershell
$env:Path += ";D:\platform-tools-latest-windows\platform-tools"
python main.py --mode test
```

### 方法 3: 永久配置 (一次性设置)

**重启 PowerShell 后生效!**

1. 关闭当前所有 PowerShell 窗口
2. 重新打开 PowerShell
3. 运行: `adb version` 验证
4. 如果成功,直接运行: `python main.py --mode test`

---

## 📱 连接手机

1. 开启 USB 调试 (设置 → 开发者选项)
2. USB 连接电脑
3. 允许 USB 调试授权弹窗
4. 验证连接: `adb devices`

---

## ✅ 验证步骤

```bash
# 1. 检查 ADB
.\start.ps1  # 会显示 ADB 版本和设备列表

# 2. 运行测试
.\start.ps1 --mode test

# 3. 开始使用
.\start.ps1 --mode auto
```

---

## 💡 提示

- ✅ 启动脚本会自动配置 ADB 环境变量
- ✅ 无需手动重启 PowerShell
- ✅ 每次使用启动脚本即可

现在就试试: `.\start.ps1 --mode test` 🚀
