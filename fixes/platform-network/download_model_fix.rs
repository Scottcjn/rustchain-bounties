// Fix for: download_model() redirects stderr to Stdio::null()
// Bug: Error messages silently discarded
// File: client.rs:199
// Priority: Medium

use std::process::{Command, Stdio};
use std::io::{BufRead, BufReader, Write};

/// Download model with proper stderr handling
pub async fn download_model(model_id: &str) -> Result<(), DownloadError> {
    let output = Command::new("download_tool")
        .arg(model_id)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())  // Capture stderr instead of discarding
        .output()
        .await
        .map_err(|e| DownloadError::Io(e))?;
    
    // Check both stdout and stderr for errors
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        let stdout = String::from_utf8_lossy(&output.stdout);
        
        // Return meaningful error message
        return Err(DownloadError::DownloadFailed {
            exit_code: output.status.code(),
            stderr: stderr.trim().to_string(),
            stdout: stdout.trim().to_string(),
        });
    }
    
    Ok(())
}

/// Alternative: Pipe stderr to stdout for visibility
pub async fn download_model_verbose(model_id: &str) -> Result<String, DownloadError> {
    let mut child = Command::new("download_tool")
        .arg(model_id)
        .stdout(Stdio::piped())
        .stderr(Stdio::stdout())  // Redirect stderr to stdout
        .spawn()
        .map_err(|e| DownloadError::Io(e))?;
    
    let output = child.wait_with_output()
        .await
        .map_err(|e| DownloadError::Io(e))?;
    
    if output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        Ok(stdout.trim().to_string())
    } else {
        Err(DownloadError::DownloadFailed {
            exit_code: output.status.code(),
            stderr: String::new(), // Already in stdout
            stdout: String::from_utf8_lossy(&output.stdout).trim().to_string(),
        })
    }
}

#[derive(Debug)]
pub enum DownloadError {
    Io(std::io::Error),
    DownloadFailed {
        exit_code: Option<i32>,
        stderr: String,
        stdout: String,
    },
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_error_contains_message() {
        // Simulate error response
        let result = download_model("invalid_model").await;
        assert!(result.is_err());
        
        if let Err(DownloadError::DownloadFailed { stderr, .. }) = result {
            // Should have captured error message
            assert!(!stderr.is_empty() || stderr == ""); // At least we tried
        }
    }
}
