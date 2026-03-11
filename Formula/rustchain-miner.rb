# SPDX-License-Identifier: MIT
# frozen_string_literal: true

# Homebrew formula for the RustChain Proof-of-Attestation miner.
#
# Source repository: https://github.com/Scottcjn/Rustchain
# Pinned to tag: v1.0.0-miner (commit dbd287470a68efb2e7cfa0c1338f53567eff557c)
#
# Install via tap:
#   brew tap Scottcjn/rustchain https://github.com/Scottcjn/rustchain-bounties.git
#   brew install rustchain-miner
#
# Usage:
#   rustchain-miner --wallet YOUR_WALLET_ID
#   rustchain-miner --wallet YOUR_WALLET_ID --node https://50.28.86.131

class RustchainMiner < Formula
  desc "RustChain Proof-of-Attestation miner for macOS and Linux"
  homepage "https://github.com/Scottcjn/Rustchain"
  url "https://github.com/Scottcjn/Rustchain/archive/refs/tags/v1.0.0-miner.tar.gz"
  sha256 "a2e16d61e62941592f7da4a688a78a2197429e8e685e04f3748b5bc9c5a38dcf"
  license "MIT"
  version "1.0.0"

  # Pinned commit: dbd287470a68efb2e7cfa0c1338f53567eff557c
  # Upstream checksums (from miners/checksums.sha256):
  #   linux/rustchain_linux_miner.py    2d166739ae9a...cc890c
  #   linux/fingerprint_checks.py       91b09779649b...191ddf
  #   macos/rustchain_mac_miner_v2.4.py 912a3073d860...eb0c68

  depends_on "python@3"

  resource "requests" do
    url "https://files.pythonhosted.org/packages/9d/be/10918a2eac4ae9f02f6cfe6414b7a155ccd8f7f9d4380d62fd5b955065c3/requests-2.31.0.tar.gz"
    sha256 "942c5a758f98d790eaed1a29cb6eefc7ffb0d1cf7af05c3d2791656dbd6ad1e1"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/36/dd/a6b232f449e1bc71802a5b7950dc3675d32c6dbc2a1bd6d71f065551adb6/urllib3-2.1.0.tar.gz"
    sha256 "df7aa8afb0148fa78488e7899b2c59b5f4ffcfa82e6c54ccb9dd37c1d7b52d54"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/71/da/e94e26401b62acd6d91df2b52954aceb7f561743aa5ccc32152886c76c96/certifi-2024.2.2.tar.gz"
    sha256 "0569859f95fc761b18b45ef421b1290a0f65f147e92a1e5eb3e635f9a5e4e66f"
  end

  resource "charset-normalizer" do
    url "https://files.pythonhosted.org/packages/63/09/c1bc53dab74b1816a00d8d030de5bf98f724c52c1635e07681d312f20be8/charset-normalizer-3.3.2.tar.gz"
    sha256 "f30c3cb33b24454a82faecaf01b19c18562b1e89558fb6c56de4d9118a032fd5"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/bf/3f/ea4b9117521a1e9c50344b909be7886dd00a519552724809bb1f486986c2/idna-3.6.tar.gz"
    sha256 "9ecdbbd083b06798ae1e86adcbfe8ab1479cf864e4ee30fe4e46a003d12491ca"
  end

  def install
    # Determine platform-specific miner files
    if OS.mac?
      miner_script = "miners/macos/rustchain_mac_miner_v2.4.py"
      miner_name   = "rustchain_mac_miner_v2.4.py"
    else
      miner_script = "miners/linux/rustchain_linux_miner.py"
      miner_name   = "rustchain_linux_miner.py"
    end

    # Verify upstream file checksums before installing
    require "digest"
    checksums = {
      "miners/linux/rustchain_linux_miner.py" =>
        "2d166739ae9a4b7764108c2efa4de38d45797858219dbeed6b149f4ba4cc890c",
      "miners/linux/fingerprint_checks.py" =>
        "91b09779649bd870ea4984c707650d1e111a92a5318634c3fb05c8ac04191ddf",
      "miners/macos/rustchain_mac_miner_v2.4.py" =>
        "912a3073d860d147bfef105f4321a2c0b5aabe30c715a84d75be9ee415eb0c68",
    }

    checksums.each do |file, expected_sha|
      path = buildpath/file
      next unless path.exist?

      actual_sha = Digest::SHA256.hexdigest(path.read)
      if actual_sha != expected_sha
        odie "Checksum mismatch for #{file}: expected #{expected_sha}, got #{actual_sha}"
      end
    end

    # Install Python dependencies into a virtualenv
    venv = virtualenv_create(libexec, "python3")
    venv.pip_install resources

    # Install miner script into libexec
    libexec.install buildpath/miner_script => miner_name

    # Install fingerprint checks module alongside miner
    fp = buildpath/"miners/linux/fingerprint_checks.py"
    libexec.install fp if fp.exist?

    # Create wrapper script in bin/
    (bin/"rustchain-miner").write <<~BASH
      #!/bin/bash
      # SPDX-License-Identifier: MIT
      # Wrapper script for the RustChain Proof-of-Attestation miner.
      # Installed by: brew install rustchain-miner
      set -euo pipefail

      export PYTHONPATH="#{libexec}:${PYTHONPATH:-}"
      exec "#{libexec}/bin/python3" "#{libexec}/#{miner_name}" "$@"
    BASH
  end

  def caveats
    <<~EOS
      RustChain miner has been installed.

      Quick start:
        rustchain-miner --wallet YOUR_WALLET_ID

      Custom node:
        rustchain-miner --wallet YOUR_WALLET_ID --node https://50.28.86.131

      Check your balance:
        curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"

      To run as a background service:
        brew services start rustchain-miner

      NOTE: The miner requires real hardware (non-VM) for full reward
      eligibility. VM miners may attest but rewards can be penalized.

      Set your wallet ID for the background service via:
        echo 'RUSTCHAIN_WALLET=your-wallet-id' > #{var}/rustchain-miner.conf
    EOS
  end

  service do
    run [opt_bin/"rustchain-miner", "--wallet", "default"]
    keep_alive true
    working_dir var
    log_path var/"log/rustchain-miner.log"
    error_log_path var/"log/rustchain-miner.log"
    environment_variables RUSTCHAIN_NODE: "https://50.28.86.131"
  end

  test do
    # Verify the wrapper script exists and is executable
    assert_predicate bin/"rustchain-miner", :exist?
    assert_predicate bin/"rustchain-miner", :executable?

    # Verify the miner script was installed
    if OS.mac?
      assert_predicate libexec/"rustchain_mac_miner_v2.4.py", :exist?
    else
      assert_predicate libexec/"rustchain_linux_miner.py", :exist?
    end

    # Verify Python can import the miner without network errors
    # (should fail gracefully with missing --wallet, not crash)
    output = shell_output("#{bin}/rustchain-miner --help 2>&1", 2)
    assert_match(/wallet/i, output)
  end
end
