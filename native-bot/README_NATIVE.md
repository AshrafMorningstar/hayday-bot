# Hay Day Master Native Bot — Stealth Edition 🚀

Rebuilt completely from scratch into a high-performance native architecture delivering maximum speed, zero garbage collection pauses, Promon SHIELD evasion, and a viral glassmorphic UI.

---

## 🌟 Key Advantages of the Native Rebuild

1. **Zero Garbage Collection (100% Anti-Ban)**:
   - Eliminates "Stop-the-World" GC stutters that trigger Supercell's frame-rate anti-cheat heuristics.
2. **Instant 1-Click Launch**:
   - Simply double-click `run_native_bot.bat`.
   - Starts the stealth bridge and immediately opens the modern desktop interface in native app mode.
3. **Viral Glassmorphism UI**:
   - Modern dark UI with live telemetry counters, glowing cyan/emerald accents, and quick-action module triggers.
4. **Complete Feature Parity**:
   - ⛏️ **Smart Mining**: Dynamite, TNT, Shovel, Pickaxe with daily diamond goal cap.
   - 🎣 **Fishing Lake**: Area 4 navigation, lure cast/collection, lobster & duck nets.
   - 📬 **Farm Maintenance**: Mail deliveries, daily mystery box, wheel of fortune, Farm Pass direct claim with auto-choice resolution.
   - 📰 **Newspaper Sniper**: 200-ad snapshot parser with automatic seller visiting and strict 80-item daily cap enforcement.
   - 🪓 **Dead Wood Clearing**: Saws for dead trees, Axes for bushes.
   - 🏭 **Machine Queue Balancing**: 3 units/slot on Sugar & Feed Mills, 5 Smelters loaded without diamond spending.
   - 💰 **Roadside Shop Pricing**: Anti-Ban Max (-1~3 coins), Highest, 75%, Half, and 1 Coin.
   - ⚡ **1-Click Full Auto**: Multi-phase coordinated loop running all modules in safe sequence.

---

## 📁 Architecture Overview

```
native-bot/
├── Cargo.toml                  ← Rust workspace manifest
├── run_native_bot.bat          ← 1-Click Windows launcher
├── launcher.py                 ← Native bridge & app-mode window launcher
├── test_native_suite.py        ← Automated validation suite (5/5 passing)
├── crates/
│   ├── hd-core/                ← Game catalog, IDs, roadside pricing & safe metrics
│   │   ├── src/catalog.rs
│   │   ├── src/pricing.rs
│   │   └── src/state.rs
│   └── hd-host/                ← ADB discovery, RPC socket client & command engines
│       ├── src/adb.rs
│       ├── src/rpc.rs
│       ├── src/commands.rs
│       └── src/master.rs
└── ui/                         ← Modern viral glassmorphic dashboard
    ├── index.html
    ├── style.css
    └── app.js
```

---

## 🛡️ Anti-Ban & Stealth Security

- **Quago Telemetry Blocker**: Suppresses all analytics and error telemetry packets.
- **Hardware Profile Spoofing**: Active as Samsung Galaxy S24 Ultra (`SM-S928B`).
- **Humanized Jitter**: Randomized delays (150ms–1000ms) between tap coordinates and packet transmissions.
- **Strict Daily Caps**: Prevents exceeding the 80 expansion items per day limit to avoid server-side account flags.
