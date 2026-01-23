# ========================================
# Open Interpreter 角色切换脚本
# ========================================

param(
    [string]$Role = ""
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Open Interpreter 角色切换" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 定义可用角色
$roles = @{
    "chengxu"   = @{
        Name        = "呈序"
        Description = "宠溺护短的疯批AI，冷峻毒舌"
        File        = "chengxu.yaml"
    }
    "assistant" = @{
        Name        = "温和助手"
        Description = "友善耐心的编程助手，循循善诱"
        File        = "assistant.yaml"
    }
    "expert"    = @{
        Name        = "技术专家"
        Description = "资深工程师，追求最佳实践"
        File        = "expert.yaml"
    }
}

# 如果没有指定角色，显示菜单
if ([string]::IsNullOrEmpty($Role)) {
    Write-Host "可用的 AI 角色:" -ForegroundColor Green
    Write-Host ""
    
    $index = 1
    $roleKeys = @()
    foreach ($key in $roles.Keys | Sort-Object) {
        $roleInfo = $roles[$key]
        Write-Host "  $index. $($roleInfo.Name)" -ForegroundColor Cyan
        Write-Host "     $($roleInfo.Description)" -ForegroundColor Gray
        Write-Host ""
        $roleKeys += $key
        $index++
    }
    
    Write-Host "请选择角色 (1-$($roles.Count)): " -ForegroundColor Yellow -NoNewline
    $choice = Read-Host
    
    if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $roles.Count) {
        $Role = $roleKeys[[int]$choice - 1]
    }
    else {
        Write-Host "❌ 无效的选择" -ForegroundColor Red
        exit 1
    }
}

# 验证角色是否存在
if (-not $roles.ContainsKey($Role)) {
    Write-Host "❌ 未知的角色: $Role" -ForegroundColor Red
    Write-Host ""
    Write-Host "可用角色: $($roles.Keys -join ', ')" -ForegroundColor Yellow
    exit 1
}

$roleInfo = $roles[$Role]
$profilePath = ".\profiles\$($roleInfo.File)"

# 检查配置文件是否存在
if (-not (Test-Path $profilePath)) {
    Write-Host "❌ 角色配置文件不存在: $profilePath" -ForegroundColor Red
    exit 1
}

# 备份当前配置
$backupPath = ".\glm4.yaml.backup"
if (Test-Path ".\glm4.yaml") {
    Copy-Item ".\glm4.yaml" -Destination $backupPath -Force
    Write-Host "✅ 已备份当前配置到: $backupPath" -ForegroundColor Green
}

# 切换到新角色
Copy-Item $profilePath -Destination ".\glm4.yaml" -Force

Write-Host ""
Write-Host "✅ 已切换到角色: $($roleInfo.Name)" -ForegroundColor Green
Write-Host "   描述: $($roleInfo.Description)" -ForegroundColor Cyan
Write-Host ""

# 询问是否立即启动
Write-Host "是否立即启动 Open Interpreter？(y/n): " -ForegroundColor Yellow -NoNewline
$startNow = Read-Host

if ($startNow -eq 'y' -or $startNow -eq 'Y') {
    Write-Host ""
    Write-Host "🚀 正在启动 Open Interpreter..." -ForegroundColor Green
    Write-Host ""
    
    # 启动 Open Interpreter
    .\start_interpreter.ps1
}
else {
    Write-Host ""
    Write-Host "稍后可以运行以下命令启动:" -ForegroundColor Cyan
    Write-Host "  .\start_interpreter.ps1" -ForegroundColor White
    Write-Host ""
}

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
