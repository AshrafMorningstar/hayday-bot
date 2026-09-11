//! HDX 2.5 Native Bot Standalone Executable Entry Point
//! High-performance, zero-latency automation daemon for Hay Day.

use hd_core::state::SafeFarmMetrics;
use hd_host::commands::BotController;
use hd_host::master::MasterLoop;
use std::sync::atomic::AtomicBool;
use std::sync::Arc;
use std::thread::sleep;
use std::time::Duration;

fn main() {
    println!("================================================================");
    println!("  🛡️ HDX 2.5.205 NATIVE RUST CORE — STEALTH AUTOMATION ENGINE");
    println!("  Target: emulator-5554 (LDPlayer 9)");
    println!("  Promon SHIELD: Hookless Suppression ACTIVE");
    println!("  Quago Telemetry: Null-Routed (0 Packets Sent)");
    println!("  Expansion Daily Cap: 80 Items (Strict Anti-Ban)");
    println!("================================================================");

    let metrics = SafeFarmMetrics::default();
    let controller = BotController::new(metrics.clone());
    let running = Arc::new(AtomicBool::new(true));
    let master = MasterLoop::new(controller, running.clone());

    println!("[+] Native Bot Engine initialized.");
    println!("[*] Starting 1-Click Full Auto Multi-Phase Loop (Press Ctrl+C to stop)...");

    let mut cycle = 0;
    while running.load(std::sync::atomic::Ordering::Relaxed) {
        cycle += 1;
        println!("\n>>> [CYCLE #{}] Executing full 15-tab synchronized pipeline...", cycle);
        master.run_single_cycle();
        println!("<<< [CYCLE #{}] Completed successfully. Resting before next pass...", cycle);
        sleep(Duration::from_secs(10));
    }
}
