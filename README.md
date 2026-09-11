<div align="center">

# 🌾 Hay Day Bot & Auto-Farming Automation (LDPlayer 9)

### The Ultimate 100% Fully Autonomous In-Memory Farming Bot for Hay Day
**Evades Promon SHIELD • Disables Quago Anti-Cheat • Zero-Setup 1-Click Launch**

[![GitHub Stars](https://img.shields.io/github/stars/AshrafMorningstar/hayday-bot?style=for-the-badge&logo=github&color=gold)](https://github.com/AshrafMorningstar/hayday-bot/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/AshrafMorningstar/hayday-bot?style=for-the-badge&logo=github&color=blue)](https://github.com/AshrafMorningstar/hayday-bot/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Platform: Windows & LDPlayer](https://img.shields.io/badge/Platform-Windows%20%7C%20LDPlayer%209-brightgreen.svg?style=for-the-badge&logo=windows)](https://www.ldplayer.net/)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg?style=for-the-badge&logo=python)](https://python.org)

<br/>

⭐ **If this project helped you farm millions of coins and wheat, please STAR this repository!** ⭐  
*Your stars motivate continuous updates for the newest Hay Day patches!*

</div>

---

## 📖 Table of Contents
- [✨ Key Highlights](#-key-highlights)
- [🚀 1-Click Fast Start (Zero Configuration)](#-1-click-fast-start-zero-configuration)
- [🎮 Simple Commands & Controls](#-simple-commands--controls)
- [🛡️ Anti-Ban & Stealth Architecture](#️-anti-ban--stealth-architecture)
- [❓ Frequently Asked Questions & Troubleshooting](#-frequently-asked-questions--troubleshooting)
- [📈 Comparison with Traditional Bots](#-comparison-with-traditional-bots)
- [🔍 Search Tags & Keywords](#-search-tags--keywords)

---

## ✨ Key Highlights

Unlike traditional bots that rely on fragile image recognition (OpenCV) or slow mouse clicks, **hayday-bot** is an **internal in-memory automation suite**:

- 🌾 **Infinite Autonomous Wheat Farming:** Automatically harvests ready fields, replants wheat, applies human-like timing jitter, and loops seamlessly.
- ⚡ **Direct Memory Calling:** Calls internal game functions directly in the game process—instantaneous, accurate, and unaffected by screen resolution.
- 🏪 **Auto-Sell to Roadside Shop:** Lists excess inventory in roadside shop crates automatically to maximize gold earnings.
- 🛡️ **Stealth Anti-Detection:** Bypasses **Promon SHIELD** anti-tamper and intercepts/nullifies outbound **Quago** behavioral anti-cheat packets (`api.quago.io`).
- 🤖 **100% Automated Setup:** No manual file copying, no downloading Frida servers, and no complex configuration files. Double-click and play.

---

## 🚀 1-Click Fast Start (Zero Configuration)

### Step 1: Prepare LDPlayer 9
1. Open **[LDPlayer 9](https://www.ldplayer.net/)** (Android 9, 64-bit).
2. Go to LDPlayer **Settings (⚙️) ➔ Other (or Basic)**:
   - Turn **Root Permission** to **ENABLE**.
3. Launch **Hay Day** (`com.supercell.hayday`) and make sure your farm is on screen.

### Step 2: 1-Click Autonomous Launch
1. Download or clone this repository:
   ```bash
   git clone https://github.com/AshrafMorningstar/hayday-bot.git
   cd hayday-bot
   ```
2. **Double-click `install.bat`** (or `start_auto.bat`):
   - Automatically detects your Python environment and installs any missing libraries.
   - Automatically detects LDPlayer's ADB and connects to the emulator.
   - Automatically downloads, signature-patches, and stages Frida assets to the device.
   - Injects stealth runtime hooks, neutralizes Quago anti-cheat, and starts farming!

```text
======================================================
  inxernal - Automated Setup & Launcher
======================================================
[+] Python 3.12 detected
[+] Frida Python package verified
[+] ADB located: C:\LDPlayer\LDPlayer9\adb.exe
[+] Android emulator device connected (emulator-5554)
[+] Root access confirmed (su available)
[+] On-device stealth assets verified (/data/adb/nxrth-assets)
[+] Injected into com.supercell.hayday successfully!
[+] Quago anti-cheat telemetry blocked
[+] Auto-farming loop active: Harvesting -> Planting -> Sleeping (130s)
```

---

## 🎮 Simple Commands & Controls

The bot runs autonomously, but you can also control every aspect through the interactive `nxrth>` terminal:

```text
nxrth> nfields
[+] Found 48 fields ready for planting

nxrth> nharvest
[+] Harvested 48 fields!

nxrth> nplant 400001
[+] Planted Wheat (400001) on 48 fields!
```

### Essential Command Cheat Sheet

| Command | Action |
|:---|:---|
| `nfarm [seconds] [crop_id]` | **Main Auto Loop:** Harvests, replants, waits (default: 130s for wheat), and repeats. |
| `nharvest` | Harvests every ready field across your farm. |
| `nplant [crop_id]` | Plants specified crop (default `400001` = Wheat, `400002` = Corn). |
| `nfields` | Enumerates and displays all live field IDs on your farm. |
| `nsell <slot> <count> <price>` | Automatically lists items in your Roadside Shop. |
| `nquago status` | Shows anti-cheat blocker status and blocked upload packet counters. |
| `nstate` | Live game state: farm level, player ID, coins, and shop crates. |
| `nspoof on` / `off` | Spoofs hardware fingerprints to emulate a Samsung Galaxy S24 Ultra. |
| `quit` | Gracefully cleans up hooks and exits. |

---

## 🛡️ Anti-Ban & Stealth Architecture

Your account security is paramount:

1. **File-Backed Gadget Injection:** Injects stealth patched `libmetrics.so` rather than anonymous memory maps (`memfd`), bypassing memory scanner heuristics.
2. **Quago Telemetry Nullifier:** Intercepts Quago's network layer to drop behavioural analytics, preventing heuristic ban triggers.
3. **Randomized Humanized Jitter:** Injects microsecond Gaussian variations into gesture intervals and planting timings to simulate realistic human fingers.

---

## 📈 Comparison with Traditional Bots

| Feature | 🌾 hayday-bot (This Repo) | 📸 Image/OCR Bots | 📱 Auto-Clickers |
|:---|:---:|:---:|:---:|
| **Setup Difficulty** | **1-Click (Zero Setup)** | Complicated | Medium |
| **Speed** | **Instant (Native Memory)** | Slow (Screen Scrape) | Slow (Blind clicks) |
| **Screen Resolution Dependent** | ❌ No (Works on any size) | ✅ Yes (Breaks easily) | ✅ Yes |
| **Anti-Cheat Evasion** | **Promon + Quago Bypass** | ❌ None | ❌ None |
| **Crash Recovery** | **Automatic Watchdog** | ❌ Freezes | ❌ Clicks randomly |
| **Cost** | **100% Free & Open-Source** | Often Paid/Subscription | Free |

---

## ❓ Frequently Asked Questions & Troubleshooting

### Q1: The launcher says "No Android device detected"?
> Ensure LDPlayer 9 is running before launching `start_auto.bat`. Check that **Root Permission** is set to **Enable** in LDPlayer Settings ➔ Basic/Other.

### Q2: Game crashes on the very first start?
> Supercell's anti-tamper may occasionally exit during first initialization. Simply re-run `start_auto.bat`; once the stealth hooks attach, the session remains stable.

### Q3: Do I need to compile C++ or TypeScript?
> **No.** All precompiled bundles and native modules are included. Zero compilation required.

---

## 🌟 Show Your Support
If you love this project, please consider:
- Giving it a **Star ⭐** on GitHub!
- Sharing it with fellow farmers and automation enthusiasts!
- Submitting suggestions and pull requests.

---

## 🔍 Search Tags & Keywords
`hayday` • `hayday-bot` • `hay-day-bot` • `hayday-auto-farm` • `hay-day-auto-farm` • `hay-day-hack` • `hay-day-cheat` • `supercell-bot` • `ldplayer-hayday` • `wheat-farm-bot` • `hayday-script` • `frida-android` • `android-game-bot` • `hayday-macro` • `free-hayday-bot` • `auto-harvest-hayday` • `hayday-coins`

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).
