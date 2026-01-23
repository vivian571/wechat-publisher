@echo off
REM 视频自动上传服务启动脚本

echo ============================================================
echo 启动视频自动上传桥接服务
echo ============================================================

REM 清除代理环境变量
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=

REM 激活虚拟环境（使用 social-auto-upload 的环境）
call social-auto-upload\venv\Scripts\activate.bat

REM 启动监控脚本
python auto_upload_bridge.py

pause
