# ShareX 非 C 盘安装完整指南

## 📋 配置信息

✅ **已完成配置**：

- **安装位置**: `F:\ShareX_Portable\`
- **录制文件保存**: `F:\ShareX\Screenshots\`
- **配置脚本**: `F:\ShareX\configure_sharex.ps1`

## 📥 下载和安装步骤

### 步骤 1：下载 ShareX 便携版

1. **打开下载页面**（已自动打开）
   - 网址：https://getsharex.com/downloads/

2. **下载便携版**
   - 找到 **"ShareX-xx.x.x-portable.zip"**
   - 点击下载（约 10 MB，比安装版小很多）

3. **保存位置**
   - 建议保存到：`F:\ShareX_Portable\`
   - 或者先保存到桌面，稍后移动

### 步骤 2：解压文件

1. **解压 ZIP 文件**
   ```
   解压到: F:\ShareX_Portable\
   ```

2. **文件结构**
   ```
   F:\ShareX_Portable\
   ├── ShareX.exe          (主程序)
   ├── ShareX_Launcher.exe
   ├── ffmpeg.exe
   └── 其他文件...
   ```

### 步骤 3：首次运行

1. **运行 ShareX**
   - 双击 `F:\ShareX_Portable\ShareX.exe`
   - 首次运行会创建配置文件

2. **允许防火墙**
   - 如果弹出防火墙提示，点击"允许访问"

### 步骤 4：配置保存路径

#### 方法 1：自动配置（推荐）

运行配置脚本：
```powershell
cd F:\ShareX
.\configure_sharex.ps1
```

#### 方法 2：手动配置

1. **打开设置**
   - 在 ShareX 主窗口，点击 `Application settings`（应用程序设置）

2. **设置路径**
   - 点击 `Paths`（路径）标签
   - 找到 `Screenshots folder`（截图文件夹）
   - 点击 `Browse...` 按钮
   - 选择：`F:\ShareX\Screenshots\`
   - 勾选 `Use custom screenshots folder`

3. **保存设置**
   - 点击 `Save` 或 `OK`

## ⌨️ 快捷键设置

### 录屏快捷键

默认快捷键：
- **Shift + Ctrl + Print Screen** - 开始/停止屏幕录制
- **Ctrl + Shift + G** - 录制 GIF

### 自定义快捷键

1. 打开 `Hotkey settings`（热键设置）
2. 找到 `Screen record` 或 `Screen record (GIF)`
3. 双击快捷键列
4. 按下你想要的快捷键组合
5. 点击 `Save`

## 🎥 开始录屏

### 快速录屏

1. **按快捷键**
   - 按 `Shift + Ctrl + Print Screen`

2. **选择录制区域**
   - 拖动鼠标选择区域
   - 或按 `Enter` 录制全屏

3. **停止录制**
   - 再次按 `Shift + Ctrl + Print Screen`
   - 或点击系统托盘的 ShareX 图标 > Stop recording

4. **查看录制文件**
   - 文件自动保存到：`F:\ShareX\Screenshots\`
   - ShareX 会自动打开文件所在文件夹

### 录制 GIF

1. 按 `Ctrl + Shift + G`
2. 选择录制区域
3. 再次按快捷键停止
4. GIF 自动生成并保存

## 📁 文件管理

### 查看录制文件

**方法 1：通过 ShareX**
- 右键点击系统托盘的 ShareX 图标
- 选择 `Open` > `Screenshots folder`

**方法 2：直接打开**
- 打开文件资源管理器
- 导航到：`F:\ShareX\Screenshots\`

### 文件命名规则

默认文件名格式：
```
ShareX_2025-12-28_16-00-00.mp4
```

可以在设置中自定义文件名格式。

## ⚙️ 高级设置

### 调整录制质量

1. **打开任务设置**
   - `Task settings` > `Screen recorder`

2. **选择录制器**
   - 推荐：`FFmpeg`（高质量）

3. **调整参数**
   - **Video codec**: x264
   - **Quality**: High (18-23)
   - **Frame rate**: 30 FPS
   - **Audio source**: 选择音频设备（如需录制声音）

### 设置自动启动

1. **开机自动运行**
   - `Application settings` > `General`
   - 勾选 `Run ShareX when Windows starts`

2. **最小化到托盘**
   - 勾选 `Start minimized to tray`

## 🔧 常见问题

### Q1: 录制的视频保存在哪里？

**答**：`F:\ShareX\Screenshots\`

你可以在 ShareX 中点击 `Open` > `Screenshots folder` 快速打开。

### Q2: 如何更改保存位置？

**答**：
1. 打开 `Application settings` > `Paths`
2. 修改 `Screenshots folder`
3. 点击 `Save`

### Q3: 快捷键不工作？

**答**：
1. 检查是否有其他软件占用了快捷键
2. 在 `Hotkey settings` 中重新设置
3. 确保 ShareX 在后台运行（系统托盘有图标）

### Q4: 录制没有声音？

**答**：
1. 打开 `Task settings` > `Screen recorder`
2. 设置 `Audio source` 为你的音频设备
3. 确保音频设备正常工作

### Q5: 如何移动到其他电脑？

**答**：
便携版的优势就是可以直接复制整个文件夹：
1. 复制 `F:\ShareX_Portable\` 到其他电脑
2. 直接运行 `ShareX.exe`
3. 所有设置都会保留

## 📊 磁盘空间管理

### 定期清理旧录制

录制文件会占用磁盘空间，建议定期清理：

1. **手动清理**
   - 打开 `F:\ShareX\Screenshots\`
   - 删除不需要的文件

2. **设置自动清理**
   - `Application settings` > `Advanced`
   - 设置 `Delete files older than X days`

### 查看占用空间

```powershell
# 在 PowerShell 中运行
$path = "F:\ShareX\Screenshots"
$size = (Get-ChildItem -Path $path -Recurse -File | Measure-Object -Property Length -Sum).Sum
$sizeMB = [math]::Round($size / 1MB, 2)
Write-Host "录制文件占用空间: $sizeMB MB"
```

## 🎯 使用技巧

### 技巧 1：快速访问

创建桌面快捷方式：
1. 右键 `F:\ShareX_Portable\ShareX.exe`
2. 选择 `发送到` > `桌面快捷方式`

### 技巧 2：录制特定窗口

1. 按录屏快捷键
2. 在弹出菜单中选择 `Window`
3. 点击要录制的窗口

### 技巧 3：添加水印

1. `Task settings` > `Image` > `Watermark`
2. 启用水印
3. 自定义文字或图片

### 技巧 4：自动上传

1. `Destinations` > 选择上传服务
2. 配置账号
3. 录制后自动上传并获取分享链接

## 📝 快速参考

### 重要路径

| 项目 | 路径 |
|------|------|
| 程序位置 | `F:\ShareX_Portable\ShareX.exe` |
| 录制文件 | `F:\ShareX\Screenshots\` |
| 配置脚本 | `F:\ShareX\configure_sharex.ps1` |

### 常用快捷键

| 功能 | 快捷键 |
|------|--------|
| 屏幕录制 | Shift + Ctrl + Print Screen |
| GIF 录制 | Ctrl + Shift + G |
| 全屏截图 | Print Screen |
| 区域截图 | Alt + Print Screen |

### 快速命令

```powershell
# 打开 ShareX
F:\ShareX_Portable\ShareX.exe

# 打开录制文件夹
explorer F:\ShareX\Screenshots\

# 运行配置脚本
F:\ShareX\configure_sharex.ps1
```

## ✅ 安装检查清单

完成以下步骤确保一切正常：

- [ ] 下载 ShareX 便携版
- [ ] 解压到 `F:\ShareX_Portable\`
- [ ] 运行 ShareX.exe
- [ ] 配置保存路径到 `F:\ShareX\Screenshots\`
- [ ] 测试录屏功能
- [ ] 检查录制文件是否保存到 F 盘
- [ ] 自定义快捷键（可选）
- [ ] 调整录制质量（可选）

---

## 🎉 完成！

现在你已经成功将 ShareX 安装到 F 盘，所有录制文件也会保存到 F 盘。

**开始录屏**：
1. 确保 ShareX 在运行（系统托盘有图标）
2. 按 `Shift + Ctrl + Print Screen`
3. 选择录制区域
4. 再次按快捷键停止
5. 文件保存在 `F:\ShareX\Screenshots\`

祝你使用愉快！🚀
