# Homebrew Formula for RustChain Miner

**Bounty**: #1612
**Value**: 5 RTC (~$0.5)
**Status**: In Progress

---

## 📁 Formula File

`rustchain-miner.rb`:

```ruby
class RustchainMiner < Formula
  desc "RustChain cryptocurrency miner"
  homepage "https://github.com/Scottcjn/RustChain"
  url "https://github.com/Scottcjn/RustChain/archive/v1.0.0.tar.gz"
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
```

---

## 🚀 Installation

```bash
# Add the tap
brew tap Scottcjn/rustchain-bounties

# Install the miner
brew install rustchain-miner

# Run it
rustchain-miner --wallet <your-wallet>
```

---

## ✅ Progress

- [x] Create formula file
- [ ] Add sha256 checksum
- [ ] Write INSTALL.md
- [ ] Test installation
- [ ] Submit PR

---

**ETA**: 30 minutes
