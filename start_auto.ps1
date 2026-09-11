# start_auto.ps1 - inxernal auto-launch (PowerShell)
# Right-click -> "Run with PowerShell"  or  .\start_auto.ps1
# Optional args: -Wait 90 -Crop 400002 -NoLaunch

param(
    [int]$Wait        = 130,
    [int]$Crop        = 400001,
    [switch]$MasterAuto,
    [switch]$NoLaunch
)

$Host.UI.RawUI.WindowTitle = "inxernal - Auto Launcher"

function Find-Python {
    $candidates = @(
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python39\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python39\python.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) {
            $v = & $p --version 2>&1
            if ($v -match "Python 3\.(9|1[0-9])") { return $p }
        }
    }
    $fromPath = Get-Command python -ErrorAction SilentlyContinue
    if ($fromPath) {
        $v = & $fromPath.Source --version 2>&1
        if ($v -match "Python 3\.(9|1[0-9])") { return $fromPath.Source }
    }
    return $null
}

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host "   inxernal  |  Auto-Setup & Farm Launcher" -ForegroundColor Cyan
Write-Host "   discord.gg/nxrth  |  Hay Day" -ForegroundColor Cyan
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $ScriptDir

$py = Find-Python
if (-not $py) {
    Write-Host "  [!] Python 3.9+ not found." -ForegroundColor Red
    Write-Host "  [!] Install from https://python.org and re-run." -ForegroundColor Red
    Read-Host "  Press Enter to exit"
    exit 1
}

Write-Host "  [+] Python: $py" -ForegroundColor Green
Write-Host ""

$setupArgs = @("setup.py", "--wait", $Wait, "--crop", $Crop)
if ($MasterAuto) { $setupArgs += "--master-auto" }
if ($NoLaunch) { $setupArgs += "--no-launch" }

& $py @setupArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "  [!] Setup failed. Fix errors above and re-run." -ForegroundColor Red
    Read-Host "  Press Enter to exit"
    exit 1
}
