//! ADB detection, port forwarding, and emulator discovery.

use std::path::{Path, PathBuf};
use std::process::Command;

pub struct AdbManager {
    pub adb_path: PathBuf,
    pub device_serial: Option<String>,
}

impl AdbManager {
    pub fn auto_discover() -> Option<Self> {
        // Standard paths for LDPlayer 9, LDPlayer 4, Nox, and system adb
        let candidates = [
            r"C:\LDPlayer\LDPlayer9\adb.exe",
            r"C:\leidian\LDPlayer9\adb.exe",
            r"C:\Program Files\Microvirt\MEmu\adb.exe",
            r"C:\Program Files\BlueStacks_nxt\HD-Adb.exe",
        ];

        let mut chosen_path = None;
        for path_str in candidates {
            let p = Path::new(path_str);
            if p.exists() {
                chosen_path = Some(p.to_path_buf());
                break;
            }
        }

        // Fallback to adb in PATH
        if chosen_path.is_none() {
            if let Ok(output) = Command::new("where").arg("adb").output() {
                if output.status.success() {
                    let out_str = String::from_utf8_lossy(&output.stdout);
                    if let Some(first_line) = out_str.lines().next() {
                        chosen_path = Some(PathBuf::from(first_line.trim()));
                    }
                }
            }
        }

        let adb = chosen_path?;
        let mut manager = Self {
            adb_path: adb,
            device_serial: None,
        };

        manager.refresh_devices();
        Some(manager)
    }

    pub fn refresh_devices(&mut self) -> Option<String> {
        let output = Command::new(&self.adb_path)
            .args(["devices"])
            .output()
            .ok()?;

        let out_str = String::from_utf8_lossy(&output.stdout);
        for line in out_str.lines().skip(1) {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 2 && parts[1] == "device" {
                self.device_serial = Some(parts[0].to_string());
                return self.device_serial.clone();
            }
        }
        None
    }

    pub fn forward_port(&self, local_port: u16, remote_port: u16) -> bool {
        let mut cmd = Command::new(&self.adb_path);
        if let Some(ref serial) = self.device_serial {
            cmd.args(["-s", serial]);
        }
        cmd.args([
            "forward",
            &format!("tcp:{}", local_port),
            &format!("tcp:{}", remote_port),
        ]);

        cmd.status().map(|s| s.success()).unwrap_or(false)
    }
}
