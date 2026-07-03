# ========================================
# Xbox Game Bar 诊断和修复工具
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Xbox Game Bar 诊断工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否是管理员
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  警告: 当前未以管理员身份运行" -ForegroundColor Yellow
    Write-Host "某些修复操作需要管理员权限" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "【1】检查系统版本" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$os = Get-CimInstance Win32_OperatingSystem
$osVersion = [System.Version]$os.Version
$osBuild = $os.BuildNumber

Write-Host "  系统: $($os.Caption)" -ForegroundColor White
Write-Host "  版本: $($os.Version)" -ForegroundColor White
Write-Host "  内部版本: $osBuild" -ForegroundColor White

# Xbox Game Bar 需要 Windows 10 1903 或更高版本
$minBuild = 18362
if ($osBuild -lt $minBuild) {
    Write-Host "  ❌ 系统版本过低，Xbox Game Bar 需要 Windows 10 1903+ (Build 18362+)" -ForegroundColor Red
    $gameBarSupported = $false
} else {
    Write-Host "  ✅ 系统版本支持 Xbox Game Bar" -ForegroundColor Green
    $gameBarSupported = $true
}
Write-Host ""

if (-not $gameBarSupported) {
    Write-Host "由于系统版本不支持，建议使用其他录屏工具。" -ForegroundColor Yellow
    Write-Host "按任意键退出..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
}

Write-Host "【2】检查 Xbox Game Bar 应用状态" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 检查 Xbox Game Bar 应用是否安装
$gameBarApp = Get-AppxPackage -Name "Microsoft.XboxGamingOverlay" -ErrorAction SilentlyContinue

