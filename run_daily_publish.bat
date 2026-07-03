@echo off
REM 公众号矩阵每日自动发布启动脚本
REM 每天晚上8点由 Windows 任务计划程序自动执行

echo ========================================
echo 公众号矩阵每日自动发布
echo 执行时间: %date% %time%
echo ========================================

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 执行 Python 脚本
python daily_auto_publish.py

REM 检查执行结果
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo ✅ 执行成功
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ❌ 执行失败，错误代码: %ERRORLEVEL%
    echo ========================================
)

REM 保持窗口打开5秒（方便查看结果）
timeout /t 5 /nobreak

exit /b %ERRORLEVEL%
