//! TLS configuration for connecting to RustChain nodes.

use reqwest::blocking::Client;
use std::time::Duration;

/// Build an HTTP client.
pub fn build_client(insecure: bool) -> Result<Client, Box<dyn std::error::Error>> {
    let mut builder = Client::builder()
        .timeout(Duration::from_secs(30))
        .connect_timeout(Duration::from_secs(10))
        .user_agent("rustchain-miner/0.1.0");

    if insecure {
        builder = builder.danger_accept_invalid_certs(true);
    }

    Ok(builder.build()?)
}
