//! Game item catalog, global IDs, and anti-ban limits.

use serde::{Deserialize, Serialize};

pub const EXPANSION_DAILY_CAP: u32 = 80;
pub const NEWSPAPER_SNAPSHOT_SIZE: usize = 200;
pub const DEFAULT_DAILY_DIAMOND_MINE_CAP: u32 = 10;
pub const DEFAULT_FEED_MILL_UNITS_PER_SLOT: u32 = 3;
pub const DEFAULT_SUGAR_MILL_UNITS_PER_SLOT: u32 = 3;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum ItemCategory {
    Crop,
    Product,
    Animal,
    TreeBush,
    Expansion,
    MiningTool,
    FishingLure,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameItem {
    pub id: u32,
    pub name: &'static str,
    pub category: ItemCategory,
    pub max_price: u32,
    pub default_price: u32,
    pub growth_or_production_seconds: u32,
}

pub static EXPANSION_MATERIALS: &[(&str, u32, u32)] = &[
    ("Land Deed", 27000001, 403),
    ("Mallet", 27000002, 403),
    ("Marker Stake", 27000003, 403),
    ("Bolt", 27000004, 270),
    ("Plank", 27000005, 270),
    ("Duct Tape", 27000006, 270),
    ("Box of Nails", 27000007, 270),
    ("Screw", 27000008, 270),
    ("Wood Panel", 27000009, 270),
];

pub static MINING_TOOLS: &[(&str, u32, u32)] = &[
    ("Dynamite", 27000010, 1),
    ("TNT", 27000011, 2),
    ("Shovel", 27000012, 3),
    ("Pickaxe", 27000013, 5),
];

pub static WOOD_CLEARING_TOOLS: &[(&str, u32)] = &[
    ("Saw", 27000014),
    ("Axe", 27000015),
];

pub static FISHING_CATALOG: &[(&str, u32)] = &[
    ("Red Lure", 28000001),
    ("Green Lure", 28000002),
    ("Blue Lure", 28000003),
    ("Purple Lure", 28000004),
    ("Gold Lure", 28000005),
    ("Lobster Trap", 28000006),
    ("Duck Net", 28000007),
];

pub fn is_expansion_material(global_id: u32) -> bool {
    EXPANSION_MATERIALS.iter().any(|(_, id, _)| *id == global_id)
}

pub fn get_expansion_max_price(global_id: u32) -> Option<u32> {
    EXPANSION_MATERIALS.iter().find(|(_, id, _)| *id == global_id).map(|(_, _, price)| *price)
}
