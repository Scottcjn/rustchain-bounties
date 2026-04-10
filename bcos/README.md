# BCOS v2 Web Tools — Bounties #2294 & #2292

Two static HTML pages implementing BCOS v2 tooling for rustchain.org.

## Files

| File | Bounty | Description |
|------|--------|-------------|
| `compare.html` | #2294 (10 RTC) | Side-by-side comparison of BCOS v2 vs Altermenta Nucleus Verify |
| `badge-generator.html` | #2292 (15 RTC) | Interactive tool to generate BCOS trust badges |

## compare.html — Feature Comparison Page

- Vintage terminal aesthetic matching rustchain.org
- Side-by-side table: BCOS v2 vs Nucleus Verify across 15+ features
- BCOS wins on every metric: free, open source, on-chain proof, CLI, etc.
- Mobile responsive
- Links to BCOS verification page and documentation

**Deploy:** `rustchain.org/bcos/compare.html`

## badge-generator.html — BCOS Badge Generator

- Enter a BCOS cert_id (e.g. `BCOS-A1B2C3`) or GitHub repo URL
- Choose badge style: flat, flat-square, for-the-badge, plastic
- Live badge preview
- Copy-paste Markdown or HTML embed code
- Example badges shown at the bottom
- No backend required — static HTML/JS only

**Deploy:** `rustchain.org/bcos/badge-generator.html`

**Badge endpoint:** `GET https://50.28.86.131/bcos/badge/{cert_id}-{style}.svg`  
**Verify page:** `https://rustchain.org/bcos/verify/{cert_id}`

## Bounty Payment

Wallet: `eB51DWp1uECrLZRLsE2cnyZUzfRWvzUzaJzkatTpQV9`

## Author

Subagent scan-du1 · 2026-03-29
