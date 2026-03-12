# Contributing to RustChain

Thank you for your interest in contributing to RustChain! Every contribution helps build a stronger Proof-of-Antiquity blockchain ecosystem.

This guide covers everything you need to know about contributing to the RustChain project, from submitting issues to earning RTC tokens.

---

## 📑 Table of Contents

1. [Quick Start](#-quick-start)
2. [Earning RTC Tokens](#-earning-rtc-tokens)
3. [Types of Contributions](#-types-of-contributions)
4. [How to Submit an Issue](#-how-to-submit-an-issue)
5. [How to Submit a Pull Request](#-how-to-submit-a-pull-request)
6. [Code Style Guidelines](#-code-style-guidelines)
7. [Development Setup](#-development-setup)
8. [Testing Guidelines](#-testing-guidelines)
9. [Review Process](#-review-process)
10. [Getting Help](#-getting-help)

---

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/rustchain-bounties.git
   cd rustchain-bounties
   ```
3. **Create a branch** for your changes
   ```bash
   git checkout -b feature/my-contribution
   ```
4. **Make your changes** and test them
5. **Commit** with a clear message (see [Commit Message Convention](#-commit-message-convention))
6. **Push** to your fork and open a **Pull Request**

---

## 💰 Earning RTC Tokens

All merged contributions earn RTC tokens! Browse [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues) to find tasks with specific RTC rewards.

### Bounty Tiers

| Tier | Reward (RTC) | Examples |
|------|--------------|----------|
| Micro | 1-10 | Typo fix, small docs, simple test |
| Standard | 10-50 | Feature, refactor, new endpoint |
| Major | 50-200 | Security fix, consensus improvement |
| Critical | 200-500 | Vulnerability patch, protocol upgrade |

### RTC Wallet Setup

**RTC wallets are simple string names**, not blockchain addresses. Pick any name you like:
- `my-cool-wallet`
- `alice`
- `builder-fred`

**Important:**
- Do NOT submit ETH, SOL, or ERG addresses as your wallet
- Those chains exist for bridging INTO the RTC economy — not for cashing out
- RustChain is a long-term project. Bounties exist to grow and support the ecosystem

Start mining with reproducible instructions only:
- Use pinned versions/commits
- Provide checksum or container digest
- Avoid unpinned `pip install` in bounty posts

---

## 📋 Types of Contributions

### Code Contributions
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

### Security
- Security audits
- Penetration testing
- Vulnerability reporting (see [SECURITY.md](SECURITY.md))

---

## 📝 How to Submit an Issue

### Before Creating an Issue
1. **Search existing issues** to avoid duplicates
2. **Check if it's a question** — use [Discussions](https://github.com/Scottcjn/rustchain-bounties/discussions) for questions
3. **Gather information** — reproduction steps, logs, screenshots

### Issue Types

#### Bug Reports
Use the bug report template and include:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, version, etc.)
- Logs or screenshots if applicable

#### Feature Requests
Include:
- Problem statement
- Proposed solution
- Use cases
- Benefits to the project

#### Bounty Issues
For creating new bounties, use the [Bounty Issue Template](https://github.com/Scottcjn/rustchain-bounties/issues/new?template=bounty.yml) and include:
- **Goal**: What needs to be built or fixed
- **Scope & Requirements**: In-scope items and acceptance criteria
- **Tier**: Micro/Standard/Major/Critical
- **RTC Payout**: Exact amount
- **Skills Needed**: Required expertise
- **Target Repo/Reference**: Exact location for changes
- **Supply-Chain Hygiene**: Pinned versions and checksums

---

## 🔀 How to Submit a Pull Request

### Before Submitting
- [ ] Code follows the project's style guidelines
- [ ] Self-review of your changes completed
- [ ] Tests pass locally
- [ ] New code includes appropriate tests
- [ ] Documentation updated if needed
- [ ] No secrets or credentials committed

### PR Submission Steps

1. **Fork and clone** the repository (if not already done)
   ```bash
   git clone https://github.com/YOUR_USERNAME/rustchain-bounties.git
   cd rustchain-bounties
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit them using the [commit convention](#-commit-message-convention)

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request** on GitHub
   - Use the [PR template](.github/PULL_REQUEST_TEMPLATE.md)
   - Link the related issue (e.g., `Closes #123`)
   - Fill in all required sections

### PR Description Template

```markdown
## Bounty Submission

**Bounty**: Closes #ISSUE_NUMBER

**RTC Wallet**: YOUR_WALLET_NAME

## BCOS Checklist (Required For Non-Doc PRs)

- [ ] Add a tier label: `BCOS-L1` or `BCOS-L2`
- [ ] Include SPDX header in new code files
- [ ] Provide test evidence (commands + output or screenshots)

## Changes

- Brief description of changes

## Testing

- [ ] Tests pass locally
- [ ] Demo or reproduction steps provided

## Evidence

- Proof links (screenshots/logs/metrics):
- Before vs after summary:
- Validation method:

## Quality Gate Self-Score (0-5)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Impact | | |
| Correctness | | |
| Evidence | | |
| Craft | | |

## Checklist

- [ ] All acceptance criteria from the bounty issue are met
- [ ] Code is tested
- [ ] No secrets or credentials committed

## Supply-Chain Proof (Required if changed)

- [ ] Dependency versions are pinned
- [ ] External repo references include commit SHA
- [ ] Artifact checksum/container digest provided
```

---

## 📏 Code Style Guidelines

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (CI, dependencies)
- `security`: Security-related changes

#### Examples
```
feat(bridge): add wRTC balance verification endpoint
fix(consensus): correct PoA difficulty adjustment calculation
docs(readme): add POWER8 hardware requirements section
test(api): add integration tests for mining endpoints
```

### Code Style

#### Rust Code
- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- Use `rustfmt` for formatting
- Run `clippy` for linting
- Include doc comments for public APIs

#### Python Code
- Follow [PEP 8](https://pep8.org/)
- Use type hints where applicable
- Include docstrings (Google or NumPy style)
- Run `black` for formatting
- Run `flake8` or `pylint` for linting

#### General
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic
- Write tests for new code

### License Headers

For new code files, include the SPDX license identifier near the top:

```rust
// SPDX-License-Identifier: Apache-2.0
```

```python
# SPDX-License-Identifier: Apache-2.0
```

---

## 🔧 Development Setup

### Prerequisites
- Git
- Rust (for Rust components): [Install](https://rustup.rs/)
- Python 3.8+ (for Python scripts)
- Node.js (for web components, if applicable)

### Clone and Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/rustchain-bounties.git
cd rustchain-bounties

# Install Rust dependencies (for Rust components)
cargo build

# Install Python dependencies (for Python scripts)
pip install -r requirements.txt

# Run tests
cargo test      # For Rust
python -m pytest  # For Python
```

### Environment Configuration

Copy the example configuration and customize:

```bash
cp config.example.toml config.toml
```

---

## 🧪 Testing Guidelines

### Running Tests

```bash
# Rust tests
cargo test

# Python tests
python -m pytest

# All tests
./build.sh test
```

### Writing Tests

- **Unit tests**: Test individual functions/components
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows

### Test Coverage

- Aim for high coverage on new code
- Include edge cases
- Test error conditions
- Document test scenarios

---

## 🔍 Review Process

### Timeline
- A maintainer will review your PR within **48-72 hours**
- Address any requested changes promptly
- Once approved, a maintainer will merge your PR
- RTC tokens will be distributed after merge

### Quality Gate Scorecard

Submissions are evaluated using a quality gate scorecard (0-5 each):

| Dimension | Description |
|-----------|-------------|
| Impact | How much does this improve the project? |
| Correctness | Does it work correctly? |
| Evidence | Is there proof of testing/validation? |
| Craft | Quality of implementation |

**Suggested gate**: Minimum total 13/20, Correctness must be > 0

### Global Disqualifiers

Submissions matching these will be rejected with no payout:
- AI slop / template-only output
- Duplicate or noisy submissions
- Missing proof links or validation evidence
- Repeated low-effort near-identical content
- Submitting ETH/SOL/ERG addresses instead of RTC wallet names

---

## 🎯 Good First Issues

New to RustChain? Start with issues labeled [`good first issue`](https://github.com/Scottcjn/rustchain-bounties/labels/good%20first%20issue). These are specifically designed for newcomers.

---

## 📬 Getting Help

- **Discord**: [Join our server](https://discord.gg/VqVVS2CW9Q)
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Email**: See repository maintainers

### Resources
- [RustChain Documentation](https://rustchain.org)
- [Block Explorer](https://50.28.86.131/explorer)
- [Security Best Practices](SECURITY_BEST_PRACTICES.md)
- [Logging Best Practices](LOGGING_BEST_PRACTICES.md)

---

## ⚖️ Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive, and harassment-free environment. Be kind, be constructive, and help each other grow.

We do not tolerate:
- Harassment or discrimination
- Offensive comments
- Personal attacks
- Spam or self-promotion without value

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (Apache 2.0).

---

## 🏆 Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md) (if exists)
- Release notes for significant contributions
- Community highlights in Discord

---

**Happy contributing! Every PR brings RustChain closer to its vision.** 🦀⛓️

---

## 📚 Additional Resources

- [Bounty Hunter Framework](docs/AGENT_BOUNTY_HUNTER_FRAMEWORK.md)
- [Bounty Hygiene](docs/BOUNTY_HYGIENE.md)
- [Miners Setup Guide](docs/MINERS_SETUP_GUIDE.md)
- [Network Topology](docs/NETWORK_TOPOLOGY.md)
- [Security Audit Checklist](docs/SECURITY_AUDIT_CHECKLIST.md)
- [Threat Modeling Guide](docs/THREAT_MODELING_GUIDE.md)
