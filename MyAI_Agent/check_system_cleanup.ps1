# ========================================
# 系统清理检查脚本
# 检查临时文件、垃圾文件和内存使用情况
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "系统清理状态检查工具" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 函数：计算文件夹大小
function Get-FolderSize {
    param([string]$Path)
    
    if (-not (Test-Path $Path)) {
        return 0
    }
    
    try {
        $size = (Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
            Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        if ($null -eq $size) { return 0 }
        return $size
    }
    catch {
        return 0
    }
}

# 函数：格式化文件大小
function Format-FileSize {
    param([long]$Size)
    
    if ($Size -gt 1GB) {
        return "{0:N2} GB" -f ($Size / 1GB)
    }
    elseif ($Size -gt 1MB) {
        return "{0:N2} MB" -f ($Size / 1MB)
    }
    elseif ($Size -gt 1KB) {
        return "{0:N2} KB" -f ($Size / 1KB)
    }
    else {
        return "$Size Bytes"
    }
}

# 函数：统计旧文件
function Get-OldFilesInfo {
    param(
        [string]$Path,
        [int]$DaysOld = 7
    )
    
    if (-not (Test-Path $Path)) {
        return @{Count = 0; Size = 0 }
    }
    
    try {
        $cutoffDate = (Get-Date).AddDays(-$DaysOld)
        $oldFiles = Get-ChildItem -Path $Path -Recurse -File -ErrorAction SilentlyContinue | 
        Where-Object { $_.LastWriteTime -lt $cutoffDate }
        
        $totalSize = ($oldFiles | Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        if ($null -eq $totalSize) { $totalSize = 0 }
        
        return @{
            Count = $oldFiles.Count
            Size  = $totalSize
        }
    }
    catch {
        return @{Count = 0; Size = 0 }
    }
}

Write-Host "正在扫描系统..." -ForegroundColor Yellow
Write-Host ""

# ========================================
# 1. 检查临时文件夹
# ========================================
Write-Host "【1】临时文件夹分析" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$tempPaths = @{
    "用户临时文件夹 (%TEMP%)" = $env:TEMP
    "系统临时文件夹"          = "C:\Windows\Temp"
    "预取文件夹"            = "C:\Windows\Prefetch"
}

$totalTempSize = 0

foreach ($name in $tempPaths.Keys) {
    $path = $tempPaths[$name]
    $size = Get-FolderSize -Path $path
    $totalTempSize += $size
    
    $oldFiles = Get-OldFilesInfo -Path $path -DaysOld 7
    
    Write-Host "  📁 $name" -ForegroundColor White
    Write-Host "     路径: $path" -ForegroundColor Gray
    Write-Host "     总大小: $(Format-FileSize $size)" -ForegroundColor Yellow
    Write-Host "     7天前文件: $($oldFiles.Count) 个, $(Format-FileSize $oldFiles.Size)" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "  💾 临时文件总计: $(Format-FileSize $totalTempSize)" -ForegroundColor Magenta
Write-Host ""

# ========================================
# 2. 检查回收站
# ========================================
Write-Host "【2】回收站分析" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

try {
    $shell = New-Object -ComObject Shell.Application
    $recycleBin = $shell.Namespace(0xA)
    $items = $recycleBin.Items()
    $recycleBinSize = 0
    
    foreach ($item in $items) {
        $recycleBinSize += $item.Size
    }
    
    Write-Host "  🗑️  回收站项目: $($items.Count) 个" -ForegroundColor White
    Write-Host "  💾 回收站大小: $(Format-FileSize $recycleBinSize)" -ForegroundColor Yellow
}
catch {
    Write-Host "  ⚠️  无法访问回收站信息" -ForegroundColor Yellow
    $recycleBinSize = 0
}
Write-Host ""

# ========================================
# 3. 检查浏览器缓存
# ========================================
Write-Host "【3】浏览器缓存分析" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$browserCaches = @{
    "Chrome"  = "$env:LOCALAPPDATA\Google\Chrome\User Data\Default\Cache"
    "Edge"    = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Default\Cache"
    "Firefox" = "$env:LOCALAPPDATA\Mozilla\Firefox\Profiles"
}

$totalBrowserCache = 0

foreach ($browser in $browserCaches.Keys) {
    $path = $browserCaches[$browser]
    $size = Get-FolderSize -Path $path
    $totalBrowserCache += $size
    
    if ($size -gt 0) {
        Write-Host "  🌐 $browser 缓存: $(Format-FileSize $size)" -ForegroundColor White
    }
}

Write-Host "  💾 浏览器缓存总计: $(Format-FileSize $totalBrowserCache)" -ForegroundColor Yellow
Write-Host ""

# ========================================
# 4. 检查内存使用情况
# ========================================
Write-Host "【4】内存使用情况" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$os = Get-CimInstance Win32_OperatingSystem
$totalMemory = $os.TotalVisibleMemorySize * 1KB
$freeMemory = $os.FreePhysicalMemory * 1KB
$usedMemory = $totalMemory - $freeMemory
$memoryUsagePercent = [math]::Round(($usedMemory / $totalMemory) * 100, 2)

Write-Host "  💻 总内存: $(Format-FileSize $totalMemory)" -ForegroundColor White
Write-Host "  ✅ 可用内存: $(Format-FileSize $freeMemory)" -ForegroundColor Green
Write-Host "  📊 已用内存: $(Format-FileSize $usedMemory) ($memoryUsagePercent%)" -ForegroundColor Yellow

if ($memoryUsagePercent -gt 80) {
    Write-Host "  ⚠️  内存使用率较高，建议关闭不必要的程序" -ForegroundColor Red
}
Write-Host ""

# ========================================
# 5. 检查磁盘空间
# ========================================
Write-Host "【5】磁盘空间分析" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$drives = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 }

foreach ($drive in $drives) {
    $total = $drive.Used + $drive.Free
    $usedPercent = [math]::Round(($drive.Used / $total) * 100, 2)
    
    Write-Host "  💿 驱动器 $($drive.Name):" -ForegroundColor White
    Write-Host "     总容量: $(Format-FileSize $total)" -ForegroundColor Gray
    Write-Host "     已使用: $(Format-FileSize $drive.Used) ($usedPercent%)" -ForegroundColor Yellow
    Write-Host "     可用空间: $(Format-FileSize $drive.Free)" -ForegroundColor Green
    
    if ($usedPercent -gt 90) {
        Write-Host "     ⚠️  磁盘空间不足，建议清理" -ForegroundColor Red
    }
    Write-Host ""
}

# ========================================
# 6. 总结和建议
# ========================================
Write-Host "【6】清理建议总结" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray

$totalCleanable = $totalTempSize + $recycleBinSize + $totalBrowserCache

Write-Host "  📊 可清理空间估算: $(Format-FileSize $totalCleanable)" -ForegroundColor Magenta
Write-Host ""
Write-Host "  建议操作:" -ForegroundColor Yellow
Write-Host "  1️⃣  清理临时文件 ($(Format-FileSize $totalTempSize))" -ForegroundColor White
Write-Host "  2️⃣  清空回收站 ($(Format-FileSize $recycleBinSize))" -ForegroundColor White
Write-Host "  3️⃣  清理浏览器缓存 ($(Format-FileSize $totalBrowserCache))" -ForegroundColor White

if ($memoryUsagePercent -gt 80) {
    Write-Host "  4️⃣  关闭不必要的程序以释放内存" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "扫描完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 询问是否执行清理
Write-Host "是否要执行自动清理？(y/n): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "开始清理..." -ForegroundColor Green
    Write-Host ""
    
    # 清理临时文件
    Write-Host "正在清理临时文件..." -ForegroundColor Yellow
    try {
        Remove-Item -Path "$env:TEMP\*" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "✅ 临时文件清理完成" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  部分临时文件无法删除（可能正在使用）" -ForegroundColor Yellow
    }
    
    # 清空回收站
    Write-Host "正在清空回收站..." -ForegroundColor Yellow
    try {
        Clear-RecycleBin -Force -ErrorAction SilentlyContinue
        Write-Host "✅ 回收站清空完成" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  无法清空回收站" -ForegroundColor Yellow
    }
    
    # 运行磁盘清理
    Write-Host "正在运行系统磁盘清理..." -ForegroundColor Yellow
    Start-Process cleanmgr -ArgumentList "/sagerun:1" -NoNewWindow
    
    Write-Host ""
    Write-Host "✅ 清理完成！" -ForegroundColor Green
    Write-Host "建议重启计算机以完全释放内存。" -ForegroundColor Cyan
}
else {
    Write-Host ""
    Write-Host "已取消清理操作。" -ForegroundColor Gray
}

Write-Host ""
Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
