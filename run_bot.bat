@echo off
title Hay Day Master Bot - 1-Click Launch
cd /d "%~dp0"

echo ================================================================
echo        HAY DAY MASTER BOT - 1-CLICK AUTOMATION LAUNCHER
echo ================================================================
echo.

:: Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python was not detected in PATH.
    echo [!] Please install Python 3.10+ from python.org or Windows Store.
    pause
    exit /b 1
)

:: Ensure required packages are present
echo [*] Verifying dependencies...
python -c "import frida" >nul 2>&1
if errorlevel 1 (
    echo [*] Installing required Python libraries (frida, frida-tools)...
    python -m pip install --quiet frida frida-tools
)

:: Set Stealth Anti-Ban environment
set NX_QUAGO=1

:: Start the Master GUI
echo [*] Starting Hay Day Master Bot UI...
start "" python app_main.py

echo [+] Master Bot launched successfully!
exit /b 0
