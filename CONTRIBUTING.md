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
| ---- | ------ | -------- |
| Micro | 1-10 RTC | Typo fix, small docs, simple test |
| Standard | 20-50 RTC | Feature, refactor, new endpoint |
| Major | 75-100 RTC | Security fix, consensus improvement |
| Critical | 100-150 RTC | Vulnerability patch, protocol upgrade |

Browse [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues) to find tasks with specific RTC rewards.

## 📋 Types of Contributions

### Code
- Bug fixes and feature implementations
- Performance improvements
- Test coverage improvements
- CI/CD pipeline enhancements

### Documentation
- README improvements
- API documentation
- Tutorials and guides
- Code comments and docstrings
- Translations (Spanish, Chinese, Japanese, etc.)

### Community
- Bug reports with reproduction steps
- Feature requests with use cases
- Code reviews on open PRs
- Helping others in [Discord](https://discord.gg/VqVVS2CW9Q)

## 🔧 Development Setup

### Prerequisites
- **Rust** (latest stable) - Install via [rustup](https://rustup.rs/)
- **Git** for version control
- **Node.js** (16+) for frontend components (if applicable)
- **Docker** (optional, for containerized development)

### Local Environment Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# Install Rust dependencies
cargo build

# Run tests to ensure everything works
cargo test

# Start development server (if applicable)
cargo run

# For frontend development (if applicable)
npm install
npm run dev
```

### Environment Variables
Create a `.env` file in the project root with:
```env
# Example environment variables
RUST_LOG=debug
DATABASE_URL=sqlite://data.db
RPC_PORT=8545
```

## 🎯 Bounty-Specific Contribution Process

### Finding Bounties
1. Check [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues)
2. Look for issues labeled with `bounty:` tags
3. Read the full issue description for requirements
4. Comment "I'd like to work on this" to claim it

### Working on Bounties
1. **Claim the bounty** by commenting on the issue
2. **Fork and clone** the repository
3. **Create a branch** named after the bounty: `bounty/issue-number-description`
4. **Follow the specific requirements** in the bounty description
5. **Test thoroughly** - bounties require working solutions
6. **Submit PR** with reference to the bounty issue

### Bounty Review Process
- All bounty submissions are reviewed within 48 hours
- RTC rewards are distributed after PR merge
- Incomplete or non-functional submissions may be rejected
- You can resubmit with fixes if needed

## 📝 Pull Request Guidelines

### Before Submitting
- [ ] Code compiles without warnings
- [ ] All tests pass (`cargo test`)
- [ ] New features have tests
- [ ] Documentation is updated
- [ ] Code follows project style guidelines

### PR Title Format
Use conventional commit format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

Examples:
- `feat: add stake delegation endpoint`
- `fix: resolve memory leak in consensus module`
- `docs: update API documentation for v2.0`

### PR Description Template
```markdown
## Description
Brief description of changes

## Related Issue
Closes #[issue number]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (specify)

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

## 📐 Code Style Standards

### Rust Guidelines
- Follow [official Rust style guide](https://doc.rust-lang.org/nightly/style-guide/)
- Use `cargo fmt` for automatic formatting
- Run `cargo clippy` for linting
- Maximum line length: 100 characters
- Use meaningful variable and function names

### Code Organization
```
src/
├── lib.rs          # Main library entry
├── config/         # Configuration modules
├── consensus/      # Consensus algorithm
├── network/        # P2P networking
├── storage/        # Database and file storage
├── api/           # REST API endpoints
├── cli/           # Command line interface
└── utils/         # Utility functions
```

### Documentation Standards
- All public functions must have rustdoc comments
- Include examples in documentation
- Document error conditions and panics
- Use `#[doc(hidden)]` for internal APIs

Example:
```rust
/// Validates a blockchain transaction
///
/// # Arguments
/// * `tx` - The transaction to validate
/// * `context` - Current blockchain state
///
/// # Returns
/// * `Ok(())` if valid
/// * `Err(ValidationError)` if invalid
///
/// # Example
/// ```
/// let result = validate_transaction(&tx, &context);
/// assert!(result.is_ok());
/// ```
pub fn validate_transaction(tx: &Transaction, context: &BlockchainState) -> Result<(), ValidationError> {
    // Implementation
}
```

### Testing Requirements
- Unit tests for all public functions
- Integration tests for major features
- Property-based tests for consensus logic
- Benchmark tests for performance-critical code

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_transaction_validation() {
        // Test implementation
    }

    #[tokio::test]
    async fn test_async_function() {
        // Async test implementation
    }
}
```

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
cargo test

# Run specific test module
cargo test consensus

# Run with output
cargo test -- --nocapture

# Run benchmarks
cargo bench
```

### Test Categories
- **Unit tests**: Test individual functions and modules
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Performance tests**: Benchmark critical paths

## 🚀 Deployment and Release

### Version Management
- Follow [Semantic Versioning](https://semver.org/)
- Update `Cargo.toml` version before release
- Tag releases with `git tag v1.2.3`

### Release Process
1. Update version numbers
2. Update CHANGELOG.md
3. Run full test suite
4. Create release PR
5. Tag and publish after merge

## 🤝 Community Guidelines

### Communication
- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers get started
- Use [Discord](https://discord.gg/VqVVS2CW9Q) for real-time discussion

### Code Review Etiquette
- Review code, not the person
- Suggest improvements with examples
- Approve when ready, request changes when needed
- Respond to feedback promptly

## 🆘 Getting Help

### Resources
- [Project Documentation](./docs/)
- [Discord Community](https://discord.gg/VqVVS2CW9Q)
- [GitHub Discussions](https://github.com/Scottcjn/rustchain/discussions)
- [Bounty Tracker](https://github.com/Scottcjn/rustchain-bounties)

### Reporting Issues
When reporting bugs, include:
- Rust version (`rustc --version`)
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages and logs

### Security Issues
Report security vulnerabilities privately to [security@rustchain.io](mailto:security@rustchain.io)

---

**Ready to contribute?** Check out our [good first issues](https://github.com/Scottcjn/rustchain/labels/good%20first%20issue) or browse available [bounties](https://github.com/Scottcjn/rustchain-bounties/issues) to start earning RTC tokens today!