#[tokio::main]
async fn main() {
    // Test the rustchain_health function
    match rustchain_health().await {
        Ok(response) => println!("Health Response: {}", response),
        Err(e) => eprintln!("Health Check Failed: {}", e),
    }

    // Test the rustchain_balance function
    let wallet_address = "test_wallet";
    match rustchain_balance(wallet_address).await {
        Ok(balance) => println!("Balance for {}: {}", wallet_address, balance),
        Err(e) => eprintln!("Balance Check Failed: {}", e),
    }
}