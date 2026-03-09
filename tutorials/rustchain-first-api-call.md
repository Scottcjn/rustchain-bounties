# RustChain First API Call Walkthrough

This tutorial will guide you through making your first API call to the RustChain network and demonstrate a signed transfer example.

## Prerequisites

- Rust installed on your system
- Basic knowledge of Rust programming
- A RustChain node running or access to a testnet

## Setting Up

First, let's add the RustChain client library to your `Cargo.toml`:

```toml
[dependencies]
rustchain-client = "0.1.0"
```

## Making Your First API Call

Create a new Rust project:

```bash
cargo new rustchain-tutorial
cd rustchain-tutorial
```

Now, let's make a simple API call to get the network status:

```rust
use rustchain_client::{Client, Result};

#[tokio::main]
async fn main() -> Result<()> {
    // Create a client instance
    let client = Client::new("https://testnet.rustchain.io");
    
    // Get network status
    let status = client.get_network_status().await?;
    
    println!("Network Status: {:?}", status);
    
    Ok(())
}
```

## Signed Transfer Example

Now, let's create a signed transfer transaction:

```rust
use rustchain_client::{
    Client,
    Transaction,
    SignedTransaction,
    KeyPair,
    Result
};

#[tokio::main]
async fn main() -> Result<()> {
    // Create a client instance
    let client = Client::new("https://testnet.rustchain.io");
    
    // Generate a key pair for signing
    let keypair = KeyPair::generate();
    let public_key = keypair.public_key();
    
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
    } else {
        println!("Transaction not confirmed within timeout");
    }
    
    Ok(())
}
```

## Complete Example

Here's a complete example that combines both API calls and transfers:

```rust
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
    
    // Step 1: Get network status
    println!("Getting network status...");
    let status = client.get_network_status().await?;
    println!("Network Status: {:?}", status);
    
    // Step 2: Generate keypair
    println!("\nGenerating keypair...");
    let keypair = KeyPair::generate();
    let public_key = keypair.public_key();
    println!("Public Key: {}", public_key);
    
    // Step 3: Create and send transaction
    println!("\nCreating transaction...");
    let transaction = Transaction::new(
        "transfer".to_string(),
        serde_json::json!({
            "from": public_key.to_string(),
            "to": "recipient_address_here",
            "amount": 100,
            "currency": "RTC"
        })
    );
    
    let signed_tx = SignedTransaction::sign(&transaction, &keypair)?;
    println!("Transaction signed successfully");
    
    // Step 4: Send transaction
    println!("\nSending transaction...");
    let tx_hash = client.send_transaction(&signed_tx).await?;
    println!("Transaction sent with hash: {:?}", tx_hash);
    
    // Step 5: Wait for confirmation
    println!("\nWaiting for confirmation...");
    let confirmed = client.wait_for_confirmation(&tx_hash, 60).await?;
    
    if confirmed {
        println!("Transaction confirmed!");
        
        // Step 6: Get transaction details
        let tx_details = client.get_transaction(&tx_hash).await?;
        println!("Transaction Details: {:?}", tx_details);
    } else {
        println!("Transaction not confirmed within timeout");
    }
    
    Ok(())
}
```

## Next Steps

1. Explore the RustChain API documentation for more endpoints
2. Try different transaction types
3. Implement error handling for production use
4. Learn about RustChain's consensus mechanism

## Troubleshooting

- If you encounter connection issues, verify your node URL
- Ensure you have enough balance for transactions
- Check that your private keys are securely stored

For more information, visit the [RustChain Documentation](https://docs.rustchain.io).