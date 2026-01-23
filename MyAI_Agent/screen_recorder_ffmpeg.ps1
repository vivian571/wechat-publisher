# ========================================
# FFmpeg 屏幕录制脚本（需要先安装 FFmpeg）
# 高质量屏幕录制
# ========================================

param(
    [int]$Duration = 10,
    [string]$OutputPath = "$env:USERPROFILE\Desktop\ScreenRecording_$(Get-Date -Format 'yyyyMMdd_HHmmss').mp4",
    [int]$FPS = 30,
    [string]$Quality = "medium"  # low, medium, high
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FFmpeg 屏幕录制工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 FFmpeg 是否安装
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($null -eq $ffmpegPath) {
    Write-Host "❌ 错误: 未检测到 FFmpeg" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先安装 FFmpeg:" -ForegroundColor Yellow
    Write-Host "  方法 1: 使用 Chocolatey" -ForegroundColor White
    Write-Host "    choco install ffmpeg" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  方法 2: 使用 Scoop" -ForegroundColor White
    Write-Host "    scoop install ffmpeg" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  方法 3: 手动下载" -ForegroundColor White
    Write-Host "    https://ffmpeg.org/download.html" -ForegroundColor Gray
    Write-Host ""
    Write-Host "或者使用 screen_recorder.ps1 脚本（使用 Xbox Game Bar）" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "按任意键退出..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "✅ 检测到 FFmpeg: $($ffmpegPath.Source)" -ForegroundColor Green
Write-Host ""

# 设置质量参数
$crf = switch ($Quality) {
    "low" { 28 }
    "medium" { 23 }
    "high" { 18 }
    default { 23 }
}

Write-Host "📹 录制设置:" -ForegroundColor Green
Write-Host "   时长: $Duration 秒" -ForegroundColor White
Write-Host "   帧率: $FPS FPS" -ForegroundColor White
Write-Host "   质量: $Quality (CRF: $crf)" -ForegroundColor White
Write-Host "   输出: $OutputPath" -ForegroundColor White
Write-Host ""

Write-Host "🎬 3秒后开始录制..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Write-Host "   3..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Write-Host "   2..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Write-Host "   1..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "📹 正在录制... (按 Ctrl+C 可提前停止)" -ForegroundColor Green
Write-Host ""

# FFmpeg 录制命令
$ffmpegArgs = @(
    "-f", "gdigrab",
    "-framerate", $FPS,
    "-i", "desktop",
    "-t", $Duration,
    "-c:v", "libx264",
    "-crf", $crf,
    "-preset", "ultrafast",
    "-pix_fmt", "yuv420p",
    "-y",
    $OutputPath
)

try {
    # 启动 FFmpeg
    $process = Start-Process -FilePath "ffmpeg" -ArgumentList $ffmpegArgs -NoNewWindow -PassThru -Wait
    
    if ($process.ExitCode -eq 0) {
        Write-Host ""
        Write-Host "✅ 录制完成！" -ForegroundColor Green
        Write-Host "📁 文件保存在: $OutputPath" -ForegroundColor Cyan
        
        # 显示文件信息
        $fileInfo = Get-Item $OutputPath
        $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
        Write-Host "📊 文件大小: $fileSizeMB MB" -ForegroundColor Yellow
        Write-Host ""
        
        # 询问是否播放
        Write-Host "是否播放录制的视频？(y/n): " -ForegroundColor Yellow -NoNewline
        $playVideo = Read-Host
        
        if ($playVideo -eq 'y' -or $playVideo -eq 'Y') {
            Start-Process $OutputPath
        }
    } else {
        Write-Host ""
        Write-Host "❌ 录制失败，退出代码: $($process.ExitCode)" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "❌ 录制过程中出错: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
