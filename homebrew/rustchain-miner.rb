# typed: false
# frozen_string_literal: true

# Homebrew formula for RustChain Proof-of-Antiquity Miner (Native Rust)
class RustchainMiner < Formula
  desc "RustChain Proof-of-Antiquity Miner - Native Rust implementation"
  homepage "https://github.com/Scottcjn/rustchain-bounties/tree/main/rustchain-miner"
  url "https://github.com/Scottcjn/rustchain-bounties.git", branch: "main"
  version "0.1.0"
  license "MIT"

  depends_on "rust" => :build

  def install
    cd "rustchain-miner" do
      system "cargo", "install", *std_cargo_args
    end
  end

  def caveats
    <<~EOS
      RustChain Miner installed successfully.

      QUICK START:
        1. Get a wallet address (or use auto-generated)
        2. Run: rustchain-miner --wallet YOUR_WALLET_ID

      MINING TIPS:
        - Vintage hardware earns higher multipliers
        - PowerPC G4/G5: 2.0-2.5x
        - Apple Silicon (M1/M2/M3): 1.2x
        - Modern x86_64: 1.0x

      SECURITY NOTES:
        - Never share your wallet ID
        - Miner runs as your user (no root required)
        - Source: https://github.com/Scottcjn/rustchain-bounties
    EOS
  end

  test do
    output = shell_output("#{bin}/rustchain-miner --help 2>&1", 1)
    assert_match "RustChain", output
    assert_match "wallet", output
  end
end
