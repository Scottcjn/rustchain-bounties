# BCOS Homebrew Formula

Homebrew formula for BCOS v2 (Beacon Certified Open Source) engine.

## Installation

```bash
# Add the tap
brew tap Scottcjn/tap

# Install BCOS
brew install bcos

# Or install directly from this formula
brew install --formula ./bcos.rb
```

## Usage

```bash
# Scan a directory for BCOS certification
bcos scan .

# Verify a BCOS certification ID
bcos verify BCOS-xxx

# Certify a directory
bcos certify .

# Get help
bcos --help
```

## Dependencies

- python3.11 (required)
- semgrep (optional)
- pip-audit (optional)

## Formula Details

- **Source**: PyPI (clawrtc 1.8.0+) or GitHub
- **License**: MIT
- **Homepage**: https://rustchain.org/bcos/
