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


## Security Contact

Preferred channel:

- GitHub Private Vulnerability Reporting (Security Advisories in this repository)

Alternative channel:

- security@elyanlabs.com (include repo, reproduction steps, impact, and proof)

PGP can be shared on request for encrypted disclosure.

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
- Optional wrapped rails (for example wRTC/eRTC) may be supported as operational bridges, but no redemption or cash-out guarantee is provided.
- Participation in this open-source program is not an investment contract and does not create ownership rights.
- Funding/utility position reference: `docs/UTILITY_COIN_POSITION.md`
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


## Payout Timing and Confirmation

- RTC payouts are queued with a public `pending_id` and `tx_hash` before confirmation.
- Standard pending window is 24h unless a bounty explicitly states otherwise.
- Maintainers may void a pending payout with public reason if duplicate/fraud evidence appears.
- Confirmed payouts are publicly auditable in the ledger issue.


