# ========================================
# WeChat Publisher 启动脚本（无代理模式）
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WeChat Publisher 启动（无代理）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 清除所有代理设置
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
$env:ALL_PROXY = $null

Write-Host "✅ 已清除所有代理设置" -ForegroundColor Green
Write-Host "⚠️  注意：图片下载将使用直连" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 正在启动 WeChat Publisher..." -ForegroundColor Green
Write-Host ""

# 启动程序
python wechat_publisher.py
