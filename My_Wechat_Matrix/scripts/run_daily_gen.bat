@echo off
chcp 65001 >nul
cd /d f:\公众号写作\My_Wechat_Matrix
echo [%date% %time%] 开始执行每日自动化任务...
python scripts\daily_auto_gen.py
echo [%date% %time%] 任务执行完毕
pause
