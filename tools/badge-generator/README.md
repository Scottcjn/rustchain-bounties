# BCOS Badge Generator

A web tool for generating BCOS (Beacon Certified Open Source) trust score badges for repositories.

## Overview

BCOS Badge Generator allows users to:
- Enter a GitHub repository URL or BCOS certificate ID
- Preview badges in multiple styles (flat, flat-square, for-the-badge)
- Copy markdown or HTML embed code for use in README files

## Features

- **Terminal Aesthetic**: Vintage green-on-black design with scanlines
- **Multiple Badge Styles**: Choose from flat, flat-square, or for-the-badge styles
- **Easy Embed**: Copy ready-to-use markdown or HTML code
- **No Backend Required**: Static HTML/JS that calls the BCOS API directly

## Usage

Simply open `index.html` in a web browser.

### Input Options

1. **GitHub Repository URL**: e.g., `https://github.com/username/repo`
2. **Repository Path**: e.g., `username/repo`
3. **BCOS Certificate ID**: e.g., `BCOS-xxx`

### Badge Styles

The tool generates badges in three popular styles:

- **flat**: Standard flat badge (Shields.io default)
- **flat-square**: Square corners, flat design
- **for-the-badge**: Bold, badge-appropriate styling

### Embed Code Examples

**Markdown:**
```markdown
[![BCOS](https://rustchain.org/bcos/badge/BCOS-xxx.svg)](https://rustchain.org/bcos/verify/BCOS-xxx)
```

**HTML:**
```html
<a href="https://rustchain.org/bcos/verify/BCOS-xxx" target="_blank">
  <img src="https://rustchain.org/bcos/badge/BCOS-xxx.svg" alt="BCOS Trust Score">
</a>
```

## BCOS Tiers

BCOS certificates are awarded based on trust scores:

| Tier | Score | Description |
|------|-------|-------------|
| L0 | ≥40 | Automated verification |
| L1 | ≥60 | Agent-reviewed |
| L2 | ≥80 | Human-signed |

## API Reference

- **Badge SVG**: `GET /bcos/badge/{cert_id}.svg`
- **Verify Page**: `https://rustchain.org/bcos/verify/{cert_id}`
- **Verify API**: `GET /bcos/verify/{cert_id}`

## Files

```
badge-generator/
├── index.html    # Main HTML page
├── styles.css    # Terminal aesthetic styles
├── app.js        # Application logic
└── README.md     # This file
```

## License

MIT License - See [rustchain-bounties](https://github.com/scottcjn/rustchain-bounties)

## Bounty

This tool was built as part of [Issue #2292](https://github.com/scottcjn/rustchain-bounties/issues/2292) on the rustchain-bounties repository.
