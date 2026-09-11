"""
setup.py - inxernal auto-setup & launcher
==========================================
Run this once (or every time) to automatically:
  1. Verify / locate Python 3.9+
  2. Install frida (pip install frida)
  3. Find LDPlayer ADB
  4. Check the Android device is connected & rooted
  5. Verify all project assets are in place
  6. Launch loader.py --auto  (fully autonomous farm mode)

Usage:
    Double-click  start_auto.bat
    -- or --
    python setup.py
    python setup.py --no-launch      (check only, dont start loader)
    python setup.py --wait 200       (custom farm wait seconds)
    python setup.py --crop 400002    (custom crop id)
"""

import sys
import os
import subprocess
import shutil
import json
import re
import time
import argparse
from pathlib import Path

# colour helpers
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleMode(
        ctypes.windll.kernel32.GetStdHandle(-11), 7)
except Exception:
    pass

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BLUE   = "\033[94m"
DIM    = "\033[2m"

def ok(msg):    print(f"  {GREEN}OK{RESET}  {msg}")
def warn(msg):  print(f"  {YELLOW}!{RESET}   {msg}")
def err(msg):   print(f"  {RED}ERR{RESET} {msg}")
def info(msg):  print(f"  {CYAN}->{RESET}  {msg}")
def step(n, total, msg):
    print(f"\n{BOLD}{BLUE}[{n}/{total}]{RESET} {BOLD}{msg}{RESET}")

BANNER = """
+======================================================+
|       inxernal  .  auto-setup & launcher             |
|           discord.gg/nxrth  .  Hay Day               |
+======================================================+
"""

PROJECT_DIR  = Path(__file__).resolve().parent
LOADER       = PROJECT_DIR / "loader.py"
ADB_PATHS    = [
    r"C:\LDPlayer\LDPlayer9\adb.exe",
    r"C:\LDPlayer\LDPlayer14\adb.exe",
    r"C:\Program Files\LDPlayer\LDPlayer9\adb.exe",
    r"C:\Program Files (x86)\LDPlayer\LDPlayer9\adb.exe",
    r"C:\Program Files\Netease\MuMuPlayer\nx_main\adb.exe",
    "adb",
]
REQUIRED_FILES = [
    "loader.py",
    "hook.js",
    "java_guard.bundle.js",
    "quago_probe.bundle.js",
    "gadget.config.json",
    "native/build/libnxrth.so",
]
ASSET_VAULT  = "/data/adb/nxrth-assets"
FRIDA_BIN    = f"{ASSET_VAULT}/.service"
GADGET_VAULT = f"{ASSET_VAULT}/libmetrics.so"


def find_python():
    """Return (exe, version_str) for Python 3.9+, or (None, None)."""
    candidates = [sys.executable, shutil.which("python"), shutil.which("python3")]
    for p in os.environ.get("PATH", "").split(os.pathsep):
        for name in ("python.exe", "python3.exe"):
            candidates.append(os.path.join(p, name))
    for exe in candidates:
        if not exe:
            continue
        try:
            r = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                m = re.search(r"Python (\d+)\.(\d+)", r.stdout + r.stderr)
                if m and (int(m.group(1)), int(m.group(2))) >= (3, 9):
                    return exe, f"{m.group(1)}.{m.group(2)}"
        except Exception:
            continue
    return None, None


def install_python_winget():
    try:
        info("Trying winget install Python 3.11...")
        r = subprocess.run(
            ["winget", "install", "--id", "Python.Python.3.11",
             "--silent", "--accept-package-agreements", "--accept-source-agreements"],
            timeout=300
        )
        return r.returncode == 0
    except Exception:
        return False


