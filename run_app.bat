@echo off
title Job Application Tracker Server
echo ========================================================
echo Starting Job Application Tracker Web Application...
echo ========================================================
cd /d "%~dp0"

:: Target Python 3.12 directly to avoid Microsoft Store app execution alias
set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY_EXE%" (
    set "PY_EXE=py"
)

echo Using Python at: "%PY_EXE%"
echo [1/2] Installing requirements...
"%PY_EXE%" -m pip install -r requirements.txt

echo.
echo [2/2] Starting Flask Web Server...
echo Application will be running at: http://127.0.0.1:5000
echo.
echo Opening browser in 3 seconds...
start /b "" cmd /c "timeout /t 3 /nobreak >nul && start http://127.0.0.1:5000"

"%PY_EXE%" app.py
pause
