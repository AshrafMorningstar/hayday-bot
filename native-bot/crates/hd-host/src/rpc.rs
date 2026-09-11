//! Direct socket RPC client for the injected game engine.

use serde::{Deserialize, Serialize};
use std::io::{Read, Write};
use std::net::TcpStream;
use std::time::Duration;

#[derive(Debug, Serialize, Deserialize)]
pub struct RpcCommand {
    pub cmd: String,
    #[serde(default)]
    pub params: serde_json::Value,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RpcResponse {
    pub success: bool,
    #[serde(default)]
    pub data: serde_json::Value,
    #[serde(default)]
    pub error: Option<String>,
}

pub struct RpcClient {
    port: u16,
    stream: Option<TcpStream>,
}

impl RpcClient {
    pub fn new(port: u16) -> Self {
        Self { port, stream: None }
    }

    pub fn connect(&mut self) -> bool {
        match TcpStream::connect_timeout(
            &format!("127.0.0.1:{}", self.port).parse().unwrap(),
            Duration::from_millis(1500),
        ) {
            Ok(stream) => {
                let _ = stream.set_read_timeout(Some(Duration::from_secs(3)));
                let _ = stream.set_write_timeout(Some(Duration::from_secs(3)));
                self.stream = Some(stream);
                true
            }
            Err(_) => false,
        }
    }

    pub fn send_command(&mut self, cmd: &str, params: serde_json::Value) -> Option<RpcResponse> {
        let req = RpcCommand {
            cmd: cmd.to_string(),
            params,
        };

        let mut payload = serde_json::to_vec(&req).ok()?;
        payload.push(b'\n');

        let stream = self.stream.as_mut()?;
        stream.write_all(&payload).ok()?;
        stream.flush().ok()?;

        let mut buffer = [0u8; 4096];
        let bytes_read = stream.read(&mut buffer).ok()?;
        if bytes_read == 0 {
            return None;
        }

        serde_json::from_slice(&buffer[..bytes_read]).ok()
    }
}
