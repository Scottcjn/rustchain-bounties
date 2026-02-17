use reqwest::Client;
use serde_json::Value;
use anyhow::Result;

/// Scanner module for discovering bounty issues
pub async fn scan_bounties(top: u32, min_reward: Option<f64>) -> Result<()> {
    let client = Client::new();

    // Fetch issues from rustchain-bounties repository
    let url = "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?state=open&labels=bounty";
    let response = client.get(url)
        .header("Accept", "application/vnd.github.v3+json")
        .send()
        .await?;

    let issues: Value = response.json().await?;

    println!("Scanning top {} bounties...", top);
    if let Some(issues_array) = issues.as_array() {
        for (i, issue) in issues_array.iter().take(top as usize).enumerate() {
            let number = issue["number"].as_u64().unwrap_or(0);
            let title = issue["title"].as_str().unwrap_or("Unknown");
            let body = issue["body"].as_str().unwrap_or("");

            println!("{}. #{} - {}", i + 1, number, title);

            // Extract reward from issue body
            if let Some(reward) = extract_reward(body) {
                if let Some(min) = min_reward {
                    if reward < min {
                        continue;
                    }
                }
                println!("   Reward: {} RTC", reward);
            }
        }
    }

    Ok(())
}

fn extract_reward(body: &str) -> Option<f64> {
    // Simple heuristic: look for RTC or reward patterns
    if let Some(caps) = regex::Regex::new(r"(\d+)\s*RTC")
        .ok()?
        .captures(body)
    {
        caps.get(1)?.as_str().parse().ok()
    } else {
        None
    }
}
