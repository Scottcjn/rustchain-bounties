# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| &lt; latest | :x:               |

## Reporting a Vulnerability

We take security seriously at Rustchain. If you discover a security vulnerability, please follow responsible disclosure:

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email your findings to the repository maintainers via GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
3. Alternatively, reach out on [Discord](https://discord.gg/XnRp7M5gBW) or [Telegram](https://t.me/+l8dHTjXCBNM1MTIx) via DM to a maintainer

### What to Include

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)

### What to Expect

- **Acknowledgment** within 48 hours of your report
- **Initial assessment** within 1 week
- **Resolution timeline** communicated after assessment
- **Credit** in the security advisory (unless you prefer to remain anonymous)

### Bounty Rewards

Security-related contributions are eligible for RTC token rewards.

**Rates were reduced 2026-06-11 as RTC's reference value rose** (1,300+ holding
wallets; reference rate stepped up, so nominal RTC per finding steps down to keep
USD-equivalent value per finding stable). The anchor is **USD value per finding**,
not a fixed RTC number.

| Severity | Reward | USD-equiv anchor | Example |
| -------- | ------ | ---------------- | ------- |
| **Critical** | **50 RTC** | ~$10 | Remote fund theft, RCE, consensus break, or auth bypass **on a live node/wallet endpoint** |
| **High** | **25 RTC** | ~$5 | Privilege escalation or sensitive-data exposure on a **deployed** surface |
| **Medium** | **13 RTC** | ~$2.50 | Limited-impact logic flaw or DoS on a **deployed** surface, with PoC |
| **Low** | **5 RTC** | ~$1 | Minor info disclosure on a **deployed** surface, with PoC |
| Out of scope | **0 RTC** | — | Acknowledged with thanks, not paid (see below) |

Severity is assigned by the maintainer based on **demonstrated impact on a
deployed surface**, not on the reporter's self-rated CVSS. A "CRITICAL" label on a
theoretical or undeployed-code finding does not make it payable.

### Deployment Scope (READ THIS BEFORE FILING)

A security finding is **only payable if it includes a working proof-of-concept
against a named, deployed, reachable surface** from the in-scope list below.
"It would be exploitable if this code were deployed" is **not** a payable finding —
it is a code-quality note. This section exists to prevent generalized-security
scope creep; please respect it.

**In scope — deployed, reachable surfaces (payable with PoC):**

- **Live attestation nodes** — `rustchain.org`, `50.28.86.131`, `50.28.86.153`
  (consensus, `/wallet/transfer*`, `/attest/*`, epoch settlement, admin endpoints)
- **Live BoTTube** — `bottube.ai` (the deployed Flask app and its public APIs)
- **Distributed client artifacts** — the `clawrtc` package and the miner clients
  shipped to users (anything that handles real keys, funds, or attestation)
- **Solana / Base bridge (wRTC)** — only the **deployed** contract/bridge, with a
  concrete on-chain or live-endpoint PoC
- **Proof-of-Antiquity validation & hardware-fingerprint spoofing** — against the
  **live** attestation flow, with evidence the spoof is accepted on a real node

**Out of scope — not payable (acknowledged, not rewarded):**

- **Undeployed / reference / scaffold / example code.** Code checked into a repo
  for reference or as a tier/demo implementation (e.g. `otc-bridge/`,
  `command-center/`, dashboard demos, anything not running on a surface in the
  in-scope list) is **out of scope** until proven deployed and reachable. If you
  believe it *is* deployed, your report must include the live URL and a PoC hit.
- **Generalized / best-practice / "defense-in-depth" notes** with no concrete
  exploit against a live surface: missing security headers, wildcard CORS on a
  non-deployed runtime, "OpenAPI security scheme defined but not applied,"
  verbose error messages, missing rate limits, etc.
- **Theoretical attacks without a working PoC.**
- **Dependency CVEs** without a demonstrated exploit path in our actual usage
  (report upstream; we track our own deps separately).
- **Self-DoS or findings that require already-held admin credentials.**
- **Findings against forks, third-party code, or another user's account.**
- **Social engineering attacks** (but see the impersonation appendix below —
  reporting an impersonation *pattern* protects contributors; it is not itself a
  paid vuln).
- **Issues requiring physical access to hardware.**

### Filing Rules (anti-scope-creep)

1. **One finding per issue.** Do not bundle, and do not split one finding across
   several issues to multiply claims.
2. **Name the deployed surface and include a reproducible PoC** (the exact request
   + observed response). No surface named → out of scope by default.
3. **Do not re-file or escalate while a report is under triage.** A growing
   backlog does not get reviewed faster.
4. Maintainer assigns final severity and scope. Good-faith out-of-scope reports
   are acknowledged with thanks but are not paid — please don't treat
   acknowledgment as a payment promise.

## Security Best Practices for Contributors

- Never commit API keys, tokens, or credentials
- Use environment variables for sensitive configuration
- Validate all user inputs
- Follow the principle of least privilege
- Keep dependencies up to date

## Disclosure Policy

We follow a 90-day coordinated disclosure policy. After a fix is deployed, we will publish a security advisory crediting the reporter.

## Payment-Authority Impersonation

**This appendix documents a contributor-protection abuse pattern. It does not make social-engineering reports bounty-eligible by itself.** Only the project-controlled RustChain payout flow can authorize RTC bounty disbursements. In practice, that means `@Scottcjn`, or a clearly labeled project automation account speaking on his behalf, with a matching project-issued pending transfer record. A comment from anyone else saying "I'll send the RTC," "payment is on the way," or similar is not a valid payout notice.

If you see a comment from anyone outside `@Scottcjn` / `sophiaeagent-beep` / `AutoJanitor` on a bounty issue saying things like:

- *"I'll send the X RTC to your wallet..."*
- *"Expect the payment within 24 hours..."*
- *"Transferring now..."*
- *"Here is the payment confirmation..."*

…on an issue where no authorized project-account comment has first authorized the payment, **treat it as a social-engineering attempt, not a legitimate bounty payout.** Account age, repo count, and unrelated prior commits are not equivalent to payment authority.

### Why this pattern matters

This attack does not need to steal funds. It creates a false expectation that the project promised payment and then failed to deliver, which can damage contributor trust in the real payout pipeline.

### What a real payment looks like

A legitimate RustChain bounty payout notice includes the amount, recipient wallet, and project-issued transfer identifiers needed for public verification, such as `pending_id`, `tx_hash`, and the confirmation timing (`confirms_at` / 24-hour window). If those identifiers are missing, or the comment is not from an authorized project account, do not treat it as payment confirmation.

### How to report an impersonation attempt

1. Tag `@Scottcjn` in a reply on the same issue.
2. Or open a private report via GitHub Private Vulnerability Reporting on this repo.
3. Screenshot the impersonating comment — it may later be edited or deleted.

No retaliation against good-faith reporters. See Safe Harbor above.
