class RustchainMiner < Formula
  desc "RustChain cryptocurrency miner"
  homepage "https://rustchain.org"
  url "https://github.com/Scottcjn/rustchain-bounties/archive/refs/tags/v1.0.0.tar.gz"
  sha256 :noprefix # Replace with actual SHA256 checksum
  license "MIT"
  version "1.0.0"

  bottle do
    root_url "https://github.com/Scottcjn/rustchain-bounties/releases/download/v1.0.0/"
    sha256 cellar: :any_skip_relocation, all: :noprefix # Replace with actual checksum
  end

  depends_on "python@3.11"

  def install
    # Install Python dependencies
    pip_install_from_requirements(buildpath/"miner/requirements.txt")
    
    # Install miner script
    bin.install "miner/rust_miner.py" => "rustchain-miner"
    bin.install "miner/rust_miner.sh" => "rustchain-miner-wrapper" if File.exist?("miner/rust_miner.sh")
    
    # Install configuration example
    etc.install "miner/config.example.json" => "rustchain-miner.conf.example"
  end

  def post_install
    # Create data directory
    (var/"lib/rustchain-miner").mkpath
  end

  service do
    run [opt_bin/"rustchain-miner", "--daemon"]
    environment_variables PATH: std_service_path_env
    keep_alive true
    working_dir var/"lib/rustchain-miner"
    log_path var/"log/rustchain-miner.log"
    error_log_path var/"log/rustchain-miner.err.log"
  end

  test do
    # Basic version check
    assert_match version.to_s, shell_output("#{bin}/rustchain-miner --version", 0)
    
    # Help command check
    assert_match "Usage:", shell_output("#{bin}/rustchain-miner --help", 0)
  end

  def caveats
    <<~EOS
      RustChain miner has been installed.
      
      To configure the miner, copy the example config:
        cp #{etc}/rustchain-miner.conf.example ~/.rustchain-miner.conf
      
      To start the miner service:
        brew services start rustchain-miner
      
      To run manually:
        rustchain-miner --wallet YOUR_WALLET --node http://localhost:8545
      
      For more information, visit: https://rustchain.org
    EOS
  end
end