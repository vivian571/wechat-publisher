# Project N 启动脚本
# 自动配置 ADB 环境变量并运行系统

# 添加 ADB 到当前会话的环境变量
$env:Path += ";D:\platform-tools-latest-windows\platform-tools"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "       Project N - 智能手机自动化系统" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 检查 ADB 是否可用
Write-Host "🔍 检查 ADB 工具..." -ForegroundColor Yellow
try {
    $adbVersion = adb version 2>&1 | Select-Object -First 1
    Write-Host "✅ ADB 已就绪: $adbVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ADB 不可用,请检查安装" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📱 检查设备连接..." -ForegroundColor Yellow
$devices = adb devices
Write-Host $devices

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "可用命令:" -ForegroundColor Green
Write-Host "  python main.py --mode test      # 测试模式" -ForegroundColor White
Write-Host "  python main.py --mode auto      # 自动刷视频(10分钟)" -ForegroundColor White
Write-Host "  python main.py --mode auto --duration 30  # 自动刷视频(30分钟)" -ForegroundColor White
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# 如果提供了参数,直接运行
if ($args.Count -gt 0) {
    Write-Host "🚀 启动 Project N..." -ForegroundColor Green
    python main.py $args
} else {
    Write-Host "💡 提示: 使用 './start.ps1 --mode test' 运行测试" -ForegroundColor Yellow
}
