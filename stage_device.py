"""
stage_device.py - Autonomous on-device asset provisioner
Stages .service (frida-server) and libmetrics.so (patched Frida Gadget)
into /data/adb/nxrth-assets/ on the Android emulator.
"""

import sys
import os
import subprocess
import hashlib
import urllib.request
import lzma
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ASSET_DIR = "/data/adb/nxrth-assets"
GADGET_SHA256 = "cfd21e76394bcf86481707754720c3d279016066e71aadeeef26d6ecdff4f981"
SERVER_SHA256 = "b34a33bdbcd2f737ef59811ca57a4c2675a528b7ffae71acd4c35337d3cb93f5"

ADB_SEARCH = [
    r"C:\LDPlayer\LDPlayer9\adb.exe",
    r"C:\LDPlayer\LDPlayer14\adb.exe",
    r"C:\Program Files\LDPlayer\LDPlayer9\adb.exe",
    r"C:\Program Files (x86)\LDPlayer\LDPlayer9\adb.exe",
    "adb"
]

def find_adb():
    for p in ADB_SEARCH:
        try:
            r = subprocess.run([p, "version"], capture_output=True, text=True, timeout=5)
            if r.returncode == 0:
                return p
        except Exception:
            continue
    return None

def find_device(adb):
    try:
        r = subprocess.run([adb, "devices"], capture_output=True, text=True, timeout=5)
        for line in r.stdout.strip().splitlines()[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 2 and parts[1] == "device":
                if "127.0.0.1" in parts[0] or "emulator" in parts[0]:
                    return parts[0]
        for line in r.stdout.strip().splitlines()[1:]:
            parts = line.strip().split("\t")
            if len(parts) >= 2 and parts[1] == "device":
                return parts[0]
    except Exception:
        pass
    return None

def ensure_gadget():
    out_path = PROJECT_DIR / "libmetrics.so"
    if out_path.exists():
        if hashlib.sha256(out_path.read_bytes()).hexdigest() == GADGET_SHA256:
            return out_path

    print("  [*] Preparing libmetrics.so (patched Frida Gadget 17.17.0 x86_64)...")
    url = "https://github.com/frida/frida/releases/download/17.17.0/frida-gadget-17.17.0-android-x86_64.so.xz"
    raw_path = PROJECT_DIR / "gadget_raw.so"
    if not raw_path.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            raw_path.write_bytes(lzma.decompress(resp.read()))

    patch_script = PROJECT_DIR / "tests" / "patch_gadget.py"
    subprocess.run([sys.executable, str(patch_script), str(raw_path), str(out_path)], check=True)
    return out_path

def ensure_server():
    server_path = PROJECT_DIR / "frida_server_x86_64"
    if server_path.exists():
        if hashlib.sha256(server_path.read_bytes()).hexdigest() == SERVER_SHA256:
            return server_path

    print("  [*] Downloading frida-server 17.17.0 x86_64...")
    url = "https://github.com/frida/frida/releases/download/17.17.0/frida-server-17.17.0-android-x86_64.xz"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        server_path.write_bytes(lzma.decompress(resp.read()))
    return server_path

def stage_assets(adb=None, device=None):
    if not adb:
        adb = find_adb()
    if not adb:
        print("  [!] ADB not found.")
        return False
    if not device:
        device = find_device(adb)
    if not device:
        print("  [!] No Android device / emulator found.")
        return False

    gadget = ensure_gadget()
    server = ensure_server()

    print(f"  [*] Staging assets to {device}:{ASSET_DIR}...")
    def run_adb(*args):
        return subprocess.run([adb, "-s", device] + list(args), capture_output=True, text=True)

    def su(cmd):
        return subprocess.run([adb, "-s", device, "shell", f"su -c '{cmd}'"], capture_output=True, text=True)

    su(f"mkdir -p {ASSET_DIR}")

    # Stage .service
    run_adb("push", str(server), "/data/local/tmp/.service")
    su(f"cp /data/local/tmp/.service {ASSET_DIR}/.service")
    su(f"chmod 755 {ASSET_DIR}/.service")
    su("rm -f /data/local/tmp/.service")

    # Stage libmetrics.so
    run_adb("push", str(gadget), "/data/local/tmp/libmetrics.so")
    su(f"cp /data/local/tmp/libmetrics.so {ASSET_DIR}/libmetrics.so")
    su(f"chmod 644 {ASSET_DIR}/libmetrics.so")
    su("rm -f /data/local/tmp/libmetrics.so")

    # Verify
    r_srv = su(f"test -x {ASSET_DIR}/.service && echo YES || echo NO")
    r_gad = su(f"test -r {ASSET_DIR}/libmetrics.so && echo YES || echo NO")

    if "YES" in (r_srv.stdout or "") and "YES" in (r_gad.stdout or ""):
        print("  [+] Assets successfully staged in /data/adb/nxrth-assets/!")
        return True
    else:
        print("  [!] Staging verification failed.")
        return False

if __name__ == "__main__":
    success = stage_assets()
    sys.exit(0 if success else 1)
