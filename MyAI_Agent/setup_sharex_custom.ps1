# ========================================
# ShareX 自定义安装和配置脚本
# 将软件和录制文件保存到非 C 盘
# ========================================

param(
    [string]$InstallDrive = "F:",  # 安装盘符
    [string]$SaveDrive = "F:"      # 录制文件保存盘符
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ShareX 自定义安装配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 选择安装位置
Write-Host "【1】选择安装位置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# 获取所有可用驱动器
$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 -and $_.Name -ne 'C' }

Write-Host "可用的非 C 盘驱动器:" -ForegroundColor Yellow
foreach ($drive in $drives) {
    $freeGB = [math]::Round($drive.Free / 1GB, 2)
    Write-Host "  $($drive.Name): - 可用空间: $freeGB GB" -ForegroundColor White
}
Write-Host ""

Write-Host "请选择安装盘符 (默认 F): " -ForegroundColor Green -NoNewline
$userInstallDrive = Read-Host
if (![string]::IsNullOrEmpty($userInstallDrive)) {
    $InstallDrive = $userInstallDrive.TrimEnd(':') + ":"
}

$installPath = "${InstallDrive}\Program Files\ShareX"
Write-Host "  安装路径: $installPath" -ForegroundColor Cyan
Write-Host ""

# 2. 选择录制文件保存位置
Write-Host "【2】选择录制文件保存位置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "请选择录制文件保存盘符 (默认 F): " -ForegroundColor Green -NoNewline
$userSaveDrive = Read-Host
if (![string]::IsNullOrEmpty($userSaveDrive)) {
    $SaveDrive = $userSaveDrive.TrimEnd(':') + ":"
}

$savePath = "${SaveDrive}\ShareX\Screenshots"
Write-Host "  保存路径: $savePath" -ForegroundColor Cyan
Write-Host ""

# 3. 创建保存目录
Write-Host "【3】创建保存目录" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

