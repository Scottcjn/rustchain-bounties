// RustChain Signed Transfer Example
// This example demonstrates how to create and sign a transaction in RustChain

use rustchain_client::{
    Client,
    Transaction,
    SignedTransaction,
    KeyPair,
    Result
};
use std::time::Duration;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize client
    let client = Client::new("https://testnet.rustchain.io");
    
    // Generate a new keypair for this example
    let keypair = KeyPair::generate();
    let public_key = keypair.public_key();
    
    println!("Public Key: {}", public_key);
    
    // Create a transaction
    let transaction = Transaction::new(
        "transfer".to_string(),
        serde_json::json!({
            "from": public_key.to_string(),
            "to": "recipient_address_here",
            "amount": 100,
            "currency": "RTC"
        })
    );
    
    // Sign the transaction
    let signed_tx = SignedTransaction::sign(&transaction, &keypair)?;
    
    // Send the transaction
    let tx_hash = client.send_transaction(&signed_tx).await?;
    
    println!("Transaction sent with hash: {:?}", tx_hash);
    
    // Wait for confirmation
    let confirmed = client.wait_for_confirmation(&tx_hash, 60).await?;
    
    if confirmed {
        println!("Transaction confirmed!");
        
        // Get transaction details
        let tx_details = client.get_transaction(&tx_hash).await?;
        println!("Transaction Details: {:?}", tx_details);
    } else {
        println!("Transaction not confirmed within timeout");
    }
    
    Ok(())
}

// Helper function to display transaction status
fn display_transaction_status(tx_hash: &str, confirmed: bool) {
    if confirmed {
        println!("✅ Transaction {} confirmed", tx_hash);
    } else {
        println!("❌ Transaction {} not confirmed", tx_hash);
    }
}