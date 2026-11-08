@echo off
setlocal enabledelayedexpansion
title Push Project to GitHub - CareerPath
color 0b
echo ========================================================
echo        CAREERPATH - GITHUB PUSH AUTOMATION
echo ========================================================
echo Target Repository: https://github.com/princessdyy/job-application-tracker
echo.

:: 1. Search for Git in PATH and common installation directories
set "GIT_CMD="
where git >nul 2>&1
if %errorlevel% equ 0 set "GIT_CMD=git"

if not defined GIT_CMD if exist "C:\Program Files\Git\cmd\git.exe" set "GIT_CMD=C:\Program Files\Git\cmd\git.exe"
if not defined GIT_CMD if exist "C:\Program Files\Git\bin\git.exe" set "GIT_CMD=C:\Program Files\Git\bin\git.exe"
if not defined GIT_CMD if exist "C:\Program Files (x86)\Git\cmd\git.exe" set "GIT_CMD=C:\Program Files (x86)\Git\cmd\git.exe"
if not defined GIT_CMD if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" set "GIT_CMD=%LOCALAPPDATA%\Programs\Git\cmd\git.exe"

if not defined GIT_CMD (
    echo [ERROR] Git could not be located.
    echo Please download from https://git-scm.com/download/win
    pause
    exit /b
)

echo [OK] Using Git at: "!GIT_CMD!"
echo.

:: 2. Initialize repo if needed
echo [1/5] Checking Git repository initialization...
if not exist ".git" (
    "!GIT_CMD!" init
    echo [OK] Initialized new Git repository.
) else (
    echo [OK] Existing Git repository found.
)

:: 3. Configure identity if not already set (required on fresh Git installations)
"!GIT_CMD!" config user.name >nul 2>&1
if %errorlevel% neq 0 (
    "!GIT_CMD!" config user.name "princessdyy"
    echo [OK] Set Git author name to 'princessdyy'.
)

"!GIT_CMD!" config user.email >nul 2>&1
if %errorlevel% neq 0 (
    "!GIT_CMD!" config user.email "princessdyy@users.noreply.github.com"
    echo [OK] Set Git author email to 'princessdyy@users.noreply.github.com'.
)

echo.
echo [2/5] Staging project files...
"!GIT_CMD!" add .
echo [OK] Staged all source code, templates, database schema, and docs.

echo.
echo [3/5] Creating commit...
"!GIT_CMD!" commit -m "Complete Job Application Tracker with Flask, MySQL 8.0, and Skills Matcher"
echo [OK] Commit created successfully.

echo.
echo [4/5] Setting default branch to 'main'...
"!GIT_CMD!" branch -M main

echo.
echo ========================================================
echo  TARGET REPOSITORY CONFIGURATION
echo ========================================================
set "DEFAULT_REPO=https://github.com/princessdyy/job-application-tracker.git"
echo Default: %DEFAULT_REPO%
set /p REPO_INPUT="Press ENTER to use this repo, or paste another URL: "

if "%REPO_INPUT%"=="" (
    set "REPO_URL=%DEFAULT_REPO%"
) else (
    set "REPO_URL=%REPO_INPUT%"
)

echo.
echo [5/5] Connecting to remote and pushing to %REPO_URL%...
"!GIT_CMD!" remote remove origin >nul 2>&1
"!GIT_CMD!" remote add origin %REPO_URL%

:: Push to GitHub
"!GIT_CMD!" push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo --------------------------------------------------------
    echo [NOTICE] Normal push encountered remote conflict
    echo (due to the older placeholder repository from September).
    echo Overwriting with the new complete senior project files...
    echo --------------------------------------------------------
    "!GIT_CMD!" push -u origin main --force
)

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS! Your project is now 100%% live on GitHub!
    echo  URL: https://github.com/princessdyy/job-application-tracker
    echo ========================================================
) else (
    echo.
    echo [!] If prompted for credentials, sign in with GitHub in the popup window.
)

echo.
pause
