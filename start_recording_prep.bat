@echo off
title Job Application Tracker Server
cd /d "%~dp0"

echo ========================================================
echo Launching MySQL Workbench + CareerPath Flask Server...
echo ========================================================
echo.

call open_mysql.bat
call run_app.bat
