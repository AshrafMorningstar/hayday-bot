"""
app_main.py - Unified One-Click Master Launcher for Hay Day Bot & Memory Gate
==============================================================================
Launches the full graphical user interface (GUI) or autonomous CLI daemon.
Enforces stealth Anti-Ban Quago blocking and hardware spoofing by default.
"""

import os
import sys
import subprocess
import threading
import time

def ensure_environment():
    """Ensure stealth environment variables are enforced for 100% anti-ban safety."""
    os.environ.setdefault("NX_QUAGO", "1")  # Block telemetry uploads to api.quago.io
    # Add current folder to sys.path so modules resolve in frozen executable
    app_dir = os.path.dirname(os.path.abspath(__file__))
    if app_dir not in sys.path:
        sys.path.insert(0, app_dir)

def main():
    ensure_environment()
    
    # If launched with CLI flags, route to loader console
    if any(arg in sys.argv for arg in ("--cli", "--headless", "--master-auto", "--auto", "-m")):
        from loader import NXRTHConsole
        console = NXRTHConsole()
        sys.exit(console.run())
    else:
        # Default: Launch rich dark-mode GUI
        import tkinter as tk
        from gui import HayDayBotGUI
        root = tk.Tk()
        app = HayDayBotGUI(root)
        root.mainloop()

if __name__ == "__main__":
    main()
