# Contributing Guide

How to contribute to RustChain development.

## Ways to Contribute

1. **Code**: Fix bugs, add features, improve performance
2. **Documentation**: Write guides, improve existing docs
3. **Testing**: Report bugs, write test cases
4. **Design**: UI/UX for wallets and explorer
5. **Community**: Help users, answer questions

## Bounty System

RustChain uses a bounty board to reward contributors with RTC.

### How Bounties Work

1. Browse [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Abounty)
2. Comment to claim (include wallet ID)
3. Do the work, submit a PR
4. Maintainer reviews and approves
5. RTC transferred to your wallet

### Bounty Tiers

| Tier | RTC Range | Typical Scope |
|------|-----------|---------------|
| Micro | 1-10 RTC | Bug reports, docs fixes, small patches |
| Standard | 10-50 RTC | Feature implementation, test coverage |
| Major | 50-200 RTC | Architecture work, new subsystems |
| Critical | 200-500 RTC | Security hardening, consensus changes |

### Claiming a Bounty

Comment on the issue with:

```
**Claim**
- Wallet: your-wallet-id
- Agent/Handle: your-github-username
- Approach: brief description of how you'll solve it
```

One claim per person per bounty. First valid submission wins.

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- PostgreSQL (for node development)
- Rust 1.70+ (for performance-critical components)

### Clone Repository

```bash
git clone https://github.com/rustchain/node.git
cd node
```

### Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest tests/
```

### Code Style

Use `black` for Python formatting:

```bash
black .
```

Use `ruff` for linting:

```bash
ruff check .
```

## Contribution Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/rustchain-node.git
cd rustchain-node
git remote add upstream https://github.com/rustchain/node.git
```

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation
- `refactor/description` - Code refactoring

### 3. Make Changes

Write clean, well-tested code:

```python
def calculate_multiplier(hardware_type: str) -> float:
    multipliers = {
        "PowerPC_G4": 2.5,
        "PowerPC_G5": 2.0,
        "x86_64": 1.0,
    }
    return multipliers.get(hardware_type, 1.0)
```

Add tests:

```python
def test_calculate_multiplier():
    assert calculate_multiplier("PowerPC_G5") == 2.0
    assert calculate_multiplier("x86_64") == 1.0
    assert calculate_multiplier("unknown") == 1.0
```

### 4. Commit Changes

Use conventional commits:

```bash
git add .
git commit -m "feat: add hardware multiplier calculation"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `perf:` - Performance improvement

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Open a pull request on GitHub:

**PR Template:**
```markdown
## Description
Brief description of changes.

## Related Issue
Closes #123

## Changes Made
- Added X
- Fixed Y
- Updated Z

## Testing
- [ ] All tests pass
- [ ] Added new tests
- [ ] Manual testing completed

## Wallet ID
my-wallet-id (for bounty payout)
```

### 6. Code Review

Maintainers will review your PR:
- Address feedback
- Update code as needed
- Ensure CI passes

### 7. Merge and Payout

Once approved:
- PR merged to main
- RTC transferred to your wallet
- Transaction recorded on-chain

## Code Guidelines

### Python Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions small and focused

**Good:**
```python
def validate_attestation(fingerprint: dict) -> bool:
    """Validate hardware attestation fingerprint.
    
    Args:
        fingerprint: 6-point hardware fingerprint
        
    Returns:
        True if valid, False otherwise
    """
    required_keys = {"cpu_model", "cpu_cores", "arch", "vendor_id", "physical_id", "timestamp"}
    return all(key in fingerprint for key in required_keys)
```

**Bad:**
```python
def validate(fp):
    # No docstring, no type hints, unclear name
    return all(k in fp for k in ["cpu_model", "cpu_cores", "arch", "vendor_id", "physical_id", "timestamp"])
```

### Testing

- Write tests for all new code
- Aim for >80% coverage
- Use pytest fixtures for setup

**Example:**
```python
import pytest
from rustchain import RustChainClient

@pytest.fixture
def client():
    return RustChainClient(node_url="https://testnet.rustchain.org")

def test_get_balance(client):
    balance = client.get_balance("test-wallet")
    assert "balance" in balance
    assert isinstance(balance["balance"], float)
```

### Security

- Never commit private keys or secrets
- Validate all user inputs
- Use parameterized queries (no SQL injection)
- Sanitize error messages (no info leaks)

**Good:**
```python
def get_balance(wallet_id: str) -> dict:
    if not wallet_id.isalnum():
        raise ValueError("Invalid wallet ID")
    cursor.execute("SELECT balance FROM wallets WHERE wallet_id = ?", (wallet_id,))
    return cursor.fetchone()
```

**Bad:**
```python
def get_balance(wallet_id):
    # SQL injection vulnerable
    cursor.execute(f"SELECT balance FROM wallets WHERE wallet_id = '{wallet_id}'")
    return cursor.fetchone()
```

## Submitting Issues

### Bug Reports

Include:
1. Description of the bug
2. Steps to reproduce
3. Expected vs actual behavior
4. System info (OS, Python version, hardware)
5. Relevant logs

**Template:**
```markdown
## Bug Description
Miner crashes when hardware fingerprint collection fails.

## Steps to Reproduce
1. Run miner on unsupported hardware
2. Wait for attestation submission
3. Miner crashes with traceback

## Expected Behavior
Miner should handle error gracefully and retry.

## Actual Behavior
Miner crashes with `KeyError: 'cpu_model'`.

## System Info
- OS: Ubuntu 22.04
- Python: 3.10.12
- Hardware: Raspberry Pi 4

## Logs
```
Traceback (most recent call last):
  File "rustchain_miner.py", line 42, in collect_fingerprint
    cpu_model = hardware_info['cpu_model']
KeyError: 'cpu_model'
```
```

### Feature Requests

Include:
1. Use case
2. Expected behavior
3. Potential implementation approach
4. Bounty amount (if offering)

**Template:**
```markdown
## Feature Request
Add support for ARM-based vintage hardware multipliers.

## Use Case
Raspberry Pi enthusiasts want to participate in mining with bonus rewards for older models.

## Proposed Behavior
- Raspberry Pi 1: 1.5x multiplier
- Raspberry Pi 2: 1.3x multiplier
- Raspberry Pi 3: 1.2x multiplier

## Implementation Ideas
Extend hardware detection to identify ARM models, add multiplier config.

## Bounty
Offering 25 RTC for implementation.
```

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers
- No harassment or discrimination

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Discord**: Real-time chat (coming soon)
- **Email**: security@rustchain.org (security issues)

## Recognition

Top contributors are recognized:

1. **Contributor Leaderboard**: Top 10 by RTC earned
2. **Hall of Fame**: Exceptional contributions
3. **Core Team**: Consistent high-quality contributors

## Getting Started

### Good First Issues

Look for issues labeled `good-first-issue`:

```bash
https://github.com/Scottcjn/rustchain-bounties/labels/good-first-issue
```

Typical good first issues:
- Documentation improvements
- Small bug fixes
- Adding tests
- Code cleanup

### Mentorship

Need help getting started? Tag `@maintainers` in the issue or discussion.

## License

All contributions are licensed under MIT License.

By contributing, you agree to license your contributions under the same terms.

## Next Steps

- [Browse open bounties](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Abounty)
- [Set up a miner](miner-setup-guide.md) to earn RTC
- [Read the API reference](api-reference.md) to understand the system
- [Join the community](https://github.com/rustchain/node/discussions)
