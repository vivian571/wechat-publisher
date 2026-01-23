# ========================================
# Open Interpreter 启动脚本 (GLM-4)
# 使用命令行参数方式，避免 profile 文件编码问题
# ========================================

# 清除代理设置（避免连接问题）
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
$env:ALL_PROXY = $null

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Open Interpreter - GLM-4 配置" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 从 glm4.yaml 读取配置
$configPath = Join-Path (Get-Location) "glm4.yaml"

if (-not (Test-Path $configPath)) {
    Write-Host "❌ 错误: 找不到配置文件 glm4.yaml" -ForegroundColor Red
    exit 1
}

# 读取配置文件
$config = @{}
Get-Content $configPath | ForEach-Object {
    if ($_ -match '^\s*(\w+):\s*"?([^"]+)"?\s*$') {
        $key = $matches[1]
        $value = $matches[2].Trim('"')
        $config[$key] = $value
    }
}

# 验证必要的配置
if ([string]::IsNullOrEmpty($config['api_key'])) {
    Write-Host "❌ 错误: glm4.yaml 中未设置 api_key" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 配置加载成功" -ForegroundColor Green
Write-Host "   模型: $($config['model'])" -ForegroundColor Gray
Write-Host "   API Base: $($config['api_base'])" -ForegroundColor Gray
Write-Host "   Context Window: $($config['context_window'])" -ForegroundColor Gray
Write-Host "   Max Tokens: $($config['max_tokens'])" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 启动 Open Interpreter..." -ForegroundColor Green
Write-Host ""

# 使用命令行参数启动（避免 profile 文件编码问题）
try {
    interpreter `
        --model $config['model'] `
        --api_base $config['api_base'] `
        --api_key $config['api_key'] `
        --context_window $config['context_window'] `
        --max_tokens $config['max_tokens']
}
catch {
    Write-Host ""
    Write-Host "❌ 启动失败: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 故障排除建议:" -ForegroundColor Yellow
    Write-Host "  1. 运行诊断脚本: .\diagnose_api.ps1" -ForegroundColor White
    Write-Host "  2. 检查网络连接" -ForegroundColor White
    Write-Host "  3. 验证 API Key 是否有效" -ForegroundColor White
    Write-Host ""
}
