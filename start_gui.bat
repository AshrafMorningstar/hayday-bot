@echo off
setlocal
title Hay Day Bot - GUI Controller
color 0B

echo ========================================================
echo    HAY DAY BOT - GRAPHICAL USER INTERFACE (GUI)        
echo ========================================================
echo.

:: Check python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python was not found in PATH.
    echo [*] Please run install.bat first.
    pause
    exit /b 1
)

echo [*] Starting Hay Day Bot GUI...
start "" python gui.py

echo [✓] GUI window launched!
exit /b 0
