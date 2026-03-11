class Rustchain < Formula
  desc "RustChain blockchain tools"
  homepage "https://github.com/Scottcjn/Rustchain"
  version "1.0.0"
  license "MIT"

  on_macos do
    on_intel do
      url "https://github.com/Scottcjn/Rustchain/releases/download/v1.0.0/rustchain-darwin-amd64.tar.gz"
      sha256 "PLACEHOLDER"
    end
    on_arm do
      url "https://github.com/Scottcjn/Rustchain/releases/download/v1.0.0/rustchain-darwin-arm64.tar.gz"
      sha256 "PLACEHOLDER"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/Scottcjn/Rustchain/releases/download/v1.0.0/rustchain-linux-amd64.tar.gz"
      sha256 "PLACEHOLDER"
    end
    on_arm do
      url "https://github.com/Scottcjn/Rustchain/releases/download/v1.0.0/rustchain-linux-arm64.tar.gz"
      sha256 "PLACEHOLDER"
    end
  end

  def install
    bin.install "rustchain"
    bin.install "rtc-miner" if File.exist?("rtc-miner")
  end

  test do
    assert_match "RustChain", shell_output("#{bin}/rustchain --version 2>&1 || true")
  end
end

# Bounty wallet: RTC27a4b8256b4d3c63737b27e96b181223cc8774ae
