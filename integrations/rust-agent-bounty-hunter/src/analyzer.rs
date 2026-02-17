use reqwest::Client;
use serde_json::Value;
use anyhow::Result;

/// Analyzer module for evaluating bounty complexity
pub async fn analyze_bounty(owner: &str, repo: &str, issue_number: u32) -> Result<()> {
    let client = Client::new();
    let url = format!(
        "https://api.github.com/repos/{}/{}/issues/{}",
        owner, repo, issue_number
    );

    let response = client.get(&url)
        .header("Accept", "application/vnd.github.v3+json")
        .send()
        .await?;

    let issue: Value = response.json().await?;

    let title = issue["title"].as_str().unwrap_or("Unknown");
    let body = issue["body"].as_str().unwrap_or("");
    let labels: Vec<String> = issue["labels"]
        .as_array()
        .unwrap_or(&Vec::new())
        .iter()
        .filter_map(|l| l["name"].as_str().map(|s| s.to_string()))
        .collect();

    println!("Analyzing bounty #{}: {}", issue_number, title);
    println!("Labels: {:?}", labels);

    // Calculate difficulty score
    let difficulty = calculate_difficulty(&labels, body);
    println!("Estimated difficulty: {}", difficulty);

    Ok(())
}

fn calculate_difficulty(labels: &[Vec<String>>, body: &str) -> String {
    let label_str = labels.join(" ");
    match label_str.to_lowercase().as_str() {
        _ if label_str.contains("critical") => "Critical - Immediate action needed",
        _ if label_str.contains("high") => "High - Significant work required",
        _ if label_str.contains("medium") => "Medium - Moderate effort",
        _ if label_str.contains("low") => "Low - Quick fix",
        _ => "Unknown - Manual review needed",
    }.to_string()
}
