@echo off
title HDX 2.5 Native Master Bot — 1-Click Turnkey Launcher
cls
color 0B
echo ====================================================================
echo   HAY DAY MASTER BOT — HDX 2.5 NATIVE STEALTH EDITION
echo ====================================================================
echo   [1] Launch HDX 2.5 Modern Desktop App (15 Tabs + Full Auto UI)
echo   [2] Run Standalone Ultra-Fast Native Rust Daemon (hd-host.exe)
echo   [3] Run Automated Verification Test Suite (37/37 Tests)
echo ====================================================================
set /p choice="Select an option [Default=1]: "

if "%choice%"=="2" (
    echo [*] Starting Standalone Native Rust Engine...
    "%~dp0native-bot\target\release\hd-host.exe"
) else if "%choice%"=="3" (
    echo [*] Executing Full Test Suite...
    python "%~dp0native-bot\test_native_suite.py"
    python "%~dp0test_farm_commands.py"
    pause
) else (
    echo [*] Starting HDX 2.5 Modern Desktop App & Engine...
    python "%~dp0native-bot\launcher.py"
)
