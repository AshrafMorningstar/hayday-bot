//! # hd-core
//!
//! Core definitions, item catalogs, roadside pricing models, and thread-safe telemetry metrics.

pub mod catalog;
pub mod pricing;
pub mod state;

pub use catalog::*;
pub use pricing::*;
pub use state::*;
