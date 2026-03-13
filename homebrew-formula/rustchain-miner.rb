class RustchainMiner < Formula
  desc "RustChain cryptocurrency miner"
  homepage "https://github.com/Scottcjn/rustchain-bounties"
  url "https://github.com/Scottcjn/rustchain-bounties/archive/v1.0.0.tar.gz"
  sha256 "TODO"
  license "MIT"

  depends_on "rust" => :build

  def install
    system "cargo", "build", "--release"
    bin.install "target/release/rustchain-miner"
  end

  test do
    system "#{bin}/rustchain-miner", "--version"
  end
end
