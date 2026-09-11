#Requires -Version 5.1
<#
.SYNOPSIS
    inxernal Full Auto Installer
.DESCRIPTION
    Installs ALL requirements for inxernal fully automatically:
      Python 3.11, Node.js LTS, frida, npm packages, JS bundles.
    Then verifies LDPlayer ADB and Android device, and launches loader.py --auto.
.PARAMETER NoLaunch
    Run all setup steps but do NOT launch the loader at the end.
.PARAMETER Wait
    Farm cycle wait in seconds (default 130).
.PARAMETER Crop
    Crop item ID (default 400001 = wheat).
.PARAMETER Force
    Re-install even if already installed.
#>
param(
    [switch]$NoLaunch,
    [int]$Wait  = 130,
    [int]$Crop  = 400001,
    [switch]$Force
)

Set-StrictMode -Off
$ErrorActionPreference = "SilentlyContinue"

# -- ANSI colours (Win10+) -----------------------------------------------------
$ESC = [char]27
function Write-OK   ($m) { Write-Host "  ${ESC}[92m[OK]${ESC}[0m  $m" }
function Write-Warn ($m) { Write-Host "  ${ESC}[93m[!]${ESC}[0m  $m" }
function Write-Err  ($m) { Write-Host "  ${ESC}[91m[X]${ESC}[0m  $m" }
function Write-Info ($m) { Write-Host "  ${ESC}[96m[>]${ESC}[0m  $m" }
function Write-Step ($n,$t,$m) {
    Write-Host ""
    Write-Host "  ${ESC}[1m${ESC}[94m[$n/$t]${ESC}[0m ${ESC}[1m$m${ESC}[0m"
    Write-Host "  $('-' * 50)"
}

$BANNER = @"

