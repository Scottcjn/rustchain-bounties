# Contributing to RustChain Bounties

Thank you for your interest in contributing to RustChain bounties! This guide explains how to participate in the bounty program, claim tasks, submit proofs, and earn RTC tokens.

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

## 🎯 Bounty Workflow Guide

### Finding Bounties
1. Go to the [rustchain-bounties repository issues](https://github.com/Scottcjn/rustchain-bounties/issues)
2. Look for issues with bounty labels (e.g., `[DOC]`, `[FEAT]`, `[BUG]`)
3. Check the issue description for RTC reward information
4. **Important**: Read the [Anti-Farming Rules (#452)](https://github.com/Scottcjn/rustchain-bounties/issues/452) before claiming any bounty

### Claiming a Bounty
1. **Check if already claimed**: Read the issue comments to see if someone has already claimed it
2. **Claim format**: Comment on the issue with:
   ```
   **Claiming this bounty.**
   
   [Brief description of your approach]
   
   Timeline: [Estimated completion time]
   -BetsyMalthus (or your GitHub username)
   ```
3. **Wait for acknowledgment**: If no one else has claimed, you can proceed
4. **Start working**: Fork the repository and begin implementation

### Why claims get turned down

Almost every declined claim we see falls into one of these. None of them are about the quality of your code, and none of them are personal. They are just the things that make a claim impossible to verify or pay.

**The deliverable is the thing itself, not a file describing it.**
If a bounty asks you to star a repo, record a video, publish a post, join the Discord, or review an open PR, then the star, the video, the post, the membership, or the review is the work. Adding a Python file named after the issue number does not complete it. Several of these arrive every week and none of them can be paid, because there is nothing to check.

**A file nothing imports is not a fix.**
Dropping `fix_1234.py` in the repository root, where no module imports it and no test covers it, does not change the behaviour the bounty is about. Change the code that actually runs, and add a test that fails before your change and passes after it.

**Evidence has to be checkable by someone who is not you.**
Links are opened. Stars are checked through the GitHub API. Videos are watched. If a link 404s, if a submission still contains placeholder text like `[your hardware here]`, or if a claimed star does not appear on your account, the claim cannot be verified and will be declined even if you did the work. Post the real artifact.

**Use one wallet, consistently.**
Pick one payout identity and keep it. When the same person claims under two different wallets, we cannot tell which one is theirs, and payment stops until it is resolved. If you need to change your payout address, say so plainly in one place rather than switching mid-stream.

**Check the work is not already done.**
Read the whole thread before claiming. A good number of claims arrive for bounties that were already paid, or for bugs someone else already fixed and merged. It costs you nothing to check and it saves you writing something that cannot be accepted.

**Do not paste the same claim on several issues.**
One claim per bounty, in your own words, describing what you will actually do. Identical text across multiple threads reads as volume rather than intent, and it makes the genuine claims underneath it harder to find.

**Racing is normal and it is not personal.**
Several people often work the same bounty. Where submissions are comparable, the first mergeable one usually wins, and the rest get closed with thanks. That is not a judgement about your work. If yours was close, say so and we will point you at something unclaimed.

### If you are new and unsure

Ask in the issue before you start. A short comment saying what you plan to do takes a minute and saves you from building the wrong thing. We would much rather answer a question up front than decline finished work.

### Wallet Format
- **Use wallet names, not addresses**: `your-wallet-name` (e.g., `BetsyMalthus`)
- **Do not include cryptocurrency addresses** in comments
- Wallet names are used to track RTC earnings in the ledger

### Proof Requirements
For bounties requiring proof of completion:
1. **Screenshots**: Clear, full-screen screenshots showing the working feature
2. **Code snippets**: Relevant sections of implemented code
3. **Test results**: Output from test commands
4. **Video demonstrations** (optional): For complex UI/UX features

### Submission Process
1. **Complete the work** in your forked repository
2. **Create a Pull Request** to the main repository
3. **Link to the issue**: In your PR description, include `Closes #<issue_number>`
4. **Provide proof**: Attach screenshots or other required proof in the PR comments
5. **Wait for review**: Maintainers will review within 48-72 hours

### After Approval
1. **PR merged**: Once approved, a maintainer will merge your PR
2. **RTC distribution**: RTC tokens will be distributed to your wallet name
3. **Ledger update**: Your earnings will be recorded in [BOUNTY_LEDGER.md](BOUNTY_LEDGER.md)

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
- Helping others in [Discord](https://discord.gg/XnRp7M5gBW)
- Helping others in [Telegram](https://t.me/+l8dHTjXCBNM1MTIx)

## Payout Authority

Only `@Scottcjn` (or a clearly labeled project automation account speaking on his behalf, with a matching project-issued `pending_id` + `tx_hash`) authorizes RTC bounty disbursements. Anyone else posting "I'll send the RTC" on a bounty issue is not a valid payout notice — see [SECURITY.md § Payment-Authority Impersonation](SECURITY.md#payment-authority-impersonation).

## 🔧 Development Setup

```bash
# Clone your fork
git clone https://github.com/Scottcjn/rustchain-bounties.git
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

New to RustChain? Start with issues labeled [`good first issue`](https://github.com/Scottcjn/Rustchain/labels/good%20first%20issue). These are specifically designed for newcomers.

## ⚖️ Code of Conduct

By participating in this project, you agree to maintain a respectful, inclusive, and harassment-free environment. Be kind, be constructive, and help each other grow.

## 📬 Getting Help

- **Discord**: [Join our server](https://discord.gg/XnRp7M5gBW)
- **Telegram**: [Join our server](https://t.me/+l8dHTjXCBNM1MTIx)
- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and ideas

## 🔒 Security Reporting

If you discover a security vulnerability in RustChain, please report it responsibly:

1. **Do not open a public issue** for security vulnerabilities
2. **Report privately** via GitHub Private Vulnerability Reporting, which is
   enabled and open to anyone. Use the repository that actually contains the
   flaw: [Rustchain](https://github.com/Scottcjn/Rustchain/security/advisories/new)
   for node, consensus, wallet, and miner issues,
   [bottube](https://github.com/Scottcjn/bottube/security/advisories/new) for
   BoTTube, or [this repo](https://github.com/Scottcjn/rustchain-bounties/security/advisories/new)
   for the bounty program itself.
3. **If you cannot reach GitHub**, or your agent harness returns
   `403 Resource not accessible by integration`, email the monitored project
   contact instead: **sophia.eagent@gmail.com**. Please do not use addresses
   found in commit history; they are personal accounts and are not monitored as
   a security queue.
4. **Include**: Steps to reproduce, potential impact, and suggested fix (if any)
5. **Response**: Maintainers will acknowledge within 48 hours and work with you on a fix
6. **Disclosure**: Coordinated disclosure will be arranged after a fix is developed

Security bounties may qualify for the **Critical** tier (100-150 RTC) depending on severity.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (Apache 2.0).

---

**Happy contributing! Every PR brings RustChain closer to its vision.**
