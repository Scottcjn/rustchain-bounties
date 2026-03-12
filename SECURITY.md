# RustChain Security Policy

## 🛡️ Security Commitment

The RustChain team takes security vulnerabilities seriously. We are committed to protecting the integrity of our consensus mechanism, user funds, and ecosystem. This document outlines our security policies, vulnerability reporting procedures, and our commitment to responsible disclosure.

---

## 📋 Table of Contents

1. [Supported Versions](#supported-versions)
2. [Reporting a Vulnerability](#reporting-a-vulnerability)
3. [Vulnerability Response Process](#vulnerability-response-process)
4. [Bounty Rewards](#bounty-rewards)
5. [Scope](#scope)
6. [Security Best Practices](#security-best-practices)
7. [Disclosure Policy](#disclosure-policy)
8. [Security Updates](#security-updates)
9. [Contact & Support](#contact--support)

---

## ✅ Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest | :x:               |

**Note:** We only provide security patches for the latest version. Please ensure you are running the most recent release.

---

## 🚨 Reporting a Vulnerability

We appreciate your help in keeping RustChain secure. If you discover a security vulnerability, please follow our responsible disclosure process:

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Use GitHub's [Private Vulnerability Reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) feature
3. Alternatively, contact maintainers directly via:
   - **Discord**: DM a maintainer in our [official server](https://discord.gg/VqVVS2CW9Q)
   - **Email**: security@rustchain.org (if available)

### What to Include

To help us assess and respond quickly, please provide:

- **Description**: Clear description of the vulnerability
- **Reproduction Steps**: Detailed steps to reproduce the issue
- **Impact Assessment**: Your assessment of potential impact
- **Proof of Concept**: Code, screenshots, or video demonstrating the issue (if possible)
- **Suggested Fix**: Any recommendations for remediation (optional)
- **Contact Info**: Your preferred contact method for follow-up

### What NOT to Do

- ❌ Do not exploit the vulnerability beyond what is necessary to demonstrate it
- ❌ Do not disclose the vulnerability publicly before we have had time to respond
- ❌ Do not access or modify other users' data
- ❌ Do not disrupt network operations or cause denial of service

---

## ⚡ Vulnerability Response Process

We follow a structured response process:

| Stage | Timeline | Action |
|-------|----------|--------|
| **Acknowledgment** | Within 48 hours | We confirm receipt of your report |
| **Initial Assessment** | Within 1 week | We evaluate severity and scope |
| **Fix Development** | 2-4 weeks | We develop and test a patch |
| **Coordinated Disclosure** | After fix deployment | We publish advisory and credit you |

### Communication

- You will receive acknowledgment within **48 hours**
- We will provide regular updates on fix progress
- You may request to remain anonymous in public disclosures

---

## 💰 Bounty Rewards

Security contributions are eligible for **RTC token rewards** through our bounty program:

| Severity | Description | Reward (RTC) |
|----------|-------------|--------------|
| **Critical** | Consensus bypass, fund theft, critical cryptographic weakness | 100-150 RTC |
| **High** | Data leak, authentication bypass, significant logic error | 75-100 RTC |
| **Medium** | DoS vector, information disclosure, moderate impact | 20-50 RTC |
| **Low** | Best practice violations, minor information leaks | 1-10 RTC |

### Bounty Eligibility

- Vulnerability must be previously unreported
- Report must follow responsible disclosure guidelines
- Fix must be implemented based on your report
- Duplicate reports: first reporter receives bounty

### Claim Process

1. Submit vulnerability report
2. Wait for validation and fix deployment
3. Submit bounty claim via GitHub Issue
4. Receive RTC tokens after approval

---

## 🎯 Scope

### In Scope

The following are **in scope** for security reports and bounty rewards:

- ✅ Consensus mechanism vulnerabilities
- ✅ Proof-of-Antiquity validation bypasses
- ✅ Hardware fingerprinting spoofing
- ✅ Solana bridge (wRTC) smart contract issues
- ✅ API authentication/authorization flaws
- ✅ Denial of service vectors
- ✅ Cryptographic implementation weaknesses
- ✅ Private key handling and storage
- ✅ Transaction validation logic
- ✅ Peer-to-peer network security

### Out of Scope

The following are **out of scope**:

- ❌ Social engineering attacks
- ❌ Issues in third-party dependencies (report upstream)
- ❌ Issues requiring physical hardware access
- ❌ Theoretical attacks without practical PoC
- ❌ Vulnerabilities in deprecated versions
- ❌ Issues already known to the team
- ❌ Spam, phishing, or social engineering vectors

---

## 🔒 Security Best Practices

### For Contributors

- **Never commit** API keys, tokens, or credentials
- **Use environment variables** for sensitive configuration
- **Validate all user inputs** on both client and server
- **Follow least privilege** principle in code design
- **Keep dependencies updated** and audit regularly
- **Use secure random** number generators for cryptographic operations
- **Implement rate limiting** on public endpoints

### For Node Operators

- Keep your node software updated
- Use firewall rules to restrict access
- Monitor logs for suspicious activity
- Backup private keys securely (offline storage)
- Use dedicated hardware for node operations

### For Miners

- Never share your miner credentials
- Use secure connections (HTTPS/WSS)
- Regularly rotate API keys
- Monitor hashrate for anomalies
- Report suspicious pool behavior

---

## 📢 Disclosure Policy

We follow a **90-day coordinated disclosure** policy:

1. **Private Report**: You report vulnerability privately
2. **Fix Development**: We develop and test a patch
3. **Deployment**: Fix is deployed to production
4. **Public Advisory**: After 90 days or fix deployment (whichever is later), we publish a security advisory
5. **Credit**: You receive credit in the advisory (unless anonymous)

### Embargo Policy

- Security information is under embargo until public advisory
- Embargo exceptions: legal requirements, active exploitation
- Violation of embargo may disqualify from bounty rewards

---

## 🔄 Security Updates

### How We Communicate

- **GitHub Security Advisories**: Official vulnerability disclosures
- **Release Notes**: Security fixes mentioned in changelog
- **Discord Announcements**: Urgent security notifications
- **Twitter/X**: Public announcements for critical issues

### Staying Updated

- ⭐ Star the repository for release notifications
- 🔔 Watch the repository for security advisories
- 💬 Join our Discord for real-time updates
- 📧 Subscribe to our security mailing list (if available)

---

## 📞 Contact & Support

### Security Team

- **GitHub**: Use Private Vulnerability Reporting
- **Discord**: [Official Server](https://discord.gg/VqVVS2CW9Q)
- **Twitter**: [@RustChain](https://twitter.com/RustChain) (for public inquiries)

### General Security Questions

For non-vulnerability security questions:
- Open a regular GitHub Discussion
- Ask in Discord #security channel
- Check existing security documentation in `/docs`

---

## 📜 Legal Notice

This security policy does not constitute a legal agreement. The RustChain team reserves the right to:
- Modify this policy at any time
- Decline bounty rewards for violations of this policy
- Take legal action against malicious actors

By reporting a vulnerability, you agree to:
- Follow responsible disclosure guidelines
- Not exploit vulnerabilities for personal gain
- Cooperate with the security team during investigation

---

## 🙏 Acknowledgments

We thank all security researchers who help keep RustChain secure. Your contributions are invaluable to our ecosystem's safety.

**Hall of Fame** (security contributors who chose to be named):
- _Your name here!_

---

*Last updated: March 12, 2026*
*Policy version: 2.0*
