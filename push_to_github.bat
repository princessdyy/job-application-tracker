@echo off
title Push Project to GitHub - CareerPath
color 0b
cd /d "%~dp0"
echo ========================================================
echo        CAREERPATH - GITHUB PUSH AUTOMATION
echo ========================================================
echo.

set "GIT_EXE=C:\Program Files\Git\cmd\git.exe"
if not exist "%GIT_EXE%" (
    where git >nul 2>&1
    if %errorlevel% equ 0 (
        set "GIT_EXE=git"
    ) else (
        echo [ERROR] Git not found at C:\Program Files\Git\cmd\git.exe
        pause
        exit /b
    )
)

echo [OK] Using Git at: "%GIT_EXE%"
echo.

echo [1/4] Configuring Git identity and upload buffer...
"%GIT_EXE%" config user.name "princessdyy"
"%GIT_EXE%" config user.email "princessdyy@users.noreply.github.com"
"%GIT_EXE%" config http.postBuffer 524288000

echo.
echo [2/4] Staging and committing files...
"%GIT_EXE%" add .
"%GIT_EXE%" commit -m "Add project demo video and latest updates"

echo.
echo [3/4] Renaming branch to main...
"%GIT_EXE%" branch -M main

echo.
echo [4/4] Connecting to GitHub and pushing to repository...
"%GIT_EXE%" remote remove origin 2>nul
"%GIT_EXE%" remote add origin https://github.com/princessdyy/job-application-tracker.git

echo.
echo Pushing code to https://github.com/princessdyy/job-application-tracker ...
echo.
"%GIT_EXE%" push -u origin main --force

echo.
if %errorlevel% equ 0 (
    echo ========================================================
    echo  SUCCESS! Your project is now 100%% live on GitHub!
    echo  URL: https://github.com/princessdyy/job-application-tracker
    echo ========================================================
) else (
    echo ========================================================
    echo  If a browser popup appeared, please sign in to GitHub.
    echo ========================================================
)
echo.
echo Press any key to close this window.
pause
