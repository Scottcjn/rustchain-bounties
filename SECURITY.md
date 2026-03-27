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

We follow a 90-day coordinated disclosure policy. After a fix is deployed, we will publish a security advisory crediting the reporter.
