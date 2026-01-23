# ========================================
# GLM-4 API 连接诊断和修复工具
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GLM-4 API 连接诊断" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 测试网络连接
Write-Host "【1】测试网络连接" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$apiHost = "open.bigmodel.cn"

try {
    $ping = Test-Connection -ComputerName $apiHost -Count 2 -ErrorAction Stop
    Write-Host "  ✅ 可以访问 $apiHost" -ForegroundColor Green
    Write-Host "     平均延迟: $([math]::Round(($ping | Measure-Object -Property ResponseTime -Average).Average, 2)) ms" -ForegroundColor Gray
} catch {
    Write-Host "  ❌ 无法访问 $apiHost" -ForegroundColor Red
    Write-Host "     错误: $_" -ForegroundColor Yellow
}
Write-Host ""

# 2. 检查代理设置
Write-Host "【2】检查代理设置" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$httpProxy = [System.Environment]::GetEnvironmentVariable("HTTP_PROXY")
$httpsProxy = [System.Environment]::GetEnvironmentVariable("HTTPS_PROXY")

if ($httpProxy -or $httpsProxy) {
    Write-Host "  ⚠️  检测到代理设置:" -ForegroundColor Yellow
    if ($httpProxy) { Write-Host "     HTTP_PROXY: $httpProxy" -ForegroundColor Gray }
    if ($httpsProxy) { Write-Host "     HTTPS_PROXY: $httpsProxy" -ForegroundColor Gray }
    Write-Host ""
    Write-Host "  这可能导致连接问题。是否清除代理设置？(y/n): " -ForegroundColor Yellow -NoNewline
    $clearProxy = Read-Host
    
    if ($clearProxy -eq 'y' -or $clearProxy -eq 'Y') {
        [System.Environment]::SetEnvironmentVariable("HTTP_PROXY", $null, "Process")
        [System.Environment]::SetEnvironmentVariable("HTTPS_PROXY", $null, "Process")
        $env:HTTP_PROXY = $null
        $env:HTTPS_PROXY = $null
        Write-Host "  ✅ 已清除代理设置" -ForegroundColor Green
    }
} else {
    Write-Host "  ✅ 未检测到代理设置" -ForegroundColor Green
}
Write-Host ""

# 3. 测试 API 连接
Write-Host "【3】测试 GLM-4 API 连接" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

# 读取配置
$configPath = ".\glm4.yaml"
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw
    
    if ($config -match 'api_key:\s*"([^"]+)"') {
        $apiKey = $matches[1]
        
        if ($apiKey -and $apiKey -ne "your-api-key-here") {
            Write-Host "  ✅ API Key 已配置" -ForegroundColor Green
            Write-Host "     Key: $($apiKey.Substring(0, 10))..." -ForegroundColor Gray
            
            # 测试 API 调用
            Write-Host ""
            Write-Host "  正在测试 API 调用..." -ForegroundColor Yellow
            
            $apiUrl = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
            $headers = @{
                "Authorization" = "Bearer $apiKey"
                "Content-Type" = "application/json"
            }
            
            $body = @{
                model = "glm-4"
                messages = @(
                    @{
                        role = "user"
                        content = "你好"
                    }
                )
                max_tokens = 10
            } | ConvertTo-Json -Depth 10
            
            try {
                $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -TimeoutSec 10
                Write-Host "  ✅ API 调用成功！" -ForegroundColor Green
                Write-Host "     响应: $($response.choices[0].message.content)" -ForegroundColor Cyan
            } catch {
                Write-Host "  ❌ API 调用失败" -ForegroundColor Red
                Write-Host "     错误: $($_.Exception.Message)" -ForegroundColor Yellow
                
                if ($_.Exception.Message -match "10054") {
                    Write-Host ""
                    Write-Host "  这是连接被重置的错误，可能原因:" -ForegroundColor Yellow
                    Write-Host "    1. 网络代理问题" -ForegroundColor Gray
                    Write-Host "    2. 防火墙阻止" -ForegroundColor Gray
                    Write-Host "    3. VPN 干扰" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "  ❌ API Key 未配置或无效" -ForegroundColor Red
        }
    } else {
        Write-Host "  ❌ 无法读取 API Key" -ForegroundColor Red
    }
} else {
    Write-Host "  ❌ 配置文件不存在: $configPath" -ForegroundColor Red
}
Write-Host ""

# 4. 建议的解决方案
Write-Host "【4】解决方案建议" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "如果连接失败，请尝试以下方法:" -ForegroundColor Yellow
Write-Host ""

Write-Host "方法 1: 清除环境变量中的代理" -ForegroundColor Cyan
Write-Host "  在 PowerShell 中运行:" -ForegroundColor White
Write-Host '  $env:HTTP_PROXY = $null' -ForegroundColor Gray
Write-Host '  $env:HTTPS_PROXY = $null' -ForegroundColor Gray
Write-Host '  $env:ALL_PROXY = $null' -ForegroundColor Gray
Write-Host ""

Write-Host "方法 2: 关闭 VPN 和代理软件" -ForegroundColor Cyan
Write-Host "  - 关闭所有 VPN 软件" -ForegroundColor White
Write-Host "  - 关闭代理软件（如 Clash、V2Ray 等）" -ForegroundColor White
Write-Host "  - 重新启动 Open Interpreter" -ForegroundColor White
Write-Host ""

Write-Host "方法 3: 检查防火墙设置" -ForegroundColor Cyan
Write-Host "  - 允许 Python 访问网络" -ForegroundColor White
Write-Host "  - 允许访问 open.bigmodel.cn" -ForegroundColor White
Write-Host ""

Write-Host "方法 4: 使用系统代理（如果在公司网络）" -ForegroundColor Cyan
Write-Host "  在启动脚本中添加:" -ForegroundColor White
Write-Host '  $env:HTTP_PROXY = "http://proxy.company.com:8080"' -ForegroundColor Gray
Write-Host '  $env:HTTPS_PROXY = "http://proxy.company.com:8080"' -ForegroundColor Gray
Write-Host ""

Write-Host "方法 5: 验证 API Key" -ForegroundColor Cyan
Write-Host "  - 访问 https://open.bigmodel.cn/" -ForegroundColor White
Write-Host "  - 检查 API Key 是否有效" -ForegroundColor White
Write-Host "  - 检查 API 配额是否充足" -ForegroundColor White
Write-Host ""

# 5. 创建无代理启动脚本
Write-Host "【5】创建无代理启动脚本" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$noProxyScript = @'
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
'@

$noProxyScript | Set-Content -Path ".\start_interpreter_no_proxy.ps1" -Encoding UTF8

Write-Host "  ✅ 已创建无代理启动脚本: start_interpreter_no_proxy.ps1" -ForegroundColor Green
Write-Host "     使用方法: .\start_interpreter_no_proxy.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
