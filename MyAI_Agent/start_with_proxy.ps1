# ========================================
# Open Interpreter 代理配置启动脚本
# 支持通过代理访问 GLM-4 API
# ========================================

param(
    [string]$ProxyUrl = ""  # 例如: "http://127.0.0.1:7890"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Open Interpreter - 代理配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 如果没有指定代理，询问用户
if ([string]::IsNullOrEmpty($ProxyUrl)) {
    Write-Host "是否使用代理？(y/n): " -ForegroundColor Yellow -NoNewline
    $useProxy = Read-Host
    
    if ($useProxy -eq 'y' -or $useProxy -eq 'Y') {
        Write-Host ""
        Write-Host "常见代理配置:" -ForegroundColor Cyan
        Write-Host "  Clash: http://127.0.0.1:7890" -ForegroundColor Gray
        Write-Host "  V2Ray: http://127.0.0.1:10809" -ForegroundColor Gray
        Write-Host "  其他: 请输入你的代理地址" -ForegroundColor Gray
        Write-Host ""
        Write-Host "请输入代理地址 (例如 http://127.0.0.1:7890): " -ForegroundColor Yellow -NoNewline
        $ProxyUrl = Read-Host
    }
}

# 激活虚拟环境
.\venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Open Interpreter - GLM-4 配置" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 配置代理
if (![string]::IsNullOrEmpty($ProxyUrl)) {
    Write-Host "🔧 配置代理设置..." -ForegroundColor Yellow
    
    # 设置环境变量
    $env:HTTP_PROXY = $ProxyUrl
    $env:HTTPS_PROXY = $ProxyUrl
    $env:ALL_PROXY = $ProxyUrl
    
    Write-Host "  ✅ HTTP_PROXY: $ProxyUrl" -ForegroundColor Green
    Write-Host "  ✅ HTTPS_PROXY: $ProxyUrl" -ForegroundColor Green
    Write-Host ""
    
    # 测试代理连接
    Write-Host "🔍 测试代理连接..." -ForegroundColor Yellow
    try {
        $testUrl = "https://open.bigmodel.cn"
        $response = Invoke-WebRequest -Uri $testUrl -Proxy $ProxyUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        Write-Host "  ✅ 代理连接成功" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠️  代理连接测试失败: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "  继续启动，但可能会遇到连接问题..." -ForegroundColor Gray
    }
    Write-Host ""
}
else {
    Write-Host "🔧 不使用代理（直连）" -ForegroundColor Yellow
    
    # 清除代理设置
    $env:HTTP_PROXY = $null
    $env:HTTPS_PROXY = $null
    $env:ALL_PROXY = $null
    
    Write-Host "  ✅ 已清除代理设置" -ForegroundColor Green
    Write-Host ""
}

# 读取配置
$configPath = Join-Path (Get-Location) "glm4.yaml"

if (-not (Test-Path $configPath)) {
    Write-Host "❌ 错误: 找不到配置文件 glm4.yaml" -ForegroundColor Red
    exit 1
}

$config = @{}
Get-Content $configPath | ForEach-Object {
    if ($_ -match '^\s*(\w+):\s*"?([^"]+)"?\s*$') {
        $key = $matches[1]
        $value = $matches[2].Trim('"')
        $config[$key] = $value
    }
}

# 验证配置
if ([string]::IsNullOrEmpty($config['api_key'])) {
    Write-Host "❌ 错误: glm4.yaml 中未设置 api_key" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 配置加载成功" -ForegroundColor Green
Write-Host "   模型: $($config['model'])" -ForegroundColor Gray
Write-Host "   API Base: $($config['api_base'])" -ForegroundColor Gray
Write-Host "   代理: $(if ($ProxyUrl) { $ProxyUrl } else { '直连' })" -ForegroundColor Gray
Write-Host ""
Write-Host "🚀 启动 Open Interpreter..." -ForegroundColor Green
Write-Host ""

# 启动
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
    
    if (![string]::IsNullOrEmpty($ProxyUrl)) {
        Write-Host "  1. 检查代理软件是否正在运行" -ForegroundColor White
        Write-Host "  2. 验证代理地址是否正确: $ProxyUrl" -ForegroundColor White
        Write-Host "  3. 尝试不使用代理: .\start_with_proxy.ps1" -ForegroundColor White
    }
    else {
        Write-Host "  1. 检查网络连接" -ForegroundColor White
        Write-Host "  2. 运行诊断脚本: .\diagnose_api.ps1" -ForegroundColor White
        Write-Host "  3. 如果在公司网络，可能需要配置代理" -ForegroundColor White
    }
    Write-Host ""
}
