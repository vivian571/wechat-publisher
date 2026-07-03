# ========================================
# 强力清除所有代理设置
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "清除所有代理设置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 清除环境变量代理
Write-Host "【1】清除环境变量代理" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$proxyVars = @(
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy"
)

foreach ($var in $proxyVars) {
    # 清除进程级别
    [System.Environment]::SetEnvironmentVariable($var, $null, "Process")
    Set-Item -Path "Env:$var" -Value $null -ErrorAction SilentlyContinue
    
    # 清除用户级别
    [System.Environment]::SetEnvironmentVariable($var, $null, "User")
    
    Write-Host "  ✅ 已清除: $var" -ForegroundColor Green
}

Write-Host ""

# 2. 清除系统代理设置
Write-Host "【2】清除系统代理设置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

try {
    # 禁用 IE/系统代理
    $regPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    Set-ItemProperty -Path $regPath -Name "ProxyEnable" -Value 0 -ErrorAction SilentlyContinue
    Set-ItemProperty -Path $regPath -Name "ProxyServer" -Value "" -ErrorAction SilentlyContinue
    
    Write-Host "  ✅ 已禁用系统代理" -ForegroundColor Green
} catch {
    Write-Host "  ⚠️  无法修改系统代理设置: $_" -ForegroundColor Yellow
}

Write-Host ""

# 3. 清除 Python/pip 代理
Write-Host "【3】清除 Python 代理配置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 删除 pip 配置文件中的代理
$pipConfigPaths = @(
    "$env:APPDATA\pip\pip.ini",
    "$env:USERPROFILE\pip\pip.ini",
    "$env:USERPROFILE\.pip\pip.ini"
)

foreach ($configPath in $pipConfigPaths) {
    if (Test-Path $configPath) {
        try {
            $content = Get-Content $configPath -Raw
            if ($content -match "proxy") {
                Write-Host "  ⚠️  发现 pip 配置文件包含代理: $configPath" -ForegroundColor Yellow
                Write-Host "     建议手动检查并删除代理配置" -ForegroundColor Gray
            }
        } catch {
            # 忽略错误
        }
    }
}

Write-Host "  ✅ Python 代理检查完成" -ForegroundColor Green
Write-Host ""

# 4. 验证代理已清除
Write-Host "【4】验证代理设置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$hasProxy = $false

foreach ($var in $proxyVars) {
    $value = [System.Environment]::GetEnvironmentVariable($var)
    if ($value) {
        Write-Host "  ⚠️  仍然存在: $var = $value" -ForegroundColor Yellow
        $hasProxy = $true
    }
}

if (-not $hasProxy) {
    Write-Host "  ✅ 所有代理设置已清除" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  部分代理设置仍然存在，可能需要重启 PowerShell" -ForegroundColor Yellow
}

Write-Host ""

# 5. 测试网络连接
Write-Host "【5】测试网络连接" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

try {
    $ping = Test-Connection -ComputerName "open.bigmodel.cn" -Count 1 -ErrorAction Stop
    Write-Host "  ✅ 可以访问 open.bigmodel.cn" -ForegroundColor Green
} catch {
    Write-Host "  ❌ 无法访问 open.bigmodel.cn" -ForegroundColor Red
}

Write-Host ""

# 6. 创建启动脚本
Write-Host "【6】创建无代理启动脚本" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$script = @'
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
'@

$script | Set-Content -Path ".\start_no_proxy.ps1" -Encoding UTF8

Write-Host "  ✅ 已创建: start_no_proxy.ps1" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "下一步操作:" -ForegroundColor Yellow
Write-Host "  1. 关闭所有代理软件（Clash、V2Ray 等）" -ForegroundColor White
Write-Host "  2. 运行无代理启动脚本:" -ForegroundColor White
Write-Host "     .\start_no_proxy.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
