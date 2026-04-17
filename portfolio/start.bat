@echo off
title Ahmad Ansar — Portfolio
cd /d "%~dp0"
echo.
echo  Portfolio Site
echo  ==============
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found.
    pause
    exit /b 1
)

echo  Installing dependencies...
python -m pip install flask flask-limiter gunicorn -q --disable-pip-version-check

echo  Starting at http://127.0.0.1:5051
echo  Press Ctrl+C to stop.
echo.
start "" "http://127.0.0.1:5051"
python app.py
pause
