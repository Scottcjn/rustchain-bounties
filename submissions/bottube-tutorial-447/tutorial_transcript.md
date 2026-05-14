# RustChain Miner Tutorial — Full Transcript

> **Video Title:** How to Set Up a RustChain Miner in 5 Minutes
> **Bounty:** #447 — Create a BoTTube Tutorial Video
> **Submitter:** zp6 | **Wallet:** zp6
> **Date:** 2026-05-14

---

## Complete Narration Transcript

This document contains the full spoken narration for the tutorial video, designed to be read aloud as a voiceover during screen recordings.

---

### [0:00 — 0:45] Intro

Hey everyone! Welcome back to the channel.

Today I'm going to show you how to set up your very own RustChain miner — and I'm talking fully operational, hashing away — in just five minutes. Whether you're a total beginner or you've been mining other chains for years, this guide has you covered.

We'll go from zero to mining in no time. Let's dive in!

---

### [0:45 — 1:30] Prerequisites

Before we start, let me show you what you'll need.

First, you need a computer running Linux, macOS, or Windows. RustChain supports all three platforms, so you're good regardless of what you're running.

Second, you'll need a RustChain wallet address to receive your mining rewards. If you don't have one yet, I'll show you how to create it right now.

*(screen recording: navigating to wallet creation)*

Head over to the RustChain website, click "Create Wallet", and copy your new address. Keep this safe — this is where your mining rewards will go.

I'll use my address as an example in this video, but make sure you use your own address when you follow along.

And one important reminder: never share your private key or seed phrase with anyone. Your wallet address is fine to share, but keep the private stuff private.

---

### [1:30 — 3:00] Installing the Miner

Alright, let's get the miner installed.

Open your terminal — that's Terminal on Mac and Linux, or PowerShell on Windows.

*(screen recording: terminal opens)*

First, let's clone the official RustChain miner repository from GitHub:

```
git clone https://github.com/rustchain-network/rustchain-miner.git
```

Now navigate into the directory:

```
cd rustchain-miner
```

And build the miner using Cargo, which is Rust's package manager:

```
cargo build --release
```

*(screen recording: compilation progress)*

This should take about 30 seconds to a minute depending on your machine. The compiler is downloading dependencies and building an optimized binary for your system.

If you don't have Rust installed yet, you can get it from rustup.rs — I'll link it in the description below. It's a one-command install.

*(screen recording: build completes)*

And that's it — the miner is compiled and ready to go. You'll find the binary at `target/release/rustchain-miner`. Let's configure it.

---

### [3:00 — 4:00] Configuration

Now we need to tell the miner where to send your mining rewards.

Create a configuration file in the miner directory. You can call it `miner-config.toml`.

*(screen recording: creating config file)*

Here's what goes in it:

```toml
[runtime]
wallet_address = "YOUR_WALLET_ADDRESS_HERE"
threads = 0  # 0 = auto-detect, uses all available cores

[network]
pool_url = "stratum+tcp://pool.rustchain.xyz:3333"
```

Replace `YOUR_WALLET_ADDRESS_HERE` with the wallet address we created earlier. Just paste it right in there.

The threads setting — when set to zero — means the miner will automatically detect and use all your CPU cores. If you want to leave some cores free for other tasks, you can set this to a specific number instead.

The pool URL connects you to the official RustChain mining pool, where miners work together and share rewards proportionally.

*(screen recording: showing completed config)*

Alright, config is done. Time to start mining!

---

### [4:00 — 5:00] Start Mining!

Here's the moment of truth.

*(screen recording: running the command)*

Run the miner with your config file:

```bash
./target/release/rustchain-miner --config miner-config.toml
```

On Windows, it would be:

```powershell
.\target\release\rustchain-miner.exe --config miner-config.toml
```

*(screen recording: miner output showing connection and hashing)*

Look at that — we're mining! You can see the miner has connected to the pool, and it's already hashing. Within seconds you should see your first accepted shares, which means you're actively contributing to the RustChain network and earning rewards.

The top line shows your current hashrate, and below you can see shares being submitted and accepted. Everything is working perfectly.

*(screen recording: zoom in on accepted share notification)*

Congratulations — you now have a working RustChain miner!

---

### [5:00 — 6:00] Monitoring & Tips

To monitor your mining progress over time, you can visit the RustChain pool dashboard.

*(screen recording: opening pool dashboard in browser)*

Just enter your wallet address, and you'll see your hashrate, total shares, and estimated earnings in real-time. It's a great way to keep track of how you're doing.

A few tips to maximize your mining experience:

**First — keep your system cool.** Mining uses a lot of CPU, so make sure you have good ventilation. Consider using a laptop cooler or running in an air-conditioned room.

**Second — set up auto-start.** You can configure the miner to run as a background service so it starts automatically when your system boots. That way you never miss mining time.

**Third — join the RustChain Discord.** That's where you'll find the latest updates on pool changes, network upgrades, and you can get help from the community if you run into any issues.

Links for everything are in the description.

---

### [6:00 — 6:30] Outro

And there you have it — a fully working RustChain miner set up in under five minutes.

If this video helped you, smash that like button, subscribe to the channel for more crypto tutorials, and drop a comment if you have any questions. I read every single one.

Check out the description for all the links and resources mentioned in this video.

Happy mining, and I'll see you in the next one. Peace!

---

## Quick Reference — Commands Cheat Sheet

```bash
# 1. Clone the repository
git clone https://github.com/rustchain-network/rustchain-miner.git
cd rustchain-miner

# 2. Build the miner
cargo build --release

# 3. Create config file
cat > miner-config.toml << EOF
[runtime]
wallet_address = "YOUR_WALLET_ADDRESS"
threads = 0

[network]
pool_url = "stratum+tcp://pool.rustchain.xyz:3333"
EOF

# 4. Start mining
./target/release/rustchain-miner --config miner-config.toml
```

---

## Troubleshooting FAQ

| Problem | Solution |
|---------|----------|
| `cargo: command not found` | Install Rust from https://rustup.rs |
| Build fails with OpenSSL error | Install `libssl-dev` (Ubuntu) or `openssl-devel` (CentOS) |
| Connection refused to pool | Check internet connection; pool may be under maintenance |
| Low hashrate | Close other CPU-intensive apps; check thermal throttling |
| Shares not being accepted | Verify wallet address in config; try a different pool server |

---

*This transcript is part of the RustChain BoTTube Tutorial Video submission for bounty #447.*
