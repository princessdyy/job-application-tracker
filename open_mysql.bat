@echo off
title Launching MySQL Workbench
echo ========================================================
echo Searching and Launching MySQL Workbench...
echo ========================================================

:: Check standard 64-bit install path
if exist "C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe" (
    echo Found at: C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe
    start "" "C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe"
    exit
)

if exist "C:\Program Files\MySQL\MySQL Workbench 8.0\MySQLWorkbench.exe" (
    echo Found at: C:\Program Files\MySQL\MySQL Workbench 8.0\MySQLWorkbench.exe
    start "" "C:\Program Files\MySQL\MySQL Workbench 8.0\MySQLWorkbench.exe"
    exit
)

if exist "C:\Program Files (x86)\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe" (
    echo Found at: C:\Program Files (x86)\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe
    start "" "C:\Program Files (x86)\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe"
    exit
)

:: Try running from Windows PATH
start "" "MySQLWorkbench.exe" 2>nul
if %errorlevel% equ 0 exit

echo.
echo [!] Could not locate MySQL Workbench in standard folders.
echo If it is not installed yet, please download it from:
echo https://dev.mysql.com/downloads/workbench/
echo.
pause