${ESC}[96m${ESC}[1m  +==================================================+
  |   inxernal  -  Full Auto Installer               |
  |   discord.gg/nxrth  |  Hay Day                   |
  +==================================================+${ESC}[0m
"@

Write-Host $BANNER

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$Loader    = Join-Path $ScriptDir "loader.py"
$SetupPy   = Join-Path $ScriptDir "setup.py"
$TOTAL     = 8
$Errors    = [System.Collections.Generic.List[string]]::new()

# ------------------------------------------------------------------------------
# Helper: run winget silently with accepted agreements
function Invoke-Winget {
    param([string[]]$Args)
    $allArgs = $Args + @(
        "--accept-package-agreements",
        "--accept-source-agreements",
        "--source", "winget"
    )
    $r = & winget @allArgs 2>&1
    return $LASTEXITCODE, ($r -join "`n")
}

# Helper: find a real (non-Store-alias) Python 3.9+ exe
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
    # Also search PATH entries
    ($env:PATH -split ";") | ForEach-Object {
        if ($_) { $candidates += (Join-Path $_ "python.exe") }
    }
    foreach ($exe in $candidates) {
        if (-not (Test-Path $exe)) { continue }
        try {
            $v = & $exe --version 2>&1
            if ($v -match "Python (3\.(9|1[0-9])\.\d+)") {
                return $exe, $Matches[1]
            }
        } catch {}
    }
    return $null, $null
}

# Helper: find node.exe
function Find-Node {
    $candidates = @(
        "C:\Program Files\nodejs\node.exe",
        "C:\Program Files (x86)\nodejs\node.exe",
        "$env:APPDATA\nvm\current\node.exe"
    )
    ($env:PATH -split ";") | ForEach-Object {
        if ($_) { $candidates += (Join-Path $_ "node.exe") }
    }
    foreach ($exe in $candidates) {
        if (Test-Path $exe) {
            try {
                $v = & $exe --version 2>&1
                if ($v -match "v\d+") { return $exe, $v }
            } catch {}
        }
    }
    return $null, $null
}

# Helper: find npm
function Find-Npm {
    $candidates = @(
        "C:\Program Files\nodejs\npm.cmd",
        "C:\Program Files (x86)\nodejs\npm.cmd"
    )
    ($env:PATH -split ";") | ForEach-Object {
        if ($_) {
            $candidates += (Join-Path $_ "npm.cmd")
            $candidates += (Join-Path $_ "npm")
        }
    }
    foreach ($exe in $candidates) {
        if (Test-Path $exe) { return $exe }
    }
    return $null
}

# Helper: refresh PATH from registry (after installs)
function Update-EnvPath {
    $machine = [System.Environment]::GetEnvironmentVariable("PATH","Machine") 
    $user    = [System.Environment]::GetEnvironmentVariable("PATH","User")
    $env:PATH = "$machine;$user"
}

# -- ADB helpers ---------------------------------------------------------------
$ADB_PATHS = @(
    "C:\LDPlayer\LDPlayer9\adb.exe",
    "C:\LDPlayer\LDPlayer14\adb.exe",
    "C:\Program Files\LDPlayer\LDPlayer9\adb.exe",
    "C:\Program Files (x86)\LDPlayer\LDPlayer9\adb.exe",
    "C:\Program Files\Netease\MuMuPlayer\nx_main\adb.exe"
)

function Find-Adb {
    foreach ($p in $ADB_PATHS) {
        if (Test-Path $p) {
            $r = & $p version 2>&1
            if ($LASTEXITCODE -eq 0) { return $p }
        }
    }
    $fromPath = Get-Command adb -ErrorAction SilentlyContinue
    if ($fromPath) { return $fromPath.Source }
    return $null
}

function Get-Device ($adb) {
    $lines = (& $adb devices 2>&1) -split "`n"
    foreach ($line in $lines[1..($lines.Length)]) {
        $line = $line.Trim()
        if ($line -match "^(\S+)\s+device$") {
            $id = $Matches[1]
            if ($id -match "127\.0\.0\.1|emulator") { return $id }
        }
    }
    foreach ($line in $lines[1..($lines.Length)]) {
        if ($line -match "^(\S+)\s+device$") { return $Matches[1] }
    }
    return $null
}

function Test-RemoteFile ($adb, $device, $path, [switch]$Executable) {
    $flag = if ($Executable) { "-x" } else { "-e" }
    $inner = "test $flag $path && echo YES || echo NO"
    $r = & $adb -s $device shell "su -c '$inner'" 2>&1
    return ($r -join " ") -match "YES"
}

function Test-Root ($adb, $device) {
    $r = & $adb -s $device shell "su -c id" 2>&1
    return ($r -join "") -match "uid=0"
}

# ==============================================================================
#  STEP 1 - Python
# ==============================================================================
Write-Step 1 $TOTAL "Python 3.11"

$pyExe, $pyVer = Find-Python
if ($pyExe -and -not $Force) {
    Write-OK "Python $pyVer  ->  $pyExe"
} else {
    if ($Force) { Write-Info "Force flag: re-installing Python..." }
    else        { Write-Warn "Python 3.9+ not found. Installing via winget..." }
    
    Write-Info "Running: winget install Python.Python.3.11 --silent"
    $code, $out = Invoke-Winget @("install","--id","Python.Python.3.11","--silent")
    
    Update-EnvPath
    $pyExe, $pyVer = Find-Python
    
    if ($pyExe) {
        Write-OK "Python $pyVer installed  ->  $pyExe"
    } else {
        Write-Err "Python install FAILED."
        Write-Err "Manual fix: https://python.org/downloads  (check 'Add to PATH')"
        $Errors.Add("python")
    }
}

# ==============================================================================
#  STEP 2 - pip / frida
# ==============================================================================
Write-Step 2 $TOTAL "frida Python package"

if ($pyExe -and "python" -notin $Errors) {
    # Check if already installed
    $fridaVer = & $pyExe -c "import frida; print(frida.__version__)" 2>&1
    if ($LASTEXITCODE -eq 0 -and $fridaVer -match "\d") {
        if (-not $Force) {
            Write-OK "frida $fridaVer (already installed)"
        } else {
            Write-Info "Force: upgrading frida..."
            & $pyExe -m pip install --upgrade frida --quiet 2>&1 | Out-Null
            $fridaVer = & $pyExe -c "import frida; print(frida.__version__)" 2>&1
            Write-OK "frida $fridaVer"
        }
    } else {
        Write-Info "Installing frida..."
        # Ensure pip is up to date first
        & $pyExe -m pip install --upgrade pip --quiet 2>&1 | Out-Null
        $pipResult = & $pyExe -m pip install frida 2>&1
        $fridaVer  = & $pyExe -c "import frida; print(frida.__version__)" 2>&1
        if ($LASTEXITCODE -eq 0 -and $fridaVer -match "\d") {
            Write-OK "frida $fridaVer installed"
        } else {
            Write-Err "frida install FAILED."
            Write-Err "Manual fix:  $pyExe -m pip install frida"
            $Errors.Add("frida")
        }
    }
} else {
    Write-Warn "Skipped (Python missing)"
}

# ==============================================================================
#  STEP 3 - Node.js
# ==============================================================================
Write-Step 3 $TOTAL "Node.js LTS (for JS bundle build)"

$nodeExe, $nodeVer = Find-Node
$npmExe            = Find-Npm

if ($nodeExe -and $npmExe -and -not $Force) {
    Write-OK "Node.js $nodeVer  ->  $nodeExe"
    Write-OK "npm found  ->  $npmExe"
} else {
    if ($Force) { Write-Info "Force flag: re-installing Node.js..." }
    else        { Write-Info "Node.js not found. Installing via winget..." }
    
    $code, $out = Invoke-Winget @("install","--id","OpenJS.NodeJS.LTS","--silent")
    Update-EnvPath
    
    $nodeExe, $nodeVer = Find-Node
    $npmExe            = Find-Npm
    
    if ($nodeExe) {
        Write-OK "Node.js $nodeVer installed"
        Write-OK "npm  ->  $(if($npmExe){$npmExe}else{'(in PATH)'})"
    } else {
        Write-Warn "Node.js install may need a terminal restart to appear in PATH."
        Write-Warn "JS bundles will be skipped if Node.js isn't found."
    }
}

# ==============================================================================
#  STEP 4 - npm packages + JS bundle build
# ==============================================================================
Write-Step 4 $TOTAL "npm packages + JS bundles (java_guard / quago_probe)"

$bundlesReady = (Test-Path (Join-Path $ScriptDir "java_guard.bundle.js")) -and
                (Test-Path (Join-Path $ScriptDir "quago_probe.bundle.js"))

if ($bundlesReady -and -not $Force) {
    Write-OK "java_guard.bundle.js   present"
    Write-OK "quago_probe.bundle.js  present"
} else {
    $npmCmd = $npmExe
    if (-not $npmCmd) { $g = Get-Command npm -ErrorAction SilentlyContinue; if ($g) { $npmCmd = $g.Source } }
    
    if ($npmCmd) {
        Write-Info "Running: npm install..."
        $r = & $npmCmd install 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-OK "npm install done"
        } else {
            Write-Warn "npm install had warnings (may still work)"
        }
        
        Write-Info "Building java_guard bundle..."
        $r = & $npmCmd run build:java-guard 2>&1
        if ($LASTEXITCODE -eq 0) { Write-OK "java_guard.bundle.js built" }
        else { Write-Warn "java_guard build failed: $($r[-1])"; Write-Warn "Loader will work without it (SHIELD guard disabled)" }
        
        Write-Info "Building quago_probe bundle..."
        $r = & $npmCmd run build:quago 2>&1
        if ($LASTEXITCODE -eq 0) { Write-OK "quago_probe.bundle.js built" }
        else { Write-Warn "quago_probe build failed: $($r[-1])"; Write-Warn "Loader will work without it (Quago blocking disabled)" }
    } else {
        Write-Warn "npm not available. Skipping JS bundle build."
        Write-Warn "Install Node.js from https://nodejs.org then re-run install.bat"
        if (-not $bundlesReady) {
            Write-Warn "Pre-built bundles missing - Quago blocking and SHIELD guard disabled."
        }
    }
}

# ==============================================================================
#  STEP 5 - Project files
# ==============================================================================
Write-Step 5 $TOTAL "Core project files"

$required = @(
    "loader.py", "hook.js", "gadget.config.json",
    "native/build/libnxrth.so"
)
$missing = $required | Where-Object { -not (Test-Path (Join-Path $ScriptDir $_)) }

if (-not $missing) {
    Write-OK "All core project files present ($($required.Count) files)"
} else {
    foreach ($f in $missing) {
        Write-Err "MISSING: $f"
    }
    if ("native/build/libnxrth.so" -in $missing) {
        Write-Warn "libnxrth.so missing -> run: powershell native/build.ps1  (needs Android NDK r27c)"
    }
    $Errors.AddRange([string[]]$missing)
}

# ==============================================================================
#  STEP 6 - ADB / LDPlayer
# ==============================================================================
Write-Step 6 $TOTAL "ADB / LDPlayer 9"

$adbExe = Find-Adb
if ($adbExe) {
    Write-OK "adb  ->  $adbExe"
} else {
    Write-Err "ADB not found. Is LDPlayer 9 installed?"
    Write-Err "Install LDPlayer 9 from https://ldplayer.net"
    $Errors.Add("adb")
}

# ==============================================================================
#  STEP 7 - Android device, root, on-device assets
# ==============================================================================
Write-Step 7 $TOTAL "Android device, root & on-device assets"

$ASSET_VAULT = "/data/adb/nxrth-assets"
$FRIDA_BIN   = "$ASSET_VAULT/.service"
$GADGET_BIN  = "$ASSET_VAULT/libmetrics.so"

if ($adbExe) {
    $device = Get-Device $adbExe
    if ($device) {
        Write-OK "Device: $device"
        
        if (Test-Root $adbExe $device) {
            Write-OK "Rooted (su works)"
        } else {
            Write-Err "Device NOT rooted."
            Write-Err "Enable: LDPlayer > 3-dot menu > Settings > Root"
            $Errors.Add("root")
        }
        
        $srvOk = Test-RemoteFile $adbExe $device $FRIDA_BIN -Executable
        $gadOk = Test-RemoteFile $adbExe $device $GADGET_BIN
        if (-not $srvOk -or -not $gadOk) {
            Write-Info "Auto-staging on-device assets (Frida server & Gadget)..."
            if ($pyExe) {
                & $pyExe (Join-Path $ScriptDir "stage_device.py")
                $srvOk = Test-RemoteFile $adbExe $device $FRIDA_BIN -Executable
                $gadOk = Test-RemoteFile $adbExe $device $GADGET_BIN
            }
        }
        
        if ($srvOk) {
            Write-OK "Frida server:  $FRIDA_BIN"
        } else {
            Write-Err "Frida server MISSING: $FRIDA_BIN"
            $Errors.Add("frida-server")
        }
        
        if ($gadOk) {
            Write-OK "Frida gadget:  $GADGET_BIN"
        } else {
            Write-Err "Frida gadget MISSING: $GADGET_BIN"
            $Errors.Add("frida-gadget")
        }
    } else {
        Write-Err "No device found. Start LDPlayer 9 and enable ADB (Settings > ADB debugging)."
        $Errors.Add("device")
    }
} else {
    Write-Warn "Skipped (adb missing)"
}

# ==============================================================================
#  STEP 8 - Summary & Launch
# ==============================================================================
Write-Step 8 $TOTAL "Summary & Launch"

$blocking = $Errors | Where-Object {
    $_ -in @("python","frida","root","frida-server","frida-gadget",
             "device","adb","loader.py","hook.js","native/build/libnxrth.so")
}

if ($blocking) {
    Write-Host ""
    Write-Host "  ${ESC}[91m${ESC}[1m  SETUP INCOMPLETE${ESC}[0m  Fix the following before launching:"
    foreach ($e in $blocking) { Write-Err "  $e" }
    Write-Host ""
    Write-Host "  Re-run install.bat after fixing the above."
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "  ${ESC}[92m${ESC}[1m  ALL CHECKS PASSED!${ESC}[0m"
Write-Host ""

if ($NoLaunch) {
    Write-Warn "-NoLaunch: skipping loader start."
    Write-Host ""
    exit 0
}

Write-Host "  ${ESC}[96m${ESC}[1m$('=' * 50)"
Write-Host "  Launching  loader.py --auto  (wait=${Wait}s, crop=${Crop})"
Write-Host "  $('=' * 50)${ESC}[0m"
Write-Host ""

Start-Sleep -Seconds 1

$loadCmd = @($pyExe, $Loader, "--auto", "--auto-wait", $Wait, "--auto-crop", $Crop)
& $loadCmd[0] $loadCmd[1..($loadCmd.Length-1)]
exit $LASTEXITCODE
