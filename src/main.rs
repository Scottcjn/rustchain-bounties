use std::time::{Duration, Instant};
use reqwest;
use serde_json::Value;

const BACKOFF_BASE: u64 = 5; // Base time for exponential backoff in seconds
const BACKOFF_MAX: u64 = 300; // Maximum backoff time in seconds

struct Header {
    data: Value,
}

impl Header {
    fn new(data: Value) -> Self {
        Header { data }
    }

    fn rebuild(&mut self) {
        // Logic to rebuild the header
    }
}

fn submit_header(header: &Header, url: &str) -> Result<(), String> {
    let client = reqwest::blocking::Client::new();
    let response = client.post(url)
        .json(&header.data)
       .send()
        .map_err(|e| format!("Request failed: {}", e))?;

    if response.status().is_success() {
        Ok(())
    } else {
        let error_body = response.text().unwrap_or_default();
        Err(error_body)
    }
}

fn main() {
    let mut header = Header::new(serde_json::json!({
        "key": "value"
    }));
    let url = "http://example.com/submit-header";

    let mut backoff_duration = Duration::from_secs(BACKOFF_BASE);
    let mut last_rejection_time = None;

    loop {
        match submit_header(&header, url) {
            Ok(_) => {
                println!("Header submitted successfully.");
                break;
            }
            Err(error_body) => {
                println!("Header submission failed: {}", error_body);

                if let Some(last_time) = last_rejection_time {
                    if Instant::now() - last_time < backoff_duration {
                        println!("Skipping resubmission due to recent rejection.");
                        continue;
                    }
                }

                if error_body.contains("non-retryable") {
                    println!("Non-retryable condition detected. Rebuilding header.");
                    header.rebuild();
                    backoff_duration = Duration::from_secs(BACKOFF_BASE); // Reset backoff
                } else {
                    println!("Retryable condition detected. Applying backoff.");
                    backoff_duration = Duration::from_secs(std::cmp::min(
                        backoff_duration.as_secs() * 2,
                        BACKOFF_MAX,
                    ));
                }

                last_rejection_time = Some(Instant::now());
            }
        }
    }
}