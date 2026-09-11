"""
build_exe.py - Standalone Single-File Windows Executable Compiler
================================================================
Compiles Hay Day Master Bot into a high-performance, single-file Windows .exe
using PyInstaller with all required metadata, runtime hooks, and assets.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build():
    project_dir = Path(__file__).resolve().parent
    dist_dir = project_dir / "dist"
    build_dir = project_dir / "build"
    
    print("================================================================")
    print("   BUILDING HAY DAY MASTER BOT STANDALONE EXECUTABLE (.EXE)     ")
    print("================================================================")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name=HayDayMasterBot",
        "--onedir",  # onedir is much faster to launch and avoids temp extraction overhead
        "--add-data=game_ids.py;.",
        "--add-data=gadget.config.json;.",
        "--hidden-import=frida",
        "--hidden-import=tkinter",
        "--hidden-import=json",
        "--hidden-import=socket",
        "--hidden-import=threading",
        "--hidden-import=queue",
        "app_main.py"
    ]

    print(f"Executing: {' '.join(cmd)}")
    ret = subprocess.run(cmd, cwd=str(project_dir))
    if ret.returncode == 0:
        exe_path = dist_dir / "HayDayMasterBot" / "HayDayMasterBot.exe"
        print(f"\n[+] BUILD SUCCESSFUL!")
        print(f"[+] Output Executable: {exe_path}")
        print("================================================================\n")
    else:
        print(f"\n[-] Build failed with exit code: {ret.returncode}\n")
    return ret.returncode

if __name__ == "__main__":
    sys.exit(build())
