# ========================================
# 无代理启动 Open Interpreter
# ========================================

# 清除所有代理设置
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
$env:ALL_PROXY = $null
$env:NO_PROXY = $null

Write-Host "✅ 已清除所有代理设置" -ForegroundColor Green
Write-Host ""

# 启动 Open Interpreter
.\start_interpreter.ps1
