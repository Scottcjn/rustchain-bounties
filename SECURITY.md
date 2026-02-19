# Security Policy

Last updated: 2026-02-19

RustChain and related open-source projects welcome good-faith security research.

## Safe Harbor

If you act in good faith and follow this policy, Elyan Labs maintainers will not pursue legal action related to your research activities.

Good-faith means:

- avoid privacy violations, data destruction, and service disruption
- do not access, alter, or exfiltrate non-public user data
- do not move funds you do not own
- do not use social engineering, phishing, or physical attacks
- report vulnerabilities responsibly and give maintainers time to fix

## Authorization Statement

Testing conducted in accordance with this policy is authorized by project maintainers.
We will not assert anti-hacking claims for good-faith research that follows these rules.

## How to Report

Preferred:

- GitHub Private Vulnerability Reporting (Security Advisories)

Alternative:

- Open a private disclosure request via maintainer contact listed in repository profile

Please include:

- affected repository/component
- clear reproduction steps
- impact assessment
- suggested mitigation if available

## Scope

In scope:

- RustChain consensus, attestation, reward, and transfer logic
- pending transfer / confirmation / void flows
- bridge and payout automation code
- API authentication, authorization, and rate-limit controls
- Beacon integration and signature verification paths

Out of scope:

- social engineering
- physical attacks
- denial-of-service against production infrastructure
- reports without reproducible evidence

## Response Targets

- acknowledgment: within 48 hours
- initial triage: within 5 business days
- fix/mitigation plan: within 30-45 days
- coordinated public disclosure target: up to 90 days

## Bounty Guidance (RTC)

Bounty rewards are discretionary and severity-based.

- Critical: 2000+ RTC
- High: 800-2000 RTC
- Medium: 300-800 RTC
- Low: 50-300 RTC

Bonuses may be granted for clear reproducibility, exploit reliability, and patch-quality remediation.

## Token Value and Compensation Disclaimer

- Bounty payouts are offered in project-native tokens unless explicitly stated otherwise.
- No token price, market value, liquidity, convertibility, or future appreciation is guaranteed.
- Participation in this open-source program is not an investment contract and does not create ownership rights.
- Rewards are recognition for accepted security work: respect earned through contribution.

## Prohibited Conduct

Reports are ineligible for reward if they involve:

- extortion or disclosure threats
- automated spam submissions
- duplicate reports without new technical substance
- exploitation beyond what is required to prove impact

## Recognition

Valid reports may receive:

- RTC bounty payout
- optional Hall of Hunters recognition
- follow-on hardening bounty invitations

## Maintainer Runbook

### Handling Security Reports

#### Step 1: Triage (Within 48 Hours)
1. Acknowledge receipt of the report
2. Assign a severity level using the rubric above
3. Create a private Security Advisory in GitHub
4. Add relevant maintainers as collaborators

#### Step 2: Assessment (Within 7 Days)
1. Reproduce the vulnerability if possible
2. Determine attack surface and impact
3. Identify affected versions/components
4. Check for similar past vulnerabilities

#### Step 3: Response Planning
1. Develop mitigation strategy
2. Determine disclosure timeline
3. Prepare communication (if public disclosure needed)
4. Set expectation with reporter

#### Step 4: Fix & Verification
1. Develop fix in private branch
2. Test fix thoroughly
3. Prepare release notes (without details)
4. Merge fix to main

#### Step 5: Disclosure
1. Publish security advisory
2. Issue CVE if applicable
3. Notify affected users
4. Process bounty payout
5. Add reporter to Hall of Hunters if applicable

### Severity Rubric Quick Reference

| Severity | Impact | Examples | Response Time |
|----------|--------|----------|---------------|
| Critical | Remote code execution, consensus failure, fund theft | Payout bug, signature forgery, validator bypass | 24-48 hours |
| High | Significant data loss or service disruption | API auth bypass, data exfiltration | 3-5 days |
| Medium | Limited impact, requires specific conditions | Information disclosure, CSRF | 7-14 days |
| Low | Minimal impact, theoretical only | Minor info leak, cosmetic issues | 14-30 days |

### Contact

- **Security Issues:** Use GitHub Security Advisories
- **General Inquiries:** Create issue with [security] tag
- **Emergency:** Email maintainers directly (see repo profile)
