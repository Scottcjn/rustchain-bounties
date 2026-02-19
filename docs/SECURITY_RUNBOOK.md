# Security Report Handling Runbook

Quick reference for maintainers handling security vulnerability reports.

## Initial Response Checklist

- [ ] Acknowledge report within 48 hours
- [ ] Assign severity level (Critical/High/Medium/Low)
- [ ] Create GitHub Security Advisory
- [ ] Add relevant maintainers to advisory

## Severity Assessment (RTC Payout Ranges)

### Critical (2000+ RTC)
- Remote code execution
- Consensus attacks
- Fund theft or unauthorized transfers
- Signature forgery
- **Response:** 24-48 hours

### High (800-2000 RTC)
- API authentication bypass
- Data exfiltration
- Service disruption
- **Response:** 3-5 days

### Medium (300-800 RTC)
- Information disclosure
- Cross-site scripting (XSS)
- CSRF vulnerabilities
- **Response:** 7-14 days

### Low (50-300 RTC)
- Minor information leaks
- Cosmetic issues
- Theoretical vulnerabilities
- **Response:** 14-30 days

## Processing Timeline

| Phase | Target | Actions |
|-------|--------|---------|
| Acknowledge | 48 hours | Confirm receipt, assign severity |
| Triage | 7 days | Reproduce, assess impact, plan response |
| Fix | 30-45 days | Develop and test mitigation |
| Disclosure | 90 days | Publish advisory, process bounty |

## Communication Templates

### Acknowledgment Email
```
Subject: Security Report Received - [Report ID]

Thank you for your security report. We have received your submission and are actively reviewing it.

Report ID: [GitHub Advisory ID]
Severity: [Pending/Assigned]
Next Update: Within 7 business days

If you have additional information, please add it to the advisory.
```

### Bounty Notification
```
Subject: Security Bounty Approved - [Amount] RTC

Your security report has been validated and approved for a bounty.

Amount: [X] RTC
Severity: [Level]
Wallet: [To be confirmed]

The payout will be processed within 30 days of this notification.
```

## Escalation Path

1. **Daily Maintainer Check:** Review new security advisories
2. **Weekly Triage Meeting:** Review all open security issues
3. **Critical Issues:** Immediate notification to all maintainers
4. **BoTTube Cross-Report:** Notify BoTTube team if cross-repo impact

## Notes

- Never disclose vulnerability details publicly before coordinated disclosure
- Keep all communication through GitHub Security Advisories when possible
- Document all decisions in the advisory comments
- Process bounties through the standard payout pipeline
