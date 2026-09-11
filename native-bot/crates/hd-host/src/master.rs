//! Master 1-Click Autonomous Loop with multi-phase sector coordination and humanized timing jitter.

use crate::commands::BotController;
use rand::Rng;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread::sleep;
use std::time::Duration;

pub struct MasterLoop {
    pub bot: BotController,
    pub running: Arc<AtomicBool>,
}

impl MasterLoop {
    pub fn new(bot: BotController, running: Arc<AtomicBool>) -> Self {
        Self { bot, running }
    }

    pub fn run_single_cycle(&self) {
        if !self.running.load(Ordering::Relaxed) {
            return;
        }

        let mut rng = rand::thread_rng();

        // Phase 1: Harvest & Replant Crops
        self.bot.cmd_harvest_all();
        sleep(Duration::from_millis(rng.gen_range(200..400)));

        // Phase 2: Collect & Feed Animals
        if !self.running.load(Ordering::Relaxed) { return; }
        self.bot.cmd_collect_animals();
        sleep(Duration::from_millis(rng.gen_range(200..400)));

        // Phase 3: Dead Wood Clearing (Saws & Axes)
        if !self.running.load(Ordering::Relaxed) { return; }
        self.bot.cmd_chop_all();
        sleep(Duration::from_millis(rng.gen_range(200..400)));

        // Phase 4: Machine Queue Balancing (Mills & Smelters)
        if !self.running.load(Ordering::Relaxed) { return; }
        self.bot.cmd_produce_machines();
        sleep(Duration::from_millis(rng.gen_range(200..400)));

        // Phase 5: Smart Mining (with diamond cap)
        if !self.running.load(Ordering::Relaxed) { return; }
        self.bot.cmd_mine(10);
        sleep(Duration::from_millis(rng.gen_range(200..400)));

        // Phase 6: Fishing Lake Navigation
        if !self.running.load(Ordering::Relaxed) { return; }
        self.bot.cmd_fishing();
        sleep(Duration::from_millis(rng.gen_range(200..400)));

        // Phase 7: Farm Maintenance Suite (Mail, Box, Wheel, Farm Pass)
        if !self.running.load(Ordering::Relaxed) { return; }
        self.bot.cmd_maintenance();
        sleep(Duration::from_millis(rng.gen_range(200..400)));

        // Phase 8: Newspaper Rare Tool Sniping (within 80/day limit)
        if !self.running.load(Ordering::Relaxed) { return; }
        self.bot.cmd_newspaper_sniper();
        sleep(Duration::from_millis(rng.gen_range(500..1000)));
    }
}
