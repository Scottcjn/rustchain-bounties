use clap::Parser;

/// Native Rust miner for RustChain — full RIP-PoA hardware fingerprinting.
#[derive(Parser, Debug)]
#[command(
    name = "rustchain-miner",
    version,
    about = "Native Rust miner for the RustChain Proof-of-Antiquity blockchain"
)]
pub struct Cli {
    /// Wallet / miner ID to mine with.
    #[arg(long)]
    pub wallet: Option<String>,

    /// RustChain node URL.
    #[arg(long, default_value = "https://50.28.86.131")]
    pub node: String,

    /// Disable TLS certificate verification for test nodes with self-signed certificates.
    #[arg(long)]
    pub insecure: bool,

    /// Build and display the attestation payload without submitting.
    #[arg(long)]
    pub dry_run: bool,

    /// Print the exact JSON payload that would be sent.
    #[arg(long)]
    pub show_payload: bool,

    /// Run fingerprint checks only (no attestation).
    #[arg(long)]
    pub test_only: bool,
}

#[cfg(test)]
mod tests {
    use super::Cli;
    use clap::Parser;

    #[test]
    fn tls_verification_is_enabled_by_default() {
        let cli = Cli::try_parse_from(["rustchain-miner"]).unwrap();

        assert!(!cli.insecure);
    }

    #[test]
    fn insecure_flag_is_explicit_opt_in() {
        let cli = Cli::try_parse_from(["rustchain-miner", "--insecure"]).unwrap();

        assert!(cli.insecure);
    }
}