if (-not (Test-Path $savePath)) {
    try {
        New-Item -ItemType Directory -Path $savePath -Force | Out-Null
        Write-Host "  ✅ 已创建目录: $savePath" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ 创建目录失败: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✅ 目录已存在: $savePath" -ForegroundColor Green
}
Write-Host ""

# 4. 下载和安装 ShareX
Write-Host "【4】安装 ShareX" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "⚠️  注意事项:" -ForegroundColor Yellow
Write-Host "  1. winget 默认会安装到 C:\Program Files\" -ForegroundColor Gray
Write-Host "  2. 需要手动下载安装包才能自定义安装位置" -ForegroundColor Gray
Write-Host ""

Write-Host "选择安装方式:" -ForegroundColor Cyan
Write-Host "  1. 使用 winget 安装 (会安装到 C 盘，但可以后续移动)" -ForegroundColor White
Write-Host "  2. 手动下载安装包 (推荐，可自定义安装位置)" -ForegroundColor White
Write-Host "  3. 下载便携版 (无需安装，直接解压使用)" -ForegroundColor White
Write-Host ""

Write-Host "请选择 (1-3): " -ForegroundColor Yellow -NoNewline
$installChoice = Read-Host

switch ($installChoice) {
    "1" {
        Write-Host ""
        Write-Host "正在使用 winget 安装..." -ForegroundColor Yellow
        Write-Host "注意: 软件会安装到 C:\Program Files\ShareX\" -ForegroundColor Red
        Write-Host ""
        
        winget install ShareX.ShareX --accept-package-agreements --accept-source-agreements
        
        Write-Host ""
        Write-Host "✅ 安装完成" -ForegroundColor Green
        Write-Host "稍后我会帮你配置录制文件保存到 $SaveDrive 盘" -ForegroundColor Cyan
    }
    "2" {
        Write-Host ""
        Write-Host "正在打开 ShareX 下载页面..." -ForegroundColor Yellow
        Start-Process "https://getsharex.com/downloads/"
        
        Write-Host ""
        Write-Host "📥 下载说明:" -ForegroundColor Cyan
        Write-Host "  1. 在打开的页面下载 'ShareX-xx.x.x-setup.exe'" -ForegroundColor White
        Write-Host "  2. 运行安装程序" -ForegroundColor White
        Write-Host "  3. 在安装向导中选择安装位置为: $installPath" -ForegroundColor Yellow
        Write-Host "  4. 完成安装后，按任意键继续配置..." -ForegroundColor White
        Write-Host ""
        
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    "3" {
        Write-Host ""
        Write-Host "正在打开便携版下载页面..." -ForegroundColor Yellow
        Start-Process "https://getsharex.com/downloads/"
        
        $portablePath = "${InstallDrive}\ShareX_Portable"
        
        Write-Host ""
        Write-Host "📥 便携版说明:" -ForegroundColor Cyan
        Write-Host "  1. 在打开的页面下载 'ShareX-xx.x.x-portable.zip'" -ForegroundColor White
        Write-Host "  2. 解压到: $portablePath" -ForegroundColor Yellow
        Write-Host "  3. 运行 ShareX.exe 即可使用" -ForegroundColor White
        Write-Host "  4. 完成后，按任意键继续配置..." -ForegroundColor White
        Write-Host ""
        
        # 创建便携版目录
        if (-not (Test-Path $portablePath)) {
            New-Item -ItemType Directory -Path $portablePath -Force | Out-Null
            Write-Host "  ✅ 已创建目录: $portablePath" -ForegroundColor Green
        }
        
        Write-Host ""
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    }
    default {
        Write-Host ""
        Write-Host "已取消安装" -ForegroundColor Gray
        exit 0
    }
}

Write-Host ""
Write-Host "【5】配置 ShareX 保存路径" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# 创建 ShareX 配置文件
$configPath = "$env:USERPROFILE\Documents\ShareX\ApplicationConfig.json"

Write-Host "ShareX 安装完成后，需要手动配置保存路径:" -ForegroundColor Yellow
Write-Host ""
Write-Host "方法 1: 通过界面配置 (推荐)" -ForegroundColor Cyan
Write-Host "  1. 打开 ShareX" -ForegroundColor White
Write-Host "  2. 点击 '应用程序设置' (Application settings)" -ForegroundColor White
Write-Host "  3. 选择 '路径' (Paths) 标签" -ForegroundColor White
Write-Host "  4. 设置 '截图文件夹' 为: $savePath" -ForegroundColor Yellow
Write-Host "  5. 点击 '保存' (Save)" -ForegroundColor White
Write-Host ""

Write-Host "方法 2: 使用配置脚本 (自动)" -ForegroundColor Cyan
Write-Host "  运行 ShareX 后，我会创建一个自动配置脚本" -ForegroundColor White
Write-Host ""

# 创建配置脚本
$configScript = @"
# ShareX 自动配置脚本
# 设置保存路径到 $SaveDrive 盘

Write-Host "正在配置 ShareX..." -ForegroundColor Yellow

# ShareX 配置文件路径
`$configFile = "`$env:USERPROFILE\Documents\ShareX\ApplicationConfig.json"

if (Test-Path `$configFile) {
    try {
        # 读取配置
        `$config = Get-Content `$configFile -Raw | ConvertFrom-Json
        
        # 修改保存路径
        `$config.CustomScreenshotsPath = "$savePath"
        `$config.UseCustomScreenshotsPath = `$true
        
        # 保存配置
        `$config | ConvertTo-Json -Depth 10 | Set-Content `$configFile -Encoding UTF8
        
        Write-Host "✅ 配置完成！" -ForegroundColor Green
        Write-Host "录制文件将保存到: $savePath" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ 配置失败: `$_" -ForegroundColor Red
        Write-Host "请手动在 ShareX 中设置保存路径" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  未找到 ShareX 配置文件" -ForegroundColor Yellow
    Write-Host "请先运行 ShareX 一次，然后再运行此脚本" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
`$null = `$Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
"@

$configScriptPath = "${SaveDrive}\ShareX\configure_sharex.ps1"
$configScript | Set-Content -Path $configScriptPath -Encoding UTF8

Write-Host "✅ 已创建配置脚本: $configScriptPath" -ForegroundColor Green
Write-Host ""

# 6. 总结
Write-Host "【6】配置总结" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "📋 配置信息:" -ForegroundColor Cyan
Write-Host "  安装位置: $installPath (或 C:\Program Files\ShareX 如使用 winget)" -ForegroundColor White
Write-Host "  保存位置: $savePath" -ForegroundColor White
Write-Host "  配置脚本: $configScriptPath" -ForegroundColor White
Write-Host ""

Write-Host "📝 下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 确保 ShareX 已安装完成" -ForegroundColor White
Write-Host "  2. 运行 ShareX 一次（让它创建配置文件）" -ForegroundColor White
Write-Host "  3. 运行配置脚本: $configScriptPath" -ForegroundColor Cyan
Write-Host "     或手动在 ShareX 中设置保存路径" -ForegroundColor Gray
Write-Host ""

Write-Host "🎯 快速配置命令:" -ForegroundColor Cyan
Write-Host "  cd ${SaveDrive}\ShareX" -ForegroundColor White
Write-Host "  .\configure_sharex.ps1" -ForegroundColor White
Write-Host ""

Write-Host "是否现在打开保存文件夹？(y/n): " -ForegroundColor Yellow -NoNewline
$openFolder = Read-Host

if ($openFolder -eq 'y' -or $openFolder -eq 'Y') {
    explorer $savePath
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
