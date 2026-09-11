import urllib.request
import lzma
import subprocess
from pathlib import Path

url = 'https://github.com/frida/frida/releases/download/17.17.0/frida-server-17.17.0-android-x86_64.xz'
server_path = Path('frida_server_x86_64')
if not server_path.exists():
    print('Downloading frida-server-17.17.0-android-x86_64...')
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        data = lzma.decompress(resp.read())
    server_path.write_bytes(data)

adb = r'C:\LDPlayer\LDPlayer9\adb.exe'
dev = 'emulator-5554'
subprocess.run([adb, '-s', dev, 'push', str(server_path), '/data/local/tmp/test_server'], check=True)
subprocess.run([adb, '-s', dev, 'shell', 'su -c "chmod 755 /data/local/tmp/test_server"'], check=True)
r = subprocess.run([adb, '-s', dev, 'shell', 'su -c "/data/local/tmp/test_server --version"'], capture_output=True, text=True)
print('Frida server version on emulator:', r.stdout.strip())
