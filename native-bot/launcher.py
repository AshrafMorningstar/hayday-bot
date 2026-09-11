"""
Native Bot Universal Launcher
Starts local stealth bridge and launches the ultra-modern glassmorphic interface.
"""

import os
import sys
import webbrowser
import threading
import http.server
import socketserver

PORT = 49152
UI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui")

class StealthHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def log_message(self, format, *args):
        # Silent logs to keep console clean
        pass

def start_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), StealthHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    url = f"http://127.0.0.1:{PORT}/index.html"
    print("=" * 60)
    print("  HAY DAY MASTER BOT — NATIVE STEALTH EDITION")
    print(f"  Interface Live: {url}")
    print("  Stealth Promon Evasion: ACTIVE")
    print("  Zero-Click Auto-Setup: ACTIVE")
    print("=" * 60)

    # Launch in app mode using Edge/Chrome if available, otherwise default browser
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    launched = False
    for edge in edge_paths:
        if os.path.exists(edge):
            os.system(f'start "" "{edge}" --app={url} --window-size=1380,920')
            launched = True
            break

    if not launched:
        webbrowser.open(url)

    # Keep alive
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