def ensure_frida(python_exe):
    r = subprocess.run([python_exe, "-c", "import frida; print(frida.__version__)"],
                       capture_output=True, text=True, timeout=15)
    if r.returncode == 0 and r.stdout.strip():
        return True, r.stdout.strip()
    info("frida not found. Installing via pip...")
    subprocess.run([python_exe, "-m", "pip", "install", "frida", "--quiet"], timeout=180)
    r2 = subprocess.run([python_exe, "-c", "import frida; print(frida.__version__)"],
                        capture_output=True, text=True, timeout=10)
    if r2.returncode == 0:
        return True, r2.stdout.strip()
    return False, None


def find_adb():
    for p in ADB_PATHS:
        try:
            r = subprocess.run([p, "version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                return p
        except Exception:
            continue
    return None


def run_adb(adb_exe, *args, timeout=10):
    try:
        return subprocess.run([adb_exe] + list(args), capture_output=True, text=True, timeout=timeout)
    except Exception:
        return None


def find_device(adb_exe):
    r = run_adb(adb_exe, "devices")
    if not r:
        return None
    for line in r.stdout.strip().splitlines()[1:]:
        line = line.strip()
        if not line or "offline" in line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2 and parts[1] == "device":
            if "127.0.0.1" in parts[0] or "emulator" in parts[0]:
                return parts[0]
    for line in r.stdout.strip().splitlines()[1:]:
        parts = line.strip().split("\t")
        if len(parts) >= 2 and parts[1] == "device":
            return parts[0]
    return None


def su_run(adb_exe, device, cmd, timeout=10):
    return run_adb(adb_exe, "-s", device, "shell", f"su -c '{cmd}'", timeout=timeout)


def check_root(adb_exe, device):
    r = su_run(adb_exe, device, "id")
    return r and "uid=0" in (r.stdout or "")


def check_remote_file(adb_exe, device, path, executable=False):
    flag = "-x" if executable else "-e"
    r = su_run(adb_exe, device, f"test {flag} {path} && echo YES || echo NO")
    return r and "YES" in (r.stdout or "")


def check_project_files():
    return [f for f in REQUIRED_FILES if not (PROJECT_DIR / f).exists()]


def check_npm_built():
    return all((PROJECT_DIR / b).exists() for b in ["java_guard.bundle.js", "quago_probe.bundle.js"])


def try_npm_build():
    npm = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm:
        return False
    if subprocess.run([npm, "install"], cwd=str(PROJECT_DIR), capture_output=True, timeout=120).returncode != 0:
        return False
    for s in ("build:java-guard", "build:quago"):
        if subprocess.run([npm, "run", s], cwd=str(PROJECT_DIR), capture_output=True, timeout=120).returncode != 0:
            return False
    return True


def parse_args():
    p = argparse.ArgumentParser(description="inxernal auto-setup & launcher")
    p.add_argument("--no-launch", action="store_true", help="Checks only, do not launch.")
    p.add_argument("--wait",  type=int, default=130,    help="Farm cycle wait seconds (default 130).")
    p.add_argument("--crop",  type=int, default=400001, help="Crop id (default 400001 = wheat).")
    return p.parse_args()


def main():
    args = parse_args()
    print(BANNER)
    TOTAL = 7
    errors = []

    # Step 1 - Python
    step(1, TOTAL, "Python 3.9+")
    python_exe, py_ver = find_python()
    if python_exe:
        ok(f"Python {py_ver}  ->  {python_exe}")
    else:
        warn("Python 3.9+ not found. Trying winget auto-install...")
        if install_python_winget():
            python_exe, py_ver = find_python()
            if python_exe:
                ok(f"Python {py_ver} installed.")
            else:
                err("Python still missing after winget. Install manually: https://python.org")
                errors.append("python")
        else:
            err("Auto-install failed. Install Python 3.9+ from https://python.org")
            errors.append("python")

    # Step 2 - frida
    step(2, TOTAL, "frida Python package")
    if python_exe and "python" not in errors:
        ok_frida, frida_ver = ensure_frida(python_exe)
        if ok_frida:
            ok(f"frida {frida_ver}")
        else:
            err("Could not install frida.  Run:  pip install frida")
            errors.append("frida")
    else:
        warn("Skipped (Python missing)")

    # Step 3 - Project files
    step(3, TOTAL, "Project files")
    missing = check_project_files()
    if not missing:
        ok(f"All {len(REQUIRED_FILES)} required files present")
    else:
        for f in missing:
            err(f"Missing: {f}")
        if "native/build/libnxrth.so" in missing:
            warn("libnxrth.so missing - build it:  powershell native/build.ps1  (needs NDK r27c)")
        errors.extend(missing)

    # Step 4 - JS bundles
    step(4, TOTAL, "JS bundles (java_guard / quago_probe)")
    if check_npm_built():
        ok("java_guard.bundle.js  OK   quago_probe.bundle.js  OK")
    else:
        warn("Bundles missing - trying npm build...")
        if try_npm_build():
            ok("npm build succeeded")
        else:
            warn("Could not build bundles. Install Node.js, then: npm install && npm run build:java-guard && npm run build:quago")
            warn("(Loader will still work; Quago probe will be disabled)")

    # Step 5 - ADB
    step(5, TOTAL, "ADB / LDPlayer")
    adb_exe = find_adb()
    if adb_exe:
        ok(f"adb  ->  {adb_exe}")
    else:
        err("adb not found. Is LDPlayer 9 installed?")
        errors.append("adb")

    # Step 6 - Device
    step(6, TOTAL, "Android device (LDPlayer)")
    device = None
    if adb_exe:
        device = find_device(adb_exe)
        if device:
            ok(f"Device: {device}")
            if check_root(adb_exe, device):
                ok("Rooted (su ok)")
            else:
                err("Device NOT rooted. Enable root in LDPlayer > Settings > Root.")
                errors.append("root")
            srv_ok = check_remote_file(adb_exe, device, FRIDA_BIN, executable=True)
            gad_ok = check_remote_file(adb_exe, device, GADGET_VAULT)
            if not (srv_ok and gad_ok):
                info("Auto-staging on-device assets (/data/adb/nxrth-assets)...")
                try:
                    import stage_device
                    stage_device.stage_assets(adb_exe, device)
                except Exception as ex:
                    warn(f"Auto-staging warning: {ex}")
                srv_ok = check_remote_file(adb_exe, device, FRIDA_BIN, executable=True)
                gad_ok = check_remote_file(adb_exe, device, GADGET_VAULT)

            if srv_ok:
                ok(f"Frida server: {FRIDA_BIN}")
            else:
                err(f"Frida server missing: {FRIDA_BIN}")
                errors.append("frida-server")

            if gad_ok:
                ok(f"Frida gadget: {GADGET_VAULT}")
            else:
                err(f"Frida gadget missing: {GADGET_VAULT}")
                errors.append("frida-gadget")
        else:
            err("No device found. Start LDPlayer 9 with ADB enabled.")
            errors.append("device")
    else:
        warn("Skipped (adb missing)")

    # Step 7 - Launch
    step(7, TOTAL, "Summary & Launch")
    blocking = [e for e in errors if e in (
        "python", "frida", "root", "frida-server", "frida-gadget",
        "device", "adb", "loader.py", "hook.js", "native/build/libnxrth.so"
    )]

    if blocking:
        print(f"\n  SETUP INCOMPLETE - fix the errors above before launching.")
        print(f"  Blocking: {', '.join(blocking)}\n")
        return 1

    print(f"\n  All checks passed!")

    if args.no_launch:
        print("  --no-launch: not starting loader.\n")
        return 0

    print(f"\n" + "="*54)
    print(f"  Launching loader.py --auto  (wait={args.wait}s, crop={args.crop})")
    print("="*54 + "\n")
    time.sleep(1)

    cmd = [
        python_exe, str(LOADER),
        "--auto",
        "--auto-wait", str(args.wait),
        "--auto-crop",  str(args.crop),
    ]
    try:
        os.execv(cmd[0], cmd)
    except (AttributeError, OSError):
        subprocess.run(cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
