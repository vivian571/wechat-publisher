# Windows 任务计划配置脚本
# 创建每天晚上8点自动执行的定时任务

$TaskName = "公众号矩阵每日自动发布"
$TaskDescription = "每天晚上8点自动执行公众号内容生成和发布流程"
$ScriptPath = "f:\公众号写作\run_daily_publish.bat"
$WorkingDirectory = "f:\公众号写作"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置 Windows 任务计划" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查脚本文件是否存在
if (-not (Test-Path $ScriptPath)) {
    Write-Host "❌ 错误: 找不到启动脚本" -ForegroundColor Red
    Write-Host "   路径: $ScriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 找到启动脚本: $ScriptPath" -ForegroundColor Green

# 删除已存在的同名任务（如果有）
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "⚠️  发现已存在的任务，正在删除..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "✅ 已删除旧任务" -ForegroundColor Green
}

# 创建任务操作
$Action = New-ScheduledTaskAction `
    -Execute "cmd.exe" `
    -Argument "/c `"$ScriptPath`"" `
    -WorkingDirectory $WorkingDirectory

# 创建触发器（每天晚上8点）
$Trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "20:00"

# 创建任务设置
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# 创建任务主体
$Principal = New-ScheduledTaskPrincipal `
    -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

# 注册任务
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Description $TaskDescription `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Force | Out-Null
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ 任务计划创建成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "任务详情:" -ForegroundColor Cyan
    Write-Host "  名称: $TaskName" -ForegroundColor White
    Write-Host "  执行时间: 每天晚上 20:00" -ForegroundColor White
    Write-Host "  脚本路径: $ScriptPath" -ForegroundColor White
    Write-Host "  工作目录: $WorkingDirectory" -ForegroundColor White
    Write-Host ""
    Write-Host "管理任务:" -ForegroundColor Cyan
    Write-Host "  查看任务: taskschd.msc" -ForegroundColor White
    Write-Host "  手动运行: Get-ScheduledTask -TaskName '$TaskName' | Start-ScheduledTask" -ForegroundColor White
    Write-Host "  禁用任务: Disable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  启用任务: Enable-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "  删除任务: Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "❌ 创建任务失败" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "错误信息: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "请确保:" -ForegroundColor Yellow
    Write-Host "  1. 以管理员身份运行此脚本" -ForegroundColor Yellow
    Write-Host "  2. 任务计划服务正在运行" -ForegroundColor Yellow
    exit 1
}

# 显示任务状态
Write-Host "当前任务状态:" -ForegroundColor Cyan
$Task = Get-ScheduledTask -TaskName $TaskName
Write-Host "  状态: $($Task.State)" -ForegroundColor White
Write-Host "  下次运行: $((Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo).NextRunTime)" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "配置完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
