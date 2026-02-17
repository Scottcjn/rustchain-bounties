use clap::{Parser, Subcommand};
use anyhow Result;

mod scanner;
mod analyzer;
mod generator;
mod quality;
mod submitter;

#[derive(Parser)]
#[command(name = "rust-agent-bounty-hunter")]
#[command(author = "星火")]
#[command(version = "1.0.0")]
#[command(about = "Rust-based AI Agent Bounty Hunter for RustChain", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Scan for open bounties
    Scan {
        #[arg(short, long, default_value = "10")]
        top: u32,
        #[arg(short, long)]
        min_reward: Option<f64>,
    },
    /// Analyze a bounty issue
    Analyze {
        #[arg(long)]
        owner: String,
        #[arg(long)]
        repo: String,
        #[arg(long)]
        issue: u32,
    },
    /// Generate submission template
    Submit {
        #[arg(long)]
        pr: u32,
        #[arg(long)]
        wallet: String,
    },
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Scan { top, min_reward } => {
            scanner::scan_bounties(top, min_reward).await?;
        }
        Commands::Analyze { owner, repo, issue } => {
            analyzer::analyze_bounty(&owner, &repo, issue).await?;
        }
        Commands::Submit { pr, wallet } => {
            submitter::generate_submission(pr, &wallet).await?;
        }
    }

    Ok(())
}
