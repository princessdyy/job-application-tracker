@echo off
title MySQL Database Auto-Setup - Job Application Tracker
echo ========================================================
echo Automatic MySQL Database Setup Script
echo ========================================================
cd /d "%~dp0"

set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not exist "%PY_EXE%" (
    set "PY_EXE=python"
)

"%PY_EXE%" setup_mysql.py > setup_log.txt 2>&1
type setup_log.txt

echo.
pause
