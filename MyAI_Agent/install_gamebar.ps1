# ========================================
# 安装 Xbox Game Bar
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "安装 Xbox Game Bar" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "正在尝试安装 Xbox Game Bar..." -ForegroundColor Yellow
Write-Host ""

try {
    # 方法 1: 使用 winget (Windows 11 内置)
    $wingetInstalled = Get-Command winget -ErrorAction SilentlyContinue
    
    if ($null -ne $wingetInstalled) {
        Write-Host "使用 winget 安装..." -ForegroundColor Green
        winget install "Xbox Game Bar" --source msstore --accept-package-agreements --accept-source-agreements
    } else {
        # 方法 2: 打开 Microsoft Store
        Write-Host "打开 Microsoft Store..." -ForegroundColor Green
        Start-Process "ms-windows-store://pdp/?productid=9NZKPSTSNW4P"
        Write-Host ""
        Write-Host "请在 Microsoft Store 中点击 '获取' 按钮安装 Xbox Game Bar" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "✅ 安装命令已执行" -ForegroundColor Green
    Write-Host ""
    Write-Host "安装完成后:" -ForegroundColor Cyan
    Write-Host "  1. 按 Win+G 打开 Xbox Game Bar" -ForegroundColor White
    Write-Host "  2. 按 Win+Alt+R 开始/停止录制" -ForegroundColor White
    Write-Host "  3. 录制文件保存在: $env:USERPROFILE\Videos\Captures\" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ 安装失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请手动安装:" -ForegroundColor Yellow
    Write-Host "  1. 打开 Microsoft Store" -ForegroundColor White
    Write-Host "  2. 搜索 'Xbox Game Bar'" -ForegroundColor White
    Write-Host "  3. 点击 '获取' 安装" -ForegroundColor White
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
