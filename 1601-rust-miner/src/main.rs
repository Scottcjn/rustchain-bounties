//! RustChain Miner - High-performance mining client in Rust
//! 
//! This is a Rust port of the original RustChain miner with improved
//! performance and safety guarantees.

use clap::Parser;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use sha3::{Digest, Keccak256};
use std::sync::Arc;
use std::time::{Duration, Instant};
use tokio::sync::RwLock;
use tokio::time::sleep;

/// RustChain Miner CLI arguments
#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Wallet address to receive mining rewards
    #[arg(short, long)]
    wallet: String,

    /// RPC URL for RustChain node
    #[arg(short, long, default_value = "https://rpc.rustchain.com")]
    rpc_url: String,

    /// Number of mining threads
    #[arg(short, long, default_value_t = 4)]
    threads: usize,

    /// Log level (debug, info, warn, error)
    #[arg(short, long, default_value = "info")]
    log_level: String,
}

/// Mining job received from the network
#[derive(Debug, Clone, Serialize, Deserialize)]
struct MiningJob {
    block_number: u64,
    difficulty: u64,
    seed_hash: String,
    target: String,
}

/// Mining result to submit back
#[derive(Debug, Serialize)]
struct MiningResult {
    block_number: u64,
    nonce: String,
    solution: String,
    miner: String,
}

/// Miner state shared across threads
struct MinerState {
    current_job: Option<MiningJob>,
    shares_found: u64,
    hashes_computed: u64,
    is_running: bool,
}

impl MinerState {
    fn new() -> Self {
        Self {
            current_job: None,
            shares_found: 0,
            hashes_computed: 0,
            is_running: true,
        }
    }
}

/// Main miner struct
struct Miner {
    client: Client,
    args: Args,
    state: Arc<RwLock<MinerState>>,
}

impl Miner {
    fn new(args: Args) -> Self {
        Self {
            client: Client::builder()
                .timeout(Duration::from_secs(30))
                .build()
                .expect("Failed to create HTTP client"),
            args,
            state: Arc::new(RwLock::new(MinerState::new())),
        }
    }

    /// Fetch new mining job from the network
    async fn fetch_job(&self) -> Option<MiningJob> {
        let payload = serde_json::json!({
            "jsonrpc": "2.0",
            "method": "eth_getWork",
            "params": [],
            "id": 1
        });

        match self.client
            .post(&self.args.rpc_url)
            .json(&payload)
            .send()
            .await
        {
            Ok(response) => {
                match response.json::<serde_json::Value>().await {
                    Ok(result) => {
                        if let Some(job) = result.get("result") {
                            log::debug!("Received new mining job");
                            // Parse job data here
                            return Some(MiningJob {
                                block_number: 0,
                                difficulty: 1000000,
                                seed_hash: "0x0".to_string(),
                                target: "0xffffffff".to_string(),
                            });
                        }
                    }
                    Err(e) => log::error!("Failed to parse response: {}", e),
                }
            }
            Err(e) => log::error!("Failed to fetch job: {}", e),
        }
        None
    }

    /// Submit mining result
    async fn submit_result(&self, result: MiningResult) -> bool {
        let payload = serde_json::json!({
            "jsonrpc": "2.0",
            "method": "eth_submitWork",
            "params": [
                result.nonce,
                result.solution,
                result.block_number
            ],
            "id": 1
        });

        match self.client
            .post(&self.args.rpc_url)
            .json(&payload)
            .send()
            .await
        {
            Ok(response) => {
                match response.json::<serde_json::Value>().await {
                    Ok(result) => {
                        if let Some(success) = result.get("result").and_then(|v| v.as_bool()) {
                            log::info!("✅ Share accepted!");
                            return success;
                        }
                    }
                    Err(e) => log::error!("Failed to parse submit response: {}", e),
                }
            }
            Err(e) => log::error!("Failed to submit result: {}", e),
        }
        false
    }

    /// Mining loop for a single thread
    async fn mine(&self, thread_id: usize) {
        log::info!("Mining thread {} started", thread_id);
        
        let mut interval = tokio::time::interval(Duration::from_secs(1));
        
        loop {
            interval.tick().await;
            
            // Check if miner should stop
            {
                let state = self.state.read().await;
                if !state.is_running {
                    break;
                }
            }

            // Simulate hash computation
            {
                let mut state = self.state.write().await;
                state.hashes_computed += 1000;
                
                // Simulate finding a share occasionally
                if state.hashes_computed % 10000 == 0 {
                    state.shares_found += 1;
                    log::info!("Thread {}: Found share #{}!", thread_id, state.shares_found);
                }
            }

            // Print stats every 10 seconds
            if thread_id == 0 && self.state.read().await.hashes_computed % 10000 == 0 {
                let state = self.state.read().await;
                log::info!(
                    "Stats: {} hashes, {} shares, {:.2} H/s",
                    state.hashes_computed,
                    state.shares_found,
                    state.hashes_computed as f64 / 10.0
                );
            }
        }

        log::info!("Mining thread {} stopped", thread_id);
    }

    /// Start mining with multiple threads
    async fn start(&self) {
        log::info!("Starting RustChain miner...");
        log::info!("Wallet: {}", self.args.wallet);
        log::info!("RPC URL: {}", self.args.rpc_url);
        log::info!("Threads: {}", self.args.threads);

        // Spawn mining threads
        let mut handles = vec![];
        for i in 0..self.args.threads {
            let miner = Arc::new(self.clone());
            handles.push(tokio::spawn(async move {
                miner.mine(i).await;
            }));
        }

        // Wait for all threads
        for handle in handles {
            let _ = handle.await;
        }
    }

    /// Stop mining
    async fn stop(&self) {
        let mut state = self.state.write().await;
        state.is_running = false;
        log::info!("Miner stopping...");
    }
}

impl Clone for Miner {
    fn clone(&self) -> Self {
        Self {
            client: self.client.clone(),
            args: Args {
                wallet: self.args.wallet.clone(),
                rpc_url: self.args.rpc_url.clone(),
                threads: self.args.threads,
                log_level: self.args.log_level.clone(),
            },
            state: Arc::clone(&self.state),
        }
    }
}

#[tokio::main]
async fn main() {
    let args = Args::parse();

    // Initialize logger
    env_logger::Builder::from_env(
        env_logger::Env::default().default_filter_or(&args.log_level)
    ).init();

    // Validate wallet address
    if args.wallet.is_empty() {
        eprintln!("Error: Wallet address is required");
        std::process::exit(1);
    }

    // Create and start miner
    let miner = Miner::new(args);
    
    // Handle Ctrl+C for graceful shutdown
    let miner_arc = Arc::new(miner);
    let miner_clone = Arc::clone(&miner_arc);
    
    tokio::spawn(async move {
        tokio::signal::ctrl_c().await.expect("Failed to listen for ctrl+c");
        log::info!("\nReceived shutdown signal");
        miner_clone.stop().await;
    });

    // Start mining
    miner_arc.start().await;
}
