# Rust Agent Bounty Hunter

A high-performance Rust-based AI agent for automated bounty hunting on RustChain and other GitHub repositories.

## Features

- **Scanner**: Fetch and rank open bounty leads from GitHub issues
- **Analyzer**: Analyze bounty requirements and complexity
- **Generator**: Generate automated claim/submission templates
- **Quality**: Validate submissions meet quality standards
- **Submitter**: Prepare PR-ready submissions

## Quick Start

```bash
cargo build --release
./target/release/rust-agent-bounty-hunter scan --top 10
```

## Modules

- `src/scanner.rs` - Issue discovery and ranking
- `src/analyzer.rs` - Bounty analysis
- `src/generator.rs` - Template generation
- `src/quality.rs` - Quality validation
- `src/submitter.rs` - Submission preparation
- `src/main.rs` - CLI interface

## Example Usage

```bash
# Scan for bounties
cargo run -- scan --top 20 --min-reward 10

# Analyze a specific issue
cargo run -- analyze --owner rustchain --repo bounties --issue 34

# Generate submission
cargo run -- submit --pr 115 --wallet my_wallet
```

## Integration

Part of the rustchain-bounties ecosystem (Issue #34).
See: `docs/AGENT_BOUNTY_HUNTER_FRAMEWORK.md`
