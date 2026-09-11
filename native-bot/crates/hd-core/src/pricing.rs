//! Roadside Shop pricing calculation engine with humanized anti-ban offsets.

use rand::Rng;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum ShopPriceStrategy {
    Highest,
    Percent75,
    Half,
    Lowest,
    AntiBanMax,
    Custom(u32),
}

impl Default for ShopPriceStrategy {
    fn default() -> Self {
        ShopPriceStrategy::AntiBanMax
    }
}

pub fn calculate_shop_price(max_price: u32, count: u32, strategy: ShopPriceStrategy) -> u32 {
    let total_max = max_price * count.max(1);
    match strategy {
        ShopPriceStrategy::Highest => total_max,
        ShopPriceStrategy::Percent75 => (total_max as f64 * 0.75).round() as u32,
        ShopPriceStrategy::Half => (total_max as f64 * 0.50).round() as u32,
        ShopPriceStrategy::Lowest => count.max(1), // 1 coin per item
        ShopPriceStrategy::AntiBanMax => {
            let mut rng = rand::thread_rng();
            let jitter: u32 = rng.gen_range(1..=3);
            if total_max > jitter {
                total_max - jitter
            } else {
                total_max
            }
        }
        ShopPriceStrategy::Custom(val) => val,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_highest_price() {
        assert_eq!(calculate_shop_price(403, 10, ShopPriceStrategy::Highest), 4030);
    }

    #[test]
    fn test_lowest_price() {
        assert_eq!(calculate_shop_price(403, 10, ShopPriceStrategy::Lowest), 10);
    }

    #[test]
    fn test_half_price() {
        assert_eq!(calculate_shop_price(403, 10, ShopPriceStrategy::Half), 2015);
    }

    #[test]
    fn test_75_percent_price() {
        assert_eq!(calculate_shop_price(400, 10, ShopPriceStrategy::Percent75), 3000);
    }

    #[test]
    fn test_anti_ban_max() {
        let price = calculate_shop_price(403, 10, ShopPriceStrategy::AntiBanMax);
        assert!(price >= 4027 && price <= 4029);
    }
}
