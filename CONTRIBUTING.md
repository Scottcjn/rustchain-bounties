# Contributing to Rustchain

Thank you for your interest in contributing to Rustchain! Every contribution helps build a stronger Proof-of-Antiquity blockchain ecosystem.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your changes (`git checkout -b feature/my-contribution`)
4. **Make your changes** and test them
5. **Commit** with a clear message
6. **Push** to your fork and open a **Pull Request**

## 💰 Earning RTC Tokens

All merged contributions earn RTC tokens! See the bounty tiers:

| Tier | Reward | Examples |
|------|--------|----------|
| Micro | 1-10 RTC | Typo fixes, small documentation updates, simple tests |
| Standard | 20-50 RTC | New features, refactoring, new API endpoints |
| Major | 75-100 RTC | Security fixes, consensus improvements |
| Critical | 100-150 RTC | Vulnerability patches, protocol upgrades |

Browse [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues) to find tasks with specific RTC rewards.

## 📋 Types of Contributions

### Code
- Bug fixes and feature implementations
- Performance optimizations
- Test coverage improvements
- CI/CD pipeline enhancements

### Documentation
- README improvements
- API documentation updates
- Tutorials and guides
- Code comments and docstrings
- Translations (Spanish, Chinese, Japanese, etc.)

### Community
- Bug reports with clear reproduction steps
- Feature requests with detailed use cases
- Code reviews on open pull requests
- Helping others in [Discord](https://discord.gg/VqVVS2CW9Q)

## 🔧 Development Setup

### Prerequisites
- Rust 1.70+ installed via [rustup](https://rustup.rs/)
- Git version control
- A code editor (VS Code with rust-analyzer recommended)

### Getting Started
```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/rustchain.git
cd rustchain

# Build the project
cargo build

# Run tests
cargo test

# Run with logging
RUST_LOG=debug cargo run
```

## 📝 Contribution Guidelines

### Code Style
- Follow Rust naming conventions
- Use `cargo fmt` to format your code
- Run `cargo clippy` to catch common mistakes
- Add tests for new functionality

### Commit Messages
Use clear, descriptive commit messages:
```
feat: add transaction validation endpoint
fix: resolve memory leak in block processing
docs: update API documentation for /blocks endpoint
```

### Pull Request Process
1. Ensure all tests pass locally
2. Update documentation for any API changes
3. Fill out the pull request template completely
4. Reference any related issues or bounties
5. Be responsive to code review feedback

## 🐛 Reporting Issues

When reporting bugs, please include:
- **Environment details** (OS, Rust version, etc.)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Relevant logs or error messages**

## 🎯 Finding Issues to Work On

- Look for issues labeled `good first issue` for beginners
- Check `help wanted` labels for priority tasks
- Browse [bounty issues](https://github.com/Scottcjn/rustchain-bounties/issues) for RTC rewards
- Join our [Discord](https://discord.gg/VqVVS2CW9Q) to discuss potential contributions

## 🔐 Security Considerations

- **Never commit secrets** or private keys
- Report security vulnerabilities privately via Discord DM
- Follow secure coding practices
- Test edge cases and error conditions

## 📞 Getting Help

Need assistance? Reach out:
- **Discord**: [Join our community](https://discord.gg/VqVVS2CW9Q)
- **Issues**: Open a GitHub issue for bugs or questions
- **Discussions**: Use GitHub Discussions for general topics

## 📜 Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:
- Be respectful and constructive in all interactions
- Focus on technical merit in discussions
- Help create a positive community experience
- Report any inappropriate behavior to the maintainers

Thank you for contributing to Rustchain! 🚀