@echo off
setlocal EnableDelayedExpansion
title inxernal - Full Auto Installer
color 0A

echo.
echo  ##################################################
echo  ##                                              ##
echo  ##    inxernal  -  Full Auto Installer          ##
echo  ##    discord.gg/nxrth  ^|  Hay Day              ##
echo  ##                                              ##
echo  ##################################################
echo.
echo  This installer will automatically:
echo    [1] Install Python 3.11
echo    [2] Install Node.js LTS
echo    [3] Install frida Python package
echo    [4] Build JS bundles (java_guard / quago_probe)
echo    [5] Verify LDPlayer ^& ADB
echo    [6] Check Android device root ^& assets
echo    [7] Launch the auto-farm
echo.
echo  Starting in 3 seconds (or press any key to start now)...
timeout /t 3 >nul 2>&1

echo.
echo  [*] Launching installer...
echo.

REM -- Run the PowerShell installer --------------------------------------------
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*

set EXIT_CODE=%ERRORLEVEL%
if %EXIT_CODE% NEQ 0 (
    echo.
    echo  [!] Installer exited with code %EXIT_CODE%.
    echo  [!] Review the output above and fix any errors.
    echo.
    pause
)
exit /b %EXIT_CODE%
