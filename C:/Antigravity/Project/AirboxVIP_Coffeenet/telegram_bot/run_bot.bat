@echo off
chcp 65001 > NUL
echo ==========================================
echo   AirboxVIP Telegram Bot Launcher
echo ==========================================
pip install -r requirements.txt
python bot.py
pause
