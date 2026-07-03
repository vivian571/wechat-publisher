# 强力清除所有代理
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
$env:ALL_PROXY = $null
$env:NO_PROXY = $null
$env:http_proxy = $null
$env:https_proxy = $null
$env:all_proxy = $null
$env:no_proxy = $null

# 激活虚拟环境
.\venv\Scripts\activate

Write-Host "✅ 已清除所有代理设置" -ForegroundColor Green
Write-Host ""

# 读取配置
$config = @{}
Get-Content ".\glm4.yaml" | ForEach-Object {
    if ($_ -match '^\s*(\w+):\s*"?([^"]+)"?\s*$') {
        $key = $matches[1]
        $value = $matches[2].Trim('"')
        $config[$key] = $value
    }
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Open Interpreter - GLM-4 (无代理)" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 配置加载成功" -ForegroundColor Green
Write-Host "   模型: $($config['model'])" -ForegroundColor Gray
Write-Host "   API Base: $($config['api_base'])" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 启动 Open Interpreter..." -ForegroundColor Green
Write-Host ""

# 启动
interpreter `
    --model $config['model'] `
    --api_base $config['api_base'] `
    --api_key $config['api_key'] `
    --context_window $config['context_window'] `
    --max_tokens $config['max_tokens']
