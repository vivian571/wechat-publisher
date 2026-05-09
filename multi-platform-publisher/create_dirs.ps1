# 创建必要的目录
$directories = @("documents", "images", "published")

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "已创建目录: $dir"
    } else {
        Write-Host "目录已存在: $dir"
    }
}
