# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest | :x:               |

## Reporting a Vulnerability

We take security seriously at Rustchain. If you discover a security vulnerability, please follow responsible disclosure:

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Email your findings to the repository maintainers via GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
3. Alternatively, reach out on [Discord](https://discord.gg/VqVVS2CW9Q) via DM to a maintainer

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

Security-related contributions are eligible for RTC token rewards:

| Severity | Reward |
| -------- | ------ |
| Critical (consensus, funds at risk) | 100-150 RTC |
| High (data leak, auth bypass) | 75-100 RTC |
| Medium (DoS, logic error) | 20-50 RTC |
| Low (info disclosure, best practice) | 1-10 RTC |

### Scope

The following are in scope for security reports:

- Consensus mechanism vulnerabilities
- Proof-of-Antiquity validation bypasses
- Hardware fingerprinting spoofing
- Solana bridge (wRTC) contract issues
- API authentication/authorization flaws
- Denial of service vectors
- Cryptographic weaknesses

### Out of Scope

- Social engineering attacks
- Issues in dependencies (report upstream)
- Issues requiring physical access to hardware
- Theoretical attacks without proof of concept

## Security Best Practices for Contributors

- Never commit API keys, tokens, or credentials
- Use environment variables for sensitive configuration
- Validate all user inputs
- Follow the principle of least privilege
- Keep dependencies up to date

## Disclosure Policy

<<<<<<< HEAD
We follow a 90-day coordinated disclosure policy. After a fix is deployed, we will publish a security advisory crediting the reporter.
=======


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
>>>>>>> 7a8dbb2 (docs(security): add Payment-Authority Impersonation appendix)
