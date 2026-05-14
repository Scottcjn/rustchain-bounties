# Contributing to RustChain

Thank you for your interest in contributing to RustChain! This guide covers everything you need to get started, from setting up your development environment to submitting your first pull request.

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Development Environment Setup](#development-environment-setup)
- [Code Style Guide](#code-style-guide)
- [Testing Requirements](#testing-requirements)
- [Commit Message Convention](#commit-message-convention)
- [Pull Request Process](#pull-request-process)
- [Issue Report Template](#issue-report-template)
- [Bounty Workflow](#bounty-workflow)
- [Code of Conduct](#code-of-conduct)
- [Getting Help](#getting-help)

---

## How to Contribute

### Quick Start

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create a branch** for your changes (`git checkout -b feature/my-contribution`)
4. **Make your changes** and test them
5. **Commit** with a clear, conventional commit message
6. **Push** to your fork and open a **Pull Request**

### Types of Contributions

| Type | Examples |
|------|----------|
| **Code** | Bug fixes, features, performance improvements, test coverage |
| **Documentation** | README updates, API docs, tutorials, translations |
| **Community** | Bug reports, feature requests, code reviews, Discord help |

---

## Development Environment Setup

### Prerequisites

- **Git** >= 2.30
- **Node.js** >= 18 (for JavaScript/TypeScript components)
- **Rust** >= 1.70 (for Rust components) — install via [rustup](https://rustup.rs/)
- **Python** >= 3.9 (for scripts and tooling)

### Setup Steps

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/rustchain-bounties.git
cd rustchain-bounties

# 2. Add upstream remote
git remote add upstream https://github.com/Scottcjn/rustchain-bounties.git

# 3. Install JavaScript dependencies
npm install

# 4. Build Rust components (if applicable)
cargo build

# 5. Verify setup by running tests
npm test          # JavaScript tests
cargo test        # Rust tests
python -m pytest  # Python tests
```

### Keeping Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

---

## Code Style Guide

### General Principles

- **Readability first**: Write code that humans can understand
- **Consistency**: Follow existing patterns in the codebase
- **Simplicity**: Prefer simple solutions over clever ones
- **Documentation**: Comment "why", not "what"

### JavaScript / TypeScript

- Use **2-space indentation**
- Prefer `const` over `let`; avoid `var`
- Use **template literals** for string interpolation
- Use **async/await** over raw promises
- Run `npm run lint` before committing

### Rust

- Follow [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/)
- Use `cargo fmt` before committing
- Use `cargo clippy` and address all warnings
- Prefer `Result<T, E>` for error handling; avoid `unwrap()` in production code

### Python

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Use **f-strings** for string formatting
- Run `flake8` and `black` before committing

### Markdown

- Use **ATX-style headers** (`# Header`)
- Wrap long lines at **100 characters**
- Use **fenced code blocks** with language identifiers

---

## Testing Requirements

### Before Every PR

- [ ] All existing tests pass (`npm test`, `cargo test`, `python -m pytest`)
- [ ] New code includes appropriate test coverage
- [ ] Edge cases and error paths are tested
- [ ] No lint warnings (`npm run lint`, `cargo clippy`, `flake8`)

### Test Naming Convention

```
test_<unit>_<scenario>_<expected_result>
```

Example:
```rust
#[test]
fn test_bridge_transfer_insufficient_balance_returns_error() { ... }
```

### Writing Good Tests

1. **Arrange-Act-Assert** pattern
2. One assertion per test when possible
3. Test descriptive names over comments
4. Mock external dependencies
5. Test both happy paths and error paths

---

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

### Types

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code formatting (no logic change) |
| `refactor` | Code refactoring |
| `test` | Adding or updating tests |
| `chore` | Maintenance (CI, dependencies) |
| `security` | Security-related changes |

### Examples

```
feat(bridge): add wRTC balance verification endpoint
fix(consensus): correct PoA difficulty adjustment calculation
docs(readme): add POWER8 hardware requirements section
test(api): add integration tests for mining endpoints
```

---

## Pull Request Process

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Self-review completed
- [ ] All tests pass locally
- [ ] New code includes tests
- [ ] Documentation updated if needed
- [ ] Commit messages follow convention

### PR Description Template

```markdown
## What does this PR do?
Brief description of changes.

## Why?
Motivation and context. Link relevant issues.

## How to test?
Steps to verify the changes work.

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented if there are)

## Related Issues
Closes #<issue_number>
```

### Review Process

1. A maintainer will review your PR within **48-72 hours**
2. Address any requested changes promptly
3. Once approved, a maintainer will merge your PR
4. RTC tokens are distributed after merge

---

## Issue Report Template

When filing a bug report, please use this template:

```markdown
## Bug Report

### Description
A clear description of the bug.

### Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

### Expected Behavior
What you expected to happen.

### Actual Behavior
What actually happened.

### Environment
- OS: [e.g., Ubuntu 22.04]
- Node.js version: [e.g., 18.17.0]
- Rust version: [e.g., 1.70.0]

### Screenshots / Logs
If applicable, add screenshots or log output.

### Additional Context
Any other context about the problem.
```

### Feature Request Template

```markdown
## Feature Request

### Problem
What problem does this feature solve?

### Proposed Solution
Describe your proposed solution.

### Alternatives Considered
Other approaches you've thought about.

### Additional Context
Any other context, screenshots, or references.
```

---

## Bounty Workflow

### Earning RTC Tokens

All merged contributions earn RTC tokens:

| Tier | Reward | Examples |
|------|--------|----------|
| Micro | 1-10 RTC | Typo fix, small docs, simple test |
| Standard | 20-50 RTC | Feature, refactor, new endpoint |
| Major | 75-100 RTC | Security fix, consensus improvement |
| Critical | 100-150 RTC | Vulnerability patch, protocol upgrade |

Browse [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues) to find tasks.

### Claiming a Bounty

1. Check if already claimed in the issue comments
2. Comment on the issue:
   ```
   **Claiming this bounty.**
   
   [Brief description of your approach]
   
   Timeline: [Estimated completion time]
   — YOUR_USERNAME
   ```
3. Wait for acknowledgment, then start working

### Wallet Format

- Use **wallet names** (e.g., `your-github-username`), not cryptocurrency addresses
- Wallet names are used to track RTC earnings in the ledger

### Proof Requirements

- **Screenshots**: Clear, full-screen captures of the working feature
- **Code snippets**: Relevant implemented code sections
- **Test results**: Output from test commands
- **Video demonstrations** (optional): For complex UI/UX features

### Payout Authority

Only `@Scottcjn` (or a clearly labeled project automation account) authorizes RTC bounty disbursements. See [SECURITY.md](SECURITY.md#payment-authority-impersonation) for details.

---

## Code of Conduct

### Our Pledge

By participating in this project, you agree to maintain a **respectful, inclusive, and harassment-free** environment.

### Our Standards

**Positive behavior includes:**
- Being welcoming and inclusive
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy toward other community members

**Unacceptable behavior includes:**
- Harassment, insults, or derogatory comments
- Trolling or intentionally disruptive behavior
- Publishing others' private information
- Any conduct that would be inappropriate in a professional setting

### Enforcement

Report violations to the maintainers via GitHub or [Discord](https://discord.gg/VqVVS2CW9Q). All reports will be reviewed and investigated fairly.

---

## Getting Help

- **Discord**: [Join our server](https://discord.gg/VqVVS2CW9Q)
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Apache 2.0).

---

**Happy contributing! Every PR brings RustChain closer to its vision.** 🦀⚡
