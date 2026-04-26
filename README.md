// File: README.md
# RustChain Bounties

Welcome to the RustChain Bounties repository — a decentralized incentive layer for open-source contributions.

This repo manages bounties, rewards, and contributor recognition for the RustChain ecosystem.

## 📢 Active Bounties

See [bounties/ACTIVE.md](bounties/ACTIVE.md) for a list of currently available bounties.

## 🏆 Reward System

Contributors earn RTC tokens and XP for meaningful contributions:
- Pull request merges
- Bug reports
- Documentation improvements
- Community support

Rewards are distributed automatically via GitHub Actions and recorded in the XP tracker.

## 🧠 RustChain MCP Server

Connect any AI agent to RustChain using the Model Context Protocol (MCP).

```bash
pip install rustchain-mcp
rustchain-mcp
```

Or with uvx:

```bash
uvx rustchain-mcp
```

Learn more at [.github/mcp_server/rustchain_mcp/](.github/mcp_server/rustchain_mcp/).

## 🛠️ Scripts

Utility scripts for maintenance and automation:
- `backfill_xp_from_ledger_issue104.py`: One-off XP backfill from ledger data
- `update_xp_tracker_api.py`: Update contributor XP levels

See `.github/scripts/` for details.

## 📄 Guidelines

- [How to claim a bounty](bounties/CLAIMING.md)
- [PR submission rules](bounties/PR_GUIDELINES.md)
- [Wallet registration](bounties/WALLET.md)

## 📈 Stats & Leaderboard

Check [bounties/LEADERBOARD.md](bounties/LEADERBOARD.md) for top contributors and reward history.

## 📄 License

MIT — See [LICENSE](LICENSE)