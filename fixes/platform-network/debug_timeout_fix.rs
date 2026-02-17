// Fix for: Missing timeout for list requests & Stdio deadlock
// Priority: High

use std::time::Duration;
use tokio::time::timeout;

const DEFAULT_TIMEOUT: Duration = Duration::from_secs(30);

pub async fn test_http_connection(url: &str) -> Result<bool, reqwest::Error> {
    match timeout(DEFAULT_TIMEOUT, reqwest::Client::new().get(url).send()).await {
        Ok(response) => Ok(response.unwrap().status().is_success()),
        Err(_) => Ok(false),
    }
}

pub async fn test_stdio_connection() -> Result<bool, std::io::Error> {
    use std::process::{Command, Stdio};
    let mut child = Command::new("echo").arg("test").stdout(Stdio::piped()).spawn()?;
    let _stderr = child.stderr.take();
    match timeout(Duration::from_secs(5), child.wait()).await {
        Ok(status) => Ok(status.success()),
        Err(_) => { let _ = child.kill(); Ok(false) }
    }
}
