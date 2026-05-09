# ========================================
# WeChat Publisher Launch Script
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WeChat Publisher Launching..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ask about proxy
Write-Host "Use proxy for image downloads? (y/n): " -ForegroundColor Yellow -NoNewline
$useProxy = Read-Host

if ($useProxy -eq 'y' -or $useProxy -eq 'Y') {
    Write-Host ""
    Write-Host "Common Proxy Configs:" -ForegroundColor Cyan
    Write-Host "  1. Clash:      http://127.0.0.1:7890" -ForegroundColor Gray
    Write-Host "  2. V2Ray:      http://127.0.0.1:10809" -ForegroundColor Gray
    Write-Host "  3. Shadowsocks: http://127.0.0.1:1080" -ForegroundColor Gray
    Write-Host "  4. Custom" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Select (1-4): " -ForegroundColor Yellow -NoNewline
    $choice = Read-Host
    
    switch ($choice) {
        "1" { $proxyUrl = "http://127.0.0.1:7890" }
        "2" { $proxyUrl = "http://127.0.0.1:10809" }
        "3" { $proxyUrl = "http://127.0.0.1:1080" }
        "4" {
            Write-Host "Enter proxy URL (e.g. http://127.0.0.1:7890): " -ForegroundColor Yellow -NoNewline
            $proxyUrl = Read-Host
        }
        default { $proxyUrl = "http://127.0.0.1:7890" }
    }
    
    $env:HTTP_PROXY = $proxyUrl
    $env:HTTPS_PROXY = $proxyUrl
    
    Write-Host ""
    Write-Host "Proxy set to: $proxyUrl" -ForegroundColor Green
} else {
    $env:HTTP_PROXY = $null
    $env:HTTPS_PROXY = $null
    
    Write-Host ""
    Write-Host "Using Direct Connection (No Proxy)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting WeChat Publisher..." -ForegroundColor Green
Write-Host ""

python wechat_publisher.py
