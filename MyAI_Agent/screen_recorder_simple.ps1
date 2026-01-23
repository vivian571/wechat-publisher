# ========================================
# 简易屏幕录制工具
# 使用 PowerShell 截取连续截图并合成视频
# ========================================

param(
    [int]$Duration = 10,
    [int]$FPS = 5,
    [string]$OutputFolder = "$env:USERPROFILE\Desktop\ScreenCapture_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PowerShell 屏幕录制工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 创建输出文件夹
New-Item -ItemType Directory -Path $OutputFolder -Force | Out-Null

Write-Host "📹 录制设置:" -ForegroundColor Green
Write-Host "   时长: $Duration 秒" -ForegroundColor White
Write-Host "   帧率: $FPS FPS" -ForegroundColor White
Write-Host "   输出文件夹: $OutputFolder" -ForegroundColor White
Write-Host ""

# 加载 System.Drawing
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Write-Host "🎬 3秒后开始录制..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Write-Host "   3..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Write-Host "   2..." -ForegroundColor Yellow
Start-Sleep -Seconds 1
Write-Host "   1..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

Write-Host ""
Write-Host "📹 正在录制..." -ForegroundColor Green
Write-Host ""

# 获取屏幕尺寸
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$width = $screen.Width
$height = $screen.Height

Write-Host "   屏幕分辨率: ${width}x${height}" -ForegroundColor Gray

# 计算总帧数
$totalFrames = $Duration * $FPS
$interval = 1000 / $FPS  # 毫秒

$frameCount = 0
$startTime = Get-Date

try {
    for ($i = 0; $i -lt $totalFrames; $i++) {
        $frameStart = Get-Date
        
        # 创建位图
        $bitmap = New-Object System.Drawing.Bitmap $width, $height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        
        # 截取屏幕
        $graphics.CopyFromScreen(0, 0, 0, 0, $bitmap.Size)
        
        # 保存图片
        $filename = Join-Path $OutputFolder ("frame_{0:D5}.png" -f $i)
        $bitmap.Save($filename, [System.Drawing.Imaging.ImageFormat]::Png)
        
        # 清理
        $graphics.Dispose()
        $bitmap.Dispose()
        
        $frameCount++
        
        # 显示进度
        $elapsed = ((Get-Date) - $startTime).TotalSeconds
        $remaining = $Duration - $elapsed
        Write-Host "`r   已录制: $frameCount 帧 | 剩余: $([math]::Max(0, [math]::Round($remaining, 1))) 秒" -NoNewline -ForegroundColor Cyan
        
        # 控制帧率
        $frameTime = ((Get-Date) - $frameStart).TotalMilliseconds
        $sleepTime = [math]::Max(0, $interval - $frameTime)
        if ($sleepTime -gt 0) {
            Start-Sleep -Milliseconds $sleepTime
        }
    }
} catch {
    Write-Host ""
    Write-Host "❌ 录制出错: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host ""
Write-Host "✅ 录制完成！共 $frameCount 帧" -ForegroundColor Green
Write-Host ""

# 检查是否安装了 FFmpeg
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($null -ne $ffmpegPath) {
    Write-Host "🎥 检测到 FFmpeg，正在合成视频..." -ForegroundColor Yellow
    
    $videoOutput = Join-Path $env:USERPROFILE "Desktop\ScreenRecording_$(Get-Date -Format 'yyyyMMdd_HHmmss').mp4"
    
    $ffmpegArgs = @(
        "-framerate", $FPS,
        "-i", (Join-Path $OutputFolder "frame_%05d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-y",
        $videoOutput
    )
    
    try {
        $process = Start-Process -FilePath "ffmpeg" -ArgumentList $ffmpegArgs -NoNewWindow -PassThru -Wait
        
        if ($process.ExitCode -eq 0) {
            Write-Host "✅ 视频合成完成！" -ForegroundColor Green
            Write-Host "📁 视频文件: $videoOutput" -ForegroundColor Cyan
            
            $fileInfo = Get-Item $videoOutput
            $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
            Write-Host "📊 文件大小: $fileSizeMB MB" -ForegroundColor Yellow
            Write-Host ""
            
            # 询问是否删除临时文件
            Write-Host "是否删除临时截图文件？(y/n): " -ForegroundColor Yellow -NoNewline
            $deleteTemp = Read-Host
            
            if ($deleteTemp -eq 'y' -or $deleteTemp -eq 'Y') {
                Remove-Item -Path $OutputFolder -Recurse -Force
                Write-Host "✅ 临时文件已删除" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "是否播放视频？(y/n): " -ForegroundColor Yellow -NoNewline
            $playVideo = Read-Host
            
            if ($playVideo -eq 'y' -or $playVideo -eq 'Y') {
                Start-Process $videoOutput
            }
        } else {
            Write-Host "❌ 视频合成失败" -ForegroundColor Red
            Write-Host "📁 截图文件保存在: $OutputFolder" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ 视频合成出错: $_" -ForegroundColor Red
        Write-Host "📁 截图文件保存在: $OutputFolder" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  未检测到 FFmpeg，无法合成视频" -ForegroundColor Yellow
    Write-Host "📁 截图文件保存在: $OutputFolder" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "你可以:" -ForegroundColor White
    Write-Host "  1. 安装 FFmpeg 后重新运行脚本合成视频" -ForegroundColor Gray
    Write-Host "  2. 使用在线工具将图片合成视频" -ForegroundColor Gray
    Write-Host "  3. 手动查看截图序列" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "是否打开截图文件夹？(y/n): " -ForegroundColor Yellow -NoNewline
    $openFolder = Read-Host
    
    if ($openFolder -eq 'y' -or $openFolder -eq 'Y') {
        explorer $OutputFolder
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host "推荐安装 FFmpeg 以获得更好的录屏体验:" -ForegroundColor Cyan
Write-Host "  choco install ffmpeg" -ForegroundColor White
Write-Host "  或访问: https://ffmpeg.org/download.html" -ForegroundColor Gray
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