if ($null -eq $gameBarApp) {
    Write-Host "  ❌ Xbox Game Bar 应用未安装" -ForegroundColor Red
    Write-Host ""
    Write-Host "是否尝试重新安装 Xbox Game Bar？(y/n): " -ForegroundColor Yellow -NoNewline
    $reinstall = Read-Host
    
    if ($reinstall -eq 'y' -or $reinstall -eq 'Y') {
        Write-Host "  正在安装 Xbox Game Bar..." -ForegroundColor Yellow
        try {
            Start-Process "ms-windows-store://pdp/?productid=9NZKPSTSNW4P"
            Write-Host "  ✅ 已打开 Microsoft Store，请手动安装 Xbox Game Bar" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ 无法打开 Microsoft Store" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  ✅ Xbox Game Bar 已安装" -ForegroundColor Green
    Write-Host "     版本: $($gameBarApp.Version)" -ForegroundColor Gray
    Write-Host "     状态: $($gameBarApp.Status)" -ForegroundColor Gray
}
Write-Host ""

Write-Host "【3】检查 Xbox Game Bar 注册表设置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 检查 Game Bar 是否启用
$gameBarEnabled = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR" -Name "AppCaptureEnabled" -ErrorAction SilentlyContinue

if ($null -eq $gameBarEnabled) {
    Write-Host "  ⚠️  未找到 GameDVR 注册表项" -ForegroundColor Yellow
    $needsEnable = $true
} elseif ($gameBarEnabled.AppCaptureEnabled -eq 0) {
    Write-Host "  ❌ Xbox Game Bar 已禁用" -ForegroundColor Red
    $needsEnable = $true
} else {
    Write-Host "  ✅ Xbox Game Bar 已启用" -ForegroundColor Green
    $needsEnable = $false
}

if ($needsEnable) {
    Write-Host ""
    Write-Host "是否启用 Xbox Game Bar？(y/n): " -ForegroundColor Yellow -NoNewline
    $enable = Read-Host
    
    if ($enable -eq 'y' -or $enable -eq 'Y') {
        try {
            # 创建或更新注册表项
            if (-not (Test-Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR")) {
                New-Item -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR" -Force | Out-Null
            }
            Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR" -Name "AppCaptureEnabled" -Value 1 -Type DWord -Force
            
            if (-not (Test-Path "HKCU:\System\GameConfigStore")) {
                New-Item -Path "HKCU:\System\GameConfigStore" -Force | Out-Null
            }
            Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 1 -Type DWord -Force
            
            Write-Host "  ✅ Xbox Game Bar 已启用" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ 启用失败: $_" -ForegroundColor Red
        }
    }
}
Write-Host ""

Write-Host "【4】检查快捷键设置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 检查快捷键是否被禁用
$gameBarHotkey = Get-ItemProperty -Path "HKCU:\Software\Microsoft\GameBar" -Name "UseNexusForGameBarEnabled" -ErrorAction SilentlyContinue

Write-Host "  默认快捷键:" -ForegroundColor White
Write-Host "    Win + G       : 打开 Game Bar" -ForegroundColor Gray
Write-Host "    Win + Alt + R : 开始/停止录制" -ForegroundColor Gray
Write-Host "    Win + Alt + G : 录制最近 30 秒" -ForegroundColor Gray
Write-Host "    Win + Alt + M : 开启/关闭麦克风" -ForegroundColor Gray
Write-Host ""

Write-Host "【5】检查后台服务" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 检查相关服务
$services = @(
    "BcastDVRUserService",
    "XblGameSave",
    "XboxGipSvc",
    "XblAuthManager"
)

foreach ($serviceName in $services) {
    $service = Get-Service -Name "${serviceName}*" -ErrorAction SilentlyContinue
    if ($null -ne $service) {
        $status = $service.Status
        $statusColor = if ($status -eq "Running") { "Green" } else { "Yellow" }
        Write-Host "  $serviceName : $status" -ForegroundColor $statusColor
    }
}
Write-Host ""

Write-Host "【6】常见问题和解决方案" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "如果快捷键仍然不工作，尝试以下方法:" -ForegroundColor Yellow
Write-Host ""
Write-Host "方法 1: 通过设置启用 Game Bar" -ForegroundColor Cyan
Write-Host "  1. 打开 Windows 设置 (Win + I)" -ForegroundColor White
Write-Host "  2. 进入 '游戏' > 'Xbox Game Bar'" -ForegroundColor White
Write-Host "  3. 确保 'Xbox Game Bar' 开关已打开" -ForegroundColor White
Write-Host "  4. 检查 '录制游戏剪辑、屏幕截图...' 开关已打开" -ForegroundColor White
Write-Host ""

Write-Host "方法 2: 重置 Xbox Game Bar 应用" -ForegroundColor Cyan
Write-Host "  1. 打开 Windows 设置 (Win + I)" -ForegroundColor White
Write-Host "  2. 进入 '应用' > '应用和功能'" -ForegroundColor White
Write-Host "  3. 搜索 'Xbox Game Bar'" -ForegroundColor White
Write-Host "  4. 点击 '高级选项' > '重置'" -ForegroundColor White
Write-Host ""

Write-Host "方法 3: 检查是否有其他软件占用快捷键" -ForegroundColor Cyan
Write-Host "  - 某些软件可能占用了 Win+G 或 Win+Alt+R" -ForegroundColor White
Write-Host "  - 尝试关闭其他软件后再试" -ForegroundColor White
Write-Host ""

Write-Host "方法 4: 手动打开 Game Bar" -ForegroundColor Cyan
Write-Host "  - 在开始菜单搜索 'Xbox Game Bar' 并打开" -ForegroundColor White
Write-Host "  - 点击录制按钮开始录制" -ForegroundColor White
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "是否打开 Windows 游戏设置？(y/n): " -ForegroundColor Yellow -NoNewline
$openSettings = Read-Host

if ($openSettings -eq 'y' -or $openSettings -eq 'Y') {
    Start-Process "ms-settings:gaming-gamebar"
    Write-Host "✅ 已打开游戏设置" -ForegroundColor Green
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "替代方案:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "如果 Xbox Game Bar 仍然无法使用，建议使用:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. ShareX (免费)" -ForegroundColor White
Write-Host "   手动下载: https://getsharex.com/" -ForegroundColor Gray
Write-Host ""
Write-Host "2. OBS Studio (免费)" -ForegroundColor White
Write-Host "   手动下载: https://obsproject.com/" -ForegroundColor Gray
Write-Host ""
Write-Host "3. 使用我创建的 PowerShell 录屏脚本" -ForegroundColor White
Write-Host "   运行: .\screen_recorder_simple.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
