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

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/rustchain-bounties.git
cd rustchain-bounties

# Install dependencies
npm install  # or cargo build (for Rust components)

# Run tests
npm test     # or cargo test
```

## 📝 Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks (CI, dependencies)
- `security`: Security-related changes

**Examples:**
```
feat(bridge): add wRTC balance verification endpoint
fix(consensus): correct PoA difficulty adjustment calculation
docs(readme): add POWER8 hardware requirements section
test(api): add integration tests for mining endpoints
```

## 🔍 Pull Request Guidelines

### Before Submitting
- [ ] Code follows the project's style guidelines
- [ ] Self-review of your changes completed
- [ ] Tests pass locally
- [ ] New code includes appropriate tests
- [ ] Documentation updated if needed

### PR Description Template
```markdown
## What does this PR do?
Brief description of changes.

## Why?
Motivation and context.

## How to test?
Steps to verify the changes work.

## Related Issues
Closes #<issue_number>
```

### Review Process
1. A maintainer will review your PR within 48-72 hours
2. Address any requested changes
3. Once approved, a maintainer will merge your PR
4. RTC tokens will be distributed after merge

## 🎯 Good First Issues

New to Rustchain? Start with issues labeled [`good first issue`](https://github.com/Scottcjn/Rustchain/labels/good%20first%20issue). These are specifically designed for newcomers.

## ⚖️ Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive, and harassment-free environment. Be kind, be constructive, and help each other grow.

## 📬 Getting Help

- **Discord**: [Join our server](https://discord.gg/VqVVS2CW9Q)
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Apache 2.0).

---

**Happy contributing! Every PR brings Rustchain closer to its vision.** 🦀⛓️
