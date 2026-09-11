@echo off
title inxernal - Auto Launcher
color 0A
echo.
echo  ================================================
echo   inxernal  ^|  Auto-Setup ^& Farm Launcher
echo   discord.gg/nxrth  ^|  Hay Day
echo  ================================================
echo.

REM -- Try to find a working Python --
set PY=
for %%E in (
  "C:\Python312\python.exe"
  "C:\Python311\python.exe"
  "C:\Python310\python.exe"
  "C:\Python39\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
  "%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
) do (
  if exist %%E (
    set PY=%%E
    goto :found_python
  )
)

REM -- Try PATH --
where python >nul 2>&1 && set PY=python && goto :found_python
where python3 >nul 2>&1 && set PY=python3 && goto :found_python

echo  [!] Python not found.
echo  [!] Please install Python 3.9+ from https://python.org
echo  [!] Then re-run this file.
pause
exit /b 1

:found_python
echo  [+] Python found: %PY%
echo.
echo  [*] Running setup checks and launching auto-farm...
echo.

cd /d "%~dp0"
%PY% setup.py %*

if errorlevel 1 (
  echo.
  echo  [!] Setup failed. See errors above.
  pause
)

