# ========================================
# Windows 录屏工具推荐和安装脚本
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows 录屏解决方案" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "检测系统信息..." -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
$osVersion = $os.Version
$osName = $os.Caption

Write-Host "  系统: $osName" -ForegroundColor White
Write-Host "  版本: $osVersion" -ForegroundColor White
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "推荐的录屏方案:" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "【方案 1】使用 OBS Studio (强烈推荐)" -ForegroundColor Cyan
Write-Host "  ✅ 免费开源" -ForegroundColor Green
Write-Host "  ✅ 功能强大" -ForegroundColor Green
Write-Host "  ✅ 支持直播和录制" -ForegroundColor Green
Write-Host "  ✅ 高质量输出" -ForegroundColor Green
Write-Host ""
Write-Host "  安装命令 (使用 Chocolatey):" -ForegroundColor Yellow
Write-Host "    choco install obs-studio -y" -ForegroundColor White
Write-Host "  或手动下载: https://obsproject.com/" -ForegroundColor Gray
Write-Host ""

Write-Host "【方案 2】使用 ShareX (推荐)" -ForegroundColor Cyan
Write-Host "  ✅ 免费开源" -ForegroundColor Green
Write-Host "  ✅ 轻量级" -ForegroundColor Green
Write-Host "  ✅ 支持截图和录屏" -ForegroundColor Green
Write-Host "  ✅ 自动上传功能" -ForegroundColor Green
Write-Host ""
Write-Host "  安装命令 (使用 Chocolatey):" -ForegroundColor Yellow
Write-Host "    choco install sharex -y" -ForegroundColor White
Write-Host "  或手动下载: https://getsharex.com/" -ForegroundColor Gray
Write-Host ""

Write-Host "【方案 3】使用 ScreenToGif (轻量)" -ForegroundColor Cyan
Write-Host "  ✅ 免费开源" -ForegroundColor Green
Write-Host "  ✅ 可录制 GIF" -ForegroundColor Green
Write-Host "  ✅ 内置编辑器" -ForegroundColor Green
Write-Host ""
Write-Host "  安装命令 (使用 Chocolatey):" -ForegroundColor Yellow
Write-Host "    choco install screentogif -y" -ForegroundColor White
Write-Host "  或手动下载: https://www.screentogif.com/" -ForegroundColor Gray
Write-Host ""

Write-Host "【方案 4】使用 Windows 内置工具" -ForegroundColor Cyan
Write-Host "  ⚙️  Xbox Game Bar (Win+G)" -ForegroundColor Yellow
Write-Host "     快捷键: Win+Alt+R 开始/停止录制" -ForegroundColor Gray
Write-Host "     录制文件位置: %USERPROFILE%\Videos\Captures\" -ForegroundColor Gray
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# 检查是否安装了 Chocolatey
$chocoInstalled = Get-Command choco -ErrorAction SilentlyContinue

if ($null -eq $chocoInstalled) {
    Write-Host "⚠️  未检测到 Chocolatey 包管理器" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "是否安装 Chocolatey？(y/n): " -ForegroundColor Green -NoNewline
    $installChoco = Read-Host
    
    if ($installChoco -eq 'y' -or $installChoco -eq 'Y') {
        Write-Host ""
        Write-Host "正在安装 Chocolatey..." -ForegroundColor Yellow
        Write-Host "注意: 需要管理员权限" -ForegroundColor Red
        Write-Host ""
        
        # 检查是否是管理员
        $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        
        if (-not $isAdmin) {
            Write-Host "❌ 需要管理员权限才能安装 Chocolatey" -ForegroundColor Red
            Write-Host "请以管理员身份运行 PowerShell，然后执行:" -ForegroundColor Yellow
            Write-Host "  Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" -ForegroundColor White
        } else {
            try {
                Set-ExecutionPolicy Bypass -Scope Process -Force
                [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
                iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
                
                Write-Host ""
                Write-Host "✅ Chocolatey 安装完成！" -ForegroundColor Green
                $chocoInstalled = $true
            } catch {
                Write-Host ""
                Write-Host "❌ Chocolatey 安装失败: $_" -ForegroundColor Red
                $chocoInstalled = $false
            }
        }
    }
}

if ($null -ne $chocoInstalled -or $chocoInstalled -eq $true) {
    Write-Host ""
    Write-Host "选择要安装的录屏工具:" -ForegroundColor Green
    Write-Host "  1. OBS Studio (推荐)" -ForegroundColor White
    Write-Host "  2. ShareX" -ForegroundColor White
    Write-Host "  3. ScreenToGif" -ForegroundColor White
    Write-Host "  4. 全部安装" -ForegroundColor White
    Write-Host "  0. 跳过" -ForegroundColor Gray
    Write-Host ""
    Write-Host "请选择 (0-4): " -ForegroundColor Yellow -NoNewline
    $choice = Read-Host
    
    switch ($choice) {
        "1" {
            Write-Host ""
            Write-Host "正在安装 OBS Studio..." -ForegroundColor Yellow
            choco install obs-studio -y
            Write-Host "✅ OBS Studio 安装完成！" -ForegroundColor Green
        }
        "2" {
            Write-Host ""
            Write-Host "正在安装 ShareX..." -ForegroundColor Yellow
            choco install sharex -y
            Write-Host "✅ ShareX 安装完成！" -ForegroundColor Green
        }
        "3" {
            Write-Host ""
            Write-Host "正在安装 ScreenToGif..." -ForegroundColor Yellow
            choco install screentogif -y
            Write-Host "✅ ScreenToGif 安装完成！" -ForegroundColor Green
        }
        "4" {
            Write-Host ""
            Write-Host "正在安装所有工具..." -ForegroundColor Yellow
            choco install obs-studio sharex screentogif -y
            Write-Host "✅ 所有工具安装完成！" -ForegroundColor Green
        }
        default {
            Write-Host ""
            Write-Host "已跳过安装" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "快速录屏指南:" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "使用 Xbox Game Bar:" -ForegroundColor Yellow
Write-Host "  1. 按 Win+G 打开 Game Bar" -ForegroundColor White
Write-Host "  2. 点击录制按钮或按 Win+Alt+R" -ForegroundColor White
Write-Host "  3. 再次按 Win+Alt+R 停止录制" -ForegroundColor White
Write-Host "  4. 文件保存在: $env:USERPROFILE\Videos\Captures\" -ForegroundColor Gray
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
