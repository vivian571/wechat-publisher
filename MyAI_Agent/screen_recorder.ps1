# ========================================
# Windows 屏幕录制脚本
# 使用 Windows 内置的 Xbox Game Bar 功能
# ========================================

param(
    [int]$Duration = 10,  # 录制时长（秒）
    [string]$OutputPath = "$env:USERPROFILE\Desktop\ScreenRecording_$(Get-Date -Format 'yyyyMMdd_HHmmss').mp4"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows 屏幕录制工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Xbox Game Bar 是否可用
$gameBarEnabled = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR" -Name "AppCaptureEnabled" -ErrorAction SilentlyContinue

if ($null -eq $gameBarEnabled -or $gameBarEnabled.AppCaptureEnabled -eq 0) {
    Write-Host "⚠️  Xbox Game Bar 未启用" -ForegroundColor Yellow
    Write-Host "正在启用 Xbox Game Bar..." -ForegroundColor Yellow
    
    # 启用 Game Bar
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\GameDVR" -Name "AppCaptureEnabled" -Value 1 -Force
    Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 1 -Force -ErrorAction SilentlyContinue
}

Write-Host "📹 录制设置:" -ForegroundColor Green
Write-Host "   时长: $Duration 秒" -ForegroundColor White
Write-Host "   输出: $OutputPath" -ForegroundColor White
Write-Host ""

Write-Host "⏱️  准备录制..." -ForegroundColor Yellow
Write-Host "提示: 使用 Win+G 可以手动打开 Xbox Game Bar" -ForegroundColor Gray
Write-Host "      使用 Win+Alt+R 可以手动开始/停止录制" -ForegroundColor Gray
Write-Host ""

# 方法 1: 使用 Win+Alt+R 快捷键（推荐）
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "方法 1: 使用快捷键录制（推荐）" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "1. 按 Win+Alt+R 开始录制" -ForegroundColor White
Write-Host "2. 等待 $Duration 秒" -ForegroundColor White
Write-Host "3. 再次按 Win+Alt+R 停止录制" -ForegroundColor White
Write-Host "4. 录制文件会保存在: $env:USERPROFILE\Videos\Captures\" -ForegroundColor Yellow
Write-Host ""

# 使用 PowerShell 模拟按键
Add-Type -AssemblyName System.Windows.Forms

Write-Host "是否自动开始录制？(y/n): " -ForegroundColor Green -NoNewline
$response = Read-Host

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "🎬 3秒后开始录制..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    Write-Host "   3..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    Write-Host "   2..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    Write-Host "   1..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1
    
    # 发送 Win+Alt+R 开始录制
    Write-Host ""
    Write-Host "📹 开始录制..." -ForegroundColor Green
    
    # 使用 Windows Script Host 发送按键
    $wshell = New-Object -ComObject wscript.shell
    $wshell.SendKeys('^%r')  # Win+Alt+R
    
    Write-Host "⏱️  录制中... ($Duration 秒)" -ForegroundColor Cyan
    
    # 显示倒计时
    for ($i = $Duration; $i -gt 0; $i--) {
        Write-Host "   剩余: $i 秒" -ForegroundColor Yellow -NoNewline
        Start-Sleep -Seconds 1
        Write-Host "`r" -NoNewline
    }
    
    Write-Host ""
    Write-Host "🛑 停止录制..." -ForegroundColor Red
    $wshell.SendKeys('^%r')  # Win+Alt+R 停止
    
    Start-Sleep -Seconds 2
    
    Write-Host ""
    Write-Host "✅ 录制完成！" -ForegroundColor Green
    Write-Host "📁 录制文件保存在: $env:USERPROFILE\Videos\Captures\" -ForegroundColor Cyan
    Write-Host ""
    
    # 打开录制文件夹
    Write-Host "是否打开录制文件夹？(y/n): " -ForegroundColor Yellow -NoNewline
    $openFolder = Read-Host
    
    if ($openFolder -eq 'y' -or $openFolder -eq 'Y') {
        explorer "$env:USERPROFILE\Videos\Captures\"
    }
} else {
    Write-Host ""
    Write-Host "已取消自动录制。" -ForegroundColor Gray
    Write-Host "你可以手动按 Win+Alt+R 来开始/停止录制。" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "其他录屏方法:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "方法 2: 使用 OBS Studio (免费开源)" -ForegroundColor White
Write-Host "   下载: https://obsproject.com/" -ForegroundColor Gray
Write-Host ""
Write-Host "方法 3: 使用 ShareX (免费开源)" -ForegroundColor White
Write-Host "   下载: https://getsharex.com/" -ForegroundColor Gray
Write-Host ""
Write-Host "方法 4: 使用 FFmpeg (命令行)" -ForegroundColor White
Write-Host "   需要先安装 FFmpeg" -ForegroundColor Gray
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
