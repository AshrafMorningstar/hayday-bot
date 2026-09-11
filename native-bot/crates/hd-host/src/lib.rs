//! # hd-host
//!
//! Host orchestrator, ADB auto-discovery, RPC socket client, smart automation commands, and 1-click master loop.

pub mod adb;
pub mod commands;
pub mod master;
pub mod rpc;

pub use adb::*;
pub use commands::*;
pub use master::*;
pub use rpc::*;
