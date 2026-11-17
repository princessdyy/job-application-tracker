@echo off
title Launching MySQL Workbench
echo ========================================================
echo Searching and Launching MySQL Workbench...
echo ========================================================

:: Standard 64-bit paths
if exist "C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe" (
    echo [OK] Found MySQL Workbench CE.
    start "" "C:\Program Files\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe"
    exit /b 0
)

if exist "C:\Program Files\MySQL\MySQL Workbench 8.0\MySQLWorkbench.exe" (
    echo [OK] Found MySQL Workbench.
    start "" "C:\Program Files\MySQL\MySQL Workbench 8.0\MySQLWorkbench.exe"
    exit /b 0
)

if exist "C:\Program Files (x86)\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe" (
    echo [OK] Found MySQL Workbench (x86).
    start "" "C:\Program Files (x86)\MySQL\MySQL Workbench 8.0 CE\MySQLWorkbench.exe"
    exit /b 0
)

:: Try from PATH
start "" "MySQLWorkbench.exe" 2>nul
if %errorlevel% equ 0 exit /b 0

echo.
echo [!] Could not automatically locate MySQLWorkbench.exe.
echo Please open MySQL Workbench from your Windows Start Menu.
echo.
pause
