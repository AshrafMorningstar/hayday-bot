# inxernal 🌾

[![Automation: 100%](https://img.shields.io/badge/Automation-100%25%20Fully%20Auto-brightgreen.svg)](#quick-start)
[![Target: LDPlayer 9](https://img.shields.io/badge/Target-LDPlayer%209%20(x86__64)-blue.svg)](https://www.ldplayer.net/)
[![Game: Hay Day](https://img.shields.io/badge/Game-Hay%20Day-orange.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An internal automation tool for **Hay Day** (`com.supercell.hayday`) running on **LDPlayer 9** (Android 9, x86_64). It injects into the game process, evades **Promon SHIELD** anti-tamper, directly triggers internal game routines (plant, harvest, sell), intercepts **Quago** behavioral anti-cheat telemetry, and provides a fully autonomous farming loop.

---

## ⚡ Quick Start (100% Fully Automatic)

You do **not** need to manually download Frida servers, type complex terminal commands, or edit device files. Everything is automated.

### 1. Prerequisites
- **Windows PC** (Windows 10 or 11)
- **[LDPlayer 9](https://www.ldplayer.net/)** (Android 9, x86_64)
  - In LDPlayer Settings ⚙️ ➔ **Basic** / **Other**: Turn **Root Permission** to **ENABLE**.
  - Install **Hay Day** and log into your farm once.
- **Python 3.9+** (if not installed, `install.bat` will offer to install it automatically via winget).

---

### 2. 1-Click Launch

1. **Start LDPlayer 9** and make sure your farm is loaded on screen.
2. **Double-click `install.bat`** (or `start_auto.bat`):
   - Automatically detects Python, ADB, and your running emulator.
   - Automatically installs Frida dependencies.
   - Automatically downloads, patches, and stages device binaries (`.service` and `libmetrics.so`).
   - Automatically connects injector, bypasses protection, and launches the autonomous farm!

```
[+] Python 3.12 detected
[+] Frida Python package verified
[+] Core project files verified
[+] ADB located: C:\LDPlayer\LDPlayer9\adb.exe
[+] Android emulator device connected (emulator-5554)
[+] Device root access confirmed (su available)
[+] On-device assets verified and staged (/data/adb/nxrth-assets)
[+] Launching autonomous farm...
```

---

## 🕹️ Interactive Console Commands

While the auto-farm is running in the background, the interactive `nxrth>` console remains active for live control and diagnostics:

```
nxrth> nfields
[+] Found 48 fields ready for planting

nxrth> nfarm 130 400001
[+] Auto-farm loop started (Wheat, 130s cycle)
```

### Core Commands Reference

| Command | Description |
|---|---|
| `nfarm [wait] [crop]` | **Auto-farm loop:** Automatically harvests ready fields, replants crops, applies humanized jitter, and repeats indefinitely. |
| `nharvest` | Harvests all ready fields instantly. |
| `nplant [crop_id]` | Plants specified crop across all fields (default: `400001` for Wheat). |
| `nfields` | Enumerates all active field IDs on the farm screen. |
| `nsell <slot> [count] [price]` | Lists items in your Roadside Shop crate. |
| `nquago status` | Shows Quago behavioral telemetry block status and dropped request counts. |
| `nstate` | Displays live farm state (level, screen, shop slots, player ID). |
| `nspoof on / off` | Toggles device hardware fingerprint spoofing (emulates Galaxy S24 Ultra). |
| `quit` | Gracefully detaches hooks, stops threads, and exits. |

---

## 🛡️ Anti-Detection & Safety

- **Promon SHIELD Bypass:** File-backed Frida Gadget (`libmetrics.so`) injection avoids in-memory `frida-agent` memfd signatures.
- **Quago Anti-Cheat Neutralization:** Automatically intercepts and drops outbound telemetry packets sent to `api.quago.io`.
- **Humanized Behavioral Jitter:** Randomizes harvest/plant delays and gesture timing to prevent algorithmic pattern detection.

---

## 🔧 Alternative Launchers

Prefer PowerShell or command line flags? Several entry points are available:

- **PowerShell:**
  ```powershell
  .\start_auto.ps1 -Wait 130 -Crop 400001
  ```
- **Python Direct:**
  ```bash
  python setup.py --auto --wait 130 --crop 400001
  ```
- **Dry-run / Verification Only:**
  ```bash
  python setup.py --no-launch
  ```

---

## ❓ Frequently Asked Questions (FAQ)

### Q: LDPlayer shows "No device detected"?
> Make sure LDPlayer 9 is running before launching `start_auto.bat`. Check that **Root Permission** is enabled in LDPlayer Settings.

### Q: Game crashed on the very first start?
> This can happen during initial process spawning while Promon SHIELD hooks are settling. Simply restart `start_auto.bat` — it will resume smoothly.

### Q: Do I need to manually transfer files to the emulator?
> **No.** `stage_device.py` handles binary fetching, marker patching, and `/data/adb/nxrth-assets/` staging automatically.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
