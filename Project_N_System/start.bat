@echo off
REM Project N 启动脚本 (Windows CMD 版本)

echo ================================================
echo        Project N - 智能手机自动化系统
echo ================================================
echo.

REM 临时添加 ADB 到环境变量
set "PATH=%PATH%;D:\platform-tools-latest-windows\platform-tools"

echo 检查 ADB 工具...
adb version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ADB 不可用,请检查安装
    pause
    exit /b 1
)
echo ✅ ADB 已就绪
echo.

echo 检查设备连接...
adb devices
echo.

echo ================================================
echo 可用命令:
echo   start.bat test           # 测试模式
echo   start.bat auto           # 自动刷视频(10分钟)
echo   start.bat auto 30        # 自动刷视频(30分钟)
echo ================================================
echo.

REM 根据参数运行
if "%1"=="test" (
    echo 🚀 启动测试模式...
    python main.py --mode test
) else if "%1"=="auto" (
    if "%2"=="" (
        echo 🚀 启动自动模式 (10分钟)...
        python main.py --mode auto
    ) else (
        echo 🚀 启动自动模式 (%2分钟)...
        python main.py --mode auto --duration %2
    )
) else (
    echo 💡 提示: 使用 'start.bat test' 运行测试
)

pause
