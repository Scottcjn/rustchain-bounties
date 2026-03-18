# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest | :x:               |

## Security Hardening Measures

### Block Explorer Security

#### Input Validation & Sanitization
- **XSS Prevention**: All user inputs and blockchain data are sanitized before rendering
- **SQL Injection Protection**: Parameterized queries and input validation on all database operations
- **Hash Validation**: Block hashes, transaction IDs, and addresses are validated against expected formats
- **Rate Limiting**: API endpoints implement rate limiting (100 requests/minute per IP)
- **Input Length Limits**: Maximum payload sizes enforced (1MB for API requests)

#### Authentication & Authorization
- **API Key Management**: Secure API key generation with configurable expiration
- **Role-Based Access Control**: Admin/read-only user roles with granular permissions
- **Session Security**: HTTP-only, secure cookies with CSRF protection
- **JWT Token Security**: Signed tokens with short expiration times (15 minutes)

#### Network Security
- **HTTPS Enforcement**: TLS 1.3 minimum, HSTS headers enabled
- **CORS Policy**: Restrictive CORS configuration for cross-origin requests
- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options implemented
- **Reverse Proxy**: Nginx/Apache configuration with security modules enabled

#### Data Protection
- **Database Security**: Encrypted connections, least privilege access
- **Sensitive Data Handling**: No private keys stored, masked sensitive information
- **Backup Encryption**: All backups encrypted at rest and in transit
- **Log Sanitization**: Personal data filtered from application logs

#### Infrastructure Hardening
- **Container Security**: Minimal base images, non-root user execution
- **Network Segmentation**: Isolated networks for different service tiers
- **Firewall Rules**: Restrictive ingress/egress rules, DDoS protection
- **Monitoring**: Real-time security event monitoring and alerting

### Dashboard Security

#### Frontend Security
- **Content Security Policy**: Strict CSP preventing script injection
- **Subresource Integrity**: SRI hashes for all external resources
- **DOM Sanitization**: Safe HTML rendering with sanitization libraries
- **Secure Storage**: Sensitive data encrypted in localStorage/sessionStorage

#### API Security
- **OAuth 2.0**: Secure authentication flow with PKCE
- **Request Signing**: HMAC-based request authentication
- **Replay Attack Prevention**: Nonce and timestamp validation
- **Data Minimization**: Only necessary data exposed in API responses

## Security Testing Guidelines

### Automated Security Testing

#### Static Analysis (SAST)
```bash
# Run security linting
cargo clippy -- -W clippy::all
cargo audit

# Frontend security scan
npm audit
eslint --ext .js,.jsx src/ --rule 'security/*: error'
```

#### Dynamic Analysis (DAST)
```bash
# OWASP ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:3000

# SQL injection testing
sqlmap -u "http://localhost:8080/api/block/*" --batch --level=5

# XSS testing
xssstrike -u http://localhost:3000/search --crawl
```

#### Dependency Scanning
```bash
# Rust dependencies
cargo audit --deny warnings

# Node.js dependencies
npm audit --audit-level high
snyk test
```

### Manual Security Testing

#### Authentication Testing
1. **Session Management**
   - Test session timeout and renewal
   - Verify secure cookie attributes
   - Test concurrent session limits

2. **Authorization Bypass**
   - Test privilege escalation attempts
   - Verify role-based access controls
   - Test API endpoint authorization

#### Input Validation Testing
1. **Injection Attacks**
   - SQL injection on search parameters
   - NoSQL injection on JSON inputs
   - Command injection on system calls

2. **Cross-Site Scripting (XSS)**
   - Reflected XSS in search results
   - Stored XSS in user-generated content
   - DOM-based XSS in client-side scripts

3. **Cross-Site Request Forgery (CSRF)**
   - Test state-changing operations
   - Verify CSRF token implementation
   - Test SameSite cookie attributes

#### API Security Testing
1. **Rate Limiting**
   - Test API rate limit enforcement
   - Verify rate limit bypass attempts
   - Test distributed rate limiting

2. **Data Exposure**
   - Test for sensitive data leaks
   - Verify proper error handling
   - Test information disclosure

### Security Testing Checklist

#### Pre-Deployment Checklist
- [ ] All dependencies updated to latest secure versions
- [ ] Security headers properly configured
- [ ] TLS/SSL configuration validated (A+ rating)
- [ ] Input validation implemented on all endpoints
- [ ] Rate limiting configured and tested
- [ ] Authentication mechanisms thoroughly tested
- [ ] Error handling doesn't expose sensitive information
- [ ] Logging configured without sensitive data
- [ ] Security policies documented and reviewed

#### Penetration Testing
- [ ] Network security assessment
- [ ] Web application security testing
- [ ] API security evaluation
- [ ] Infrastructure security review
- [ ] Social engineering resistance testing

#### Compliance Verification
- [ ] OWASP Top 10 mitigation verified
- [ ] Data protection regulations compliance
- [ ] Security monitoring and alerting active
- [ ] Incident response procedures tested
- [ ] Security training completed for team

### Security Tools Integration

#### CI/CD Pipeline Security
```yaml
# Example GitHub Actions security workflow
security_checks:
  runs-on: ubuntu-latest
  steps:
    - name: Cargo Audit
      run: cargo audit --deny warnings
    - name: Semgrep SAST
      run: semgrep --config=auto src/
    - name: Docker Security Scan
      run: docker scout cves --only-severity critical,high
```

#### Monitoring & Alerting
- **WAF Integration**: Web Application Firewall with custom rules
- **SIEM Integration**: Security event correlation and analysis
- **Vulnerability Scanning**: Automated daily security scans
- **Threat Intelligence**: Integration with threat feeds and indicators

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
- Security testing evidence (logs, screenshots)
- Affected versions and components

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

### Additional Bounty Categories

| Category | Description | Reward Range |
| -------- | ----------- | ------------ |
| Block Explorer Hardening | XSS, injection, auth bypass | 75-100 RTC |
| API Security | Rate limiting bypass, data exposure | 50-75 RTC |
| Infrastructure Security | Container escape, network issues | 25-50 RTC |
| Security Documentation | Testing guides, best practices | 5-25 RTC |