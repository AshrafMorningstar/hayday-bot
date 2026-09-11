//! Bot runtime state, telemetry metrics, and anti-ban daily limits.

use serde::{Deserialize, Serialize};
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::Arc;

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct FarmStats {
    pub crops_harvested: u32,
    pub animals_collected: u32,
    pub items_produced: u32,
    pub trees_chopped: u32,
    pub fish_caught: u32,
    pub ore_mined: u32,
    pub diamonds_mined: u32,
    pub newspaper_tools_sniped: u32,
    pub coins_earned: u32,
    pub maintenance_tasks_completed: u32,
}

#[derive(Clone)]
pub struct SafeFarmMetrics {
    pub crops: Arc<AtomicU32>,
    pub animals: Arc<AtomicU32>,
    pub items: Arc<AtomicU32>,
    pub trees: Arc<AtomicU32>,
    pub fish: Arc<AtomicU32>,
    pub ore: Arc<AtomicU32>,
    pub diamonds: Arc<AtomicU32>,
    pub sniped_tools: Arc<AtomicU32>,
    pub coins: Arc<AtomicU32>,
    pub maintenance: Arc<AtomicU32>,
    pub daily_expansion_sniped: Arc<AtomicU32>,
}

impl Default for SafeFarmMetrics {
    fn default() -> Self {
        Self {
            crops: Arc::new(AtomicU32::new(0)),
            animals: Arc::new(AtomicU32::new(0)),
            items: Arc::new(AtomicU32::new(0)),
            trees: Arc::new(AtomicU32::new(0)),
            fish: Arc::new(AtomicU32::new(0)),
            ore: Arc::new(AtomicU32::new(0)),
            diamonds: Arc::new(AtomicU32::new(0)),
            sniped_tools: Arc::new(AtomicU32::new(0)),
            coins: Arc::new(AtomicU32::new(0)),
            maintenance: Arc::new(AtomicU32::new(0)),
            daily_expansion_sniped: Arc::new(AtomicU32::new(0)),
        }
    }
}

impl SafeFarmMetrics {
    pub fn can_snipe_expansion(&self) -> bool {
        self.daily_expansion_sniped.load(Ordering::Relaxed) < crate::catalog::EXPANSION_DAILY_CAP
    }

    pub fn record_expansion_sniped(&self, count: u32) -> bool {
        let current = self.daily_expansion_sniped.load(Ordering::Relaxed);
        if current + count <= crate::catalog::EXPANSION_DAILY_CAP {
            self.daily_expansion_sniped.fetch_add(count, Ordering::Relaxed);
            self.sniped_tools.fetch_add(count, Ordering::Relaxed);
            true
        } else {
            false
        }
    }

    pub fn snapshot(&self) -> FarmStats {
        FarmStats {
            crops_harvested: self.crops.load(Ordering::Relaxed),
            animals_collected: self.animals.load(Ordering::Relaxed),
            items_produced: self.items.load(Ordering::Relaxed),
            trees_chopped: self.trees.load(Ordering::Relaxed),
            fish_caught: self.fish.load(Ordering::Relaxed),
            ore_mined: self.ore.load(Ordering::Relaxed),
            diamonds_mined: self.diamonds.load(Ordering::Relaxed),
            newspaper_tools_sniped: self.sniped_tools.load(Ordering::Relaxed),
            coins_earned: self.coins.load(Ordering::Relaxed),
            maintenance_tasks_completed: self.maintenance.load(Ordering::Relaxed),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_daily_expansion_cap() {
        let metrics = SafeFarmMetrics::default();
        assert!(metrics.can_snipe_expansion());
        assert!(metrics.record_expansion_sniped(50));
        assert!(metrics.can_snipe_expansion());
        assert!(metrics.record_expansion_sniped(30));
        // Hit 80 cap
        assert!(!metrics.can_snipe_expansion());
        assert!(!metrics.record_expansion_sniped(1));
    }
}
