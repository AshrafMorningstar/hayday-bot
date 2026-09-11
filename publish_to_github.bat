@echo off
setlocal
title inxernal - GitHub Dual-Repository Publisher
color 0B

echo ======================================================
echo   inxernal - GitHub Dual-Repository Publisher
echo ======================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [-] Python not found in PATH. Checking default install paths...
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
        set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    ) else (
        echo [-] Could not find Python. Please install Python 3.9+ from https://python.org
        pause
        exit /b 1
    )
) else (
    set "PY_BIN=python"
)

"%PY_BIN%" "%~dp0publish_to_github.py" %*

if %errorlevel% neq 0 (
    echo.
    echo [-] Publisher encountered an error.
    pause
    exit /b %errorlevel%
)

echo.
echo [+] Done! Press any key to close this window.
pause >nul
