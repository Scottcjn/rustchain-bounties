pub async fn rustchain_miners() -> Result<Vec<String>> {
    // Send a GET request to retrieve the list of active miners
    let url = "https://50.28.86.131/miners";  // Default URL, configurable if necessary
    let response = reqwest::get(url).await
        .context("Failed to call rustchain miners endpoint")?;

    if response.status().is_success() {
        let miners_info: Vec<String> = response.json().await.context("Failed to read json from response")?;
        Ok(miners_info)  // Return the list of active miners
    } else {
        Err(anyhow::anyhow!("Miners check failed: {}", response.status()))
    }
}