# ========================================
# 快速安装录屏软件（无需 Chocolatey）
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "快速安装录屏软件" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "推荐的免费录屏软件:" -ForegroundColor Green
Write-Host ""

Write-Host "【1】ShareX (推荐)" -ForegroundColor Cyan
Write-Host "  ✅ 完全免费开源" -ForegroundColor Green
Write-Host "  ✅ 功能强大" -ForegroundColor Green
Write-Host "  ✅ 支持截图和录屏" -ForegroundColor Green
Write-Host "  ✅ 轻量级" -ForegroundColor Green
Write-Host "  📥 下载: https://getsharex.com/" -ForegroundColor Yellow
Write-Host ""

Write-Host "【2】OBS Studio" -ForegroundColor Cyan
Write-Host "  ✅ 专业级录屏" -ForegroundColor Green
Write-Host "  ✅ 支持直播" -ForegroundColor Green
Write-Host "  ✅ 高质量输出" -ForegroundColor Green
Write-Host "  📥 下载: https://obsproject.com/" -ForegroundColor Yellow
Write-Host ""

Write-Host "【3】ScreenToGif" -ForegroundColor Cyan
Write-Host "  ✅ 轻量级" -ForegroundColor Green
Write-Host "  ✅ 可录制 GIF" -ForegroundColor Green
Write-Host "  ✅ 内置编辑器" -ForegroundColor Green
Write-Host "  📥 下载: https://www.screentogif.com/" -ForegroundColor Yellow
Write-Host ""

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "选择要打开的下载页面:" -ForegroundColor Green
Write-Host "  1. ShareX (推荐)" -ForegroundColor White
Write-Host "  2. OBS Studio" -ForegroundColor White
Write-Host "  3. ScreenToGif" -ForegroundColor White
Write-Host "  4. 全部打开" -ForegroundColor White
Write-Host "  0. 跳过" -ForegroundColor Gray
Write-Host ""

Write-Host "请选择 (0-4): " -ForegroundColor Yellow -NoNewline
$choice = Read-Host

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "正在打开 ShareX 下载页面..." -ForegroundColor Green
        Start-Process "https://getsharex.com/"
    }
    "2" {
        Write-Host ""
        Write-Host "正在打开 OBS Studio 下载页面..." -ForegroundColor Green
        Start-Process "https://obsproject.com/"
    }
    "3" {
        Write-Host ""
        Write-Host "正在打开 ScreenToGif 下载页面..." -ForegroundColor Green
        Start-Process "https://www.screentogif.com/"
    }
    "4" {
        Write-Host ""
        Write-Host "正在打开所有下载页面..." -ForegroundColor Green
        Start-Process "https://getsharex.com/"
        Start-Sleep -Seconds 1
        Start-Process "https://obsproject.com/"
        Start-Sleep -Seconds 1
        Start-Process "https://www.screentogif.com/"
    }
    default {
        Write-Host ""
        Write-Host "已跳过" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "使用 winget 安装 (Windows 11 推荐):" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

$wingetInstalled = Get-Command winget -ErrorAction SilentlyContinue

if ($null -ne $wingetInstalled) {
    Write-Host "✅ 检测到 winget，可以使用以下命令安装:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  ShareX:" -ForegroundColor Yellow
    Write-Host "    winget install ShareX.ShareX" -ForegroundColor White
    Write-Host ""
    Write-Host "  OBS Studio:" -ForegroundColor Yellow
    Write-Host "    winget install OBSProject.OBSStudio" -ForegroundColor White
    Write-Host ""
    Write-Host "  ScreenToGif:" -ForegroundColor Yellow
    Write-Host "    winget install NickeManarin.ScreenToGif" -ForegroundColor White
    Write-Host ""
    
    Write-Host "是否使用 winget 安装 ShareX？(y/n): " -ForegroundColor Green -NoNewline
    $installShareX = Read-Host
    
    if ($installShareX -eq 'y' -or $installShareX -eq 'Y') {
        Write-Host ""
        Write-Host "正在安装 ShareX..." -ForegroundColor Yellow
        winget install ShareX.ShareX --accept-package-agreements --accept-source-agreements
        Write-Host ""
        Write-Host "✅ ShareX 安装完成！" -ForegroundColor Green
        Write-Host "可以在开始菜单找到 ShareX" -ForegroundColor Cyan
    }
} else {
    Write-Host "⚠️  未检测到 winget" -ForegroundColor Yellow
    Write-Host "请手动下载安装软件" -ForegroundColor Gray
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
