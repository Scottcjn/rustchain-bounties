# RustChain Security Best Practices Guide

> **Comprehensive security guide for miners, wallet users, and node operators**
> 
> **Reward:** 3 RTC (Issue #1642)

---

## Table of Contents

1. [Introduction](#introduction)
2. [Miner Security](#miner-security)
3. [Wallet Security](#wallet-security)
4. [Node Operator Security](#node-operator-security)
5. [API & Application Security](#api--application-security)
6. [Operational Security](#operational-security)
7. [Incident Response](#incident-response)
8. [Security Checklist](#security-checklist)

---

## Introduction

This guide provides comprehensive security best practices for participating in the RustChain ecosystem. Whether you're running a miner, managing wallets, or operating nodes, following these practices will help protect your assets and contribute to network security.

### Security Principles

- **Defense in Depth**: Multiple layers of security controls
- **Least Privilege**: Grant only necessary permissions
- **Zero Trust**: Verify explicitly, never trust implicitly
- **Fail Secure**: Default to secure states on errors

---

## Miner Security

### Hardware Security

#### Physical Security
- **Secure Location**: Keep mining hardware in a locked, access-controlled environment
- **Environmental Controls**: Maintain proper temperature (15-25°C) and humidity (40-60%)
- **Power Protection**: Use UPS (Uninterruptible Power Supply) to prevent data corruption
- **Network Isolation**: Consider VLAN segregation for mining equipment

#### Hardware Integrity
```bash
# Verify hardware fingerprint hasn't been tampered
rustchain-miner verify-fingerprint --device /dev/miner0

# Check for unauthorized firmware modifications
rustchain-miner firmware-check --verbose
```

### Software Security

#### System Hardening
```bash
# Update system packages regularly
sudo apt update && sudo apt upgrade -y

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable cups

# Configure firewall (Linux)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.1.0/24 to any port 22  # SSH from LAN only
sudo ufw enable
```

#### Miner Configuration Security
```toml
# rustchain.toml - Secure Configuration Example

[security]
# Never hardcode credentials - use environment variables
api_key = "${RUSTCHAIN_API_KEY}"
wallet_id = "${RUSTCHAIN_WALLET_ID}"

# Enable TLS for all connections
require_tls = true
verify_certificates = true

# Rate limiting to prevent abuse
max_requests_per_minute = 60

[logging]
# Log security events but redact sensitive data
level = "info"
redact_credentials = true
audit_log_path = "/var/log/rustchain/audit.log"
```

#### Access Control
```bash
# Create dedicated user for miner process
sudo useradd -r -s /bin/false rustchain-miner

# Set restrictive file permissions
sudo chown -R rustchain-miner:rustchain-miner /opt/rustchain
sudo chmod 750 /opt/rustchain
sudo chmod 640 /opt/rustchain/config/*.toml
```

### Network Security

#### Firewall Rules
```bash
# Essential ports only
# SSH (22) - Restrict to management network
# Miner API (8545) - Localhost only
# RustChain P2P (30333) - As needed

# Example iptables rules
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p tcp --dport 8545 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 30333 -j ACCEPT
iptables -A INPUT -j DROP
```

#### TLS/SSL Configuration
```toml
[tls]
enabled = true
cert_path = "/etc/ssl/certs/rustchain.crt"
key_path = "/etc/ssl/private/rustchain.key"
min_version = "TLS1.2"
cipher_suites = [
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
]
```

### Monitoring & Alerting

```bash
# Monitor miner health
rustchain-miner health-check --interval 60

# Set up alerts for anomalies
# - Hash rate drops > 20%
# - Temperature > 80°C
# - Unauthorized access attempts
# - Configuration changes
```

---

## Wallet Security

### Wallet Types & Use Cases

| Wallet Type | Security Level | Best For | Risk |
|-------------|---------------|----------|------|
| Hardware Wallet | ⭐⭐⭐⭐⭐ | Long-term storage, large amounts | Physical loss |
| Desktop Wallet | ⭐⭐⭐ | Daily operations, medium amounts | Malware, OS compromise |
| Mobile Wallet | ⭐⭐ | Small amounts, payments | Device loss, apps |
| Web Wallet | ⭐ | Testing, minimal funds | Phishing, server breach |

### Private Key Management

#### Golden Rules
1. **NEVER** share your private key or seed phrase
2. **NEVER** store keys in plain text
3. **NEVER** commit keys to version control
4. **ALWAYS** use encrypted storage
5. **ALWAYS** backup securely (offline, multiple locations)

#### Secure Storage Methods

**Hardware Wallet (Recommended)**
```bash
# Using Ledger or Trezor
# Keys never leave the device
# Transactions signed on-device

rustchain-wallet connect --hardware ledger
rustchain-wallet sign --tx transaction.json --hardware
```

**Encrypted Software Wallet**
```bash
# Create encrypted wallet
rustchain-wallet create --encrypted --cipher aes-256-gcm

# Set strong passphrase (minimum 16 characters)
# Use combination of: uppercase, lowercase, numbers, symbols

# Backup encrypted wallet file
cp ~/.rustchain/wallet.dat /secure/backup/location/
```

### Multi-Signature Wallets

For enhanced security, use multi-sig wallets for significant amounts:

```toml
# Multi-sig configuration (2-of-3 example)
[multisig]
type = "2-of-3"
signers = [
    "0x1234...abcd",  # Primary key (desktop)
    "0x5678...efgh",  # Backup key (hardware wallet)
    "0x9abc...ijkl"   # Recovery key (offline storage)
]
threshold = 2
```

### Transaction Security

#### Before Sending
```bash
# Verify recipient address
rustchain-wallet verify-address 0xRecipient...

# Check transaction details
rustchain-wallet decode-tx transaction.json

# Use address whitelist for frequent recipients
rustchain-wallet whitelist add 0xTrusted... --label "Exchange"
```

#### Safe Transaction Practices
- Double-check recipient addresses (first 4 and last 4 characters)
- Start with small test transactions for new addresses
- Enable transaction notifications
- Set daily withdrawal limits
- Use time-locks for large transfers

### Backup & Recovery

#### Backup Strategy (3-2-1 Rule)
- **3** copies of your wallet backup
- **2** different storage media (USB drive + paper)
- **1** copy stored offsite (safe deposit box, trusted family)

#### Backup Commands
```bash
# Create encrypted backup
rustchain-wallet backup --output backup.enc --encrypt

# Verify backup integrity
rustchain-wallet verify-backup backup.enc

# Test recovery (on separate device)
rustchain-wallet restore --from backup.enc
```

---

## Node Operator Security

### System Requirements & Hardening

#### OS Security Baseline
```bash
# Use LTS versions only (Ubuntu 22.04 LTS, RHEL 9)
# Enable automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades

# Kernel hardening parameters
cat >> /etc/sysctl.d/99-rustchain.conf << EOF
net.ipv4.tcp_syncookies = 1
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
kernel.kptr_restrict = 2
kernel.dmesg_restrict = 1
EOF

sysctl --system
```

#### Container Security (Docker)
```yaml
# docker-compose.yml - Secure Configuration
version: '3.8'
services:
  rustchain-node:
    image: rustchain/node:latest
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    user: "1000:1000"
    volumes:
      - ./data:/data:ro
      - ./config:/config:ro
    networks:
      - rustchain-internal

networks:
  rustchain-internal:
    driver: bridge
    internal: true
```

### Consensus Security

#### Validator Key Protection
```bash
# Store validator keys in HSM or hardware wallet
rustchain-validator init --hsm --device /dev/hsm0

# Never expose validator keys to network
# Use separate signing machine (air-gapped if possible)

# Rotate keys periodically
rustchain-validator rotate-keys --interval 90d
```

#### Slashing Prevention
- Monitor node uptime (maintain > 99%)
- Set up redundant nodes in different locations
- Configure alerting for missed attestations
- Keep adequate collateral buffer

### Network Security

#### DDoS Protection
```bash
# Rate limiting with nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;

server {
    location /api/ {
        limit_req zone=one burst=20 nodelay;
        proxy_pass http://rustchain-node:8545;
    }
}

# Connection limits
iptables -A INPUT -p tcp --syn -m connlimit --connlimit-above 20 -j DROP
```

#### Peer Management
```toml
[network]
# Trusted peers only (optional, for private networks)
trusted_peers = [
    "/ip4/192.168.1.100/tcp/30333",
    "/ip4/192.168.1.101/tcp/30333"
]

# Maximum peer connections
max_peers = 50

# Ban misbehaving peers automatically
ban_misbehaving = true
ban_duration = "24h"
```

---

## API & Application Security

### Authentication

#### API Key Management
```bash
# Generate strong API key
rustchain-api key generate --bits 256

# Rotate keys every 90 days
rustchain-api key rotate --current KEY_ID --expires-in 90d

# Revoke compromised keys immediately
rustchain-api key revoke KEY_ID --reason "suspected_compromise"
```

#### OAuth 2.0 Implementation
```toml
[oauth]
client_id = "${OAUTH_CLIENT_ID}"
client_secret = "${OAUTH_CLIENT_SECRET}"
redirect_uri = "https://yourapp.com/callback"
scope = "read write"
pkce_required = true
```

### Input Validation

```python
# Example: Validate wallet address
import re

def validate_wallet_address(address: str) -> bool:
    """Validate RustChain wallet address format"""
    pattern = r'^0x[a-fA-F0-9]{40}$'
    if not re.match(pattern, address):
        return False
    
    # Additional checksum validation
    return rustchain.verify_checksum(address)

# Sanitize all user inputs
from html import escape

def sanitize_input(user_input: str) -> str:
    """Prevent XSS and injection attacks"""
    return escape(user_input.strip())
```

### Rate Limiting

```python
# Implement rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)

@app.route("/api/transfer", methods=["POST"])
@limiter.limit("5 per minute")
def transfer():
    # Transfer logic
    pass
```

### Logging & Monitoring

```toml
[logging]
# Structured logging for security events
format = "json"
level = "info"

# Redact sensitive fields
redact_fields = [
    "api_key",
    "private_key",
    "password",
    "token",
    "authorization"
]

# Security event categories
security_events = [
    "authentication_failure",
    "authorization_denied",
    "configuration_change",
    "key_rotation",
    "suspicious_activity"
]
```

---

## Operational Security

### Credential Management

#### Environment Variables
```bash
# .env file (NEVER commit to git)
RUSTCHAIN_API_KEY="your-api-key-here"
RUSTCHAIN_WALLET_ID="your-wallet-id"
DATABASE_URL="postgresql://user:pass@localhost/db"

# Load securely
set -a
source .env
set +a

# Or use secrets manager
aws secretsmanager get-secret-value --secret-id rustchain/credentials
```

#### Password Policy
- Minimum 16 characters
- Mix of uppercase, lowercase, numbers, symbols
- No dictionary words or personal information
- Unique password for each service
- Use password manager (1Password, Bitwarden, KeePass)

### Secure Development

#### Code Review Checklist
- [ ] No hardcoded credentials
- [ ] Input validation on all user inputs
- [ ] Output encoding to prevent XSS
- [ ] Parameterized queries (no SQL injection)
- [ ] Proper error handling (no stack traces)
- [ ] TLS for all network communications
- [ ] Authentication on all endpoints
- [ ] Authorization checks on sensitive operations

#### Dependency Management
```bash
# Regularly scan for vulnerabilities
npm audit
cargo audit
pip-audit

# Auto-update dependencies
dependabot:
  schedule:
    interval: daily
  open-pull-requests-limit: 10
```

### Data Protection

#### Encryption at Rest
```bash
# Encrypt sensitive data files
openssl enc -aes-256-cbc -salt -in wallet.dat -out wallet.dat.enc

# Use encrypted filesystems
# Linux: LUKS
# macOS: FileVault
# Windows: BitLocker
```

#### Encryption in Transit
```toml
[tls]
# Always use TLS 1.2 or higher
min_version = "TLS1.2"
prefer_server_ciphers = true

# Certificate validation
verify_mode = "required"
ca_certs = "/etc/ssl/certs/ca-certificates.crt"
```

---

## Incident Response

### Security Incident Classification

| Severity | Description | Response Time |
|----------|-------------|---------------|
| Critical | Funds at risk, consensus attack | Immediate (< 15 min) |
| High | Data breach, auth bypass | < 1 hour |
| Medium | Suspicious activity, policy violation | < 4 hours |
| Low | Best practice violations, minor issues | < 24 hours |

### Incident Response Plan

#### 1. Detection & Analysis
```bash
# Monitor for indicators of compromise
rustchain-security scan --full --output report.json

# Check for unauthorized access
grep "FAILED" /var/log/auth.log | tail -100

# Verify file integrity
rustchain-security verify-checksums
```

#### 2. Containment
- Isolate affected systems
- Revoke compromised credentials
- Block suspicious IP addresses
- Preserve evidence for analysis

#### 3. Eradication
- Remove malware or backdoors
- Patch vulnerabilities
- Reset all credentials
- Update security controls

#### 4. Recovery
- Restore from clean backups
- Verify system integrity
- Monitor closely for re-infection
- Gradually restore services

#### 5. Lessons Learned
- Document incident timeline
- Identify root cause
- Update security policies
- Implement preventive measures

### Contact Information

- **Security Team**: Use GitHub private vulnerability reporting
- **Discord**: DM to maintainers
- **Emergency**: For critical issues, tag @Scottcjn with [CRITICAL] prefix

---

## Security Checklist

### Daily Checks
- [ ] Review security logs for anomalies
- [ ] Verify miner/node health
- [ ] Check for unauthorized access attempts
- [ ] Monitor wallet balances

### Weekly Checks
- [ ] Review and rotate API keys if needed
- [ ] Update system packages
- [ ] Verify backup integrity
- [ ] Check firewall rules

### Monthly Checks
- [ ] Full security audit
- [ ] Review access permissions
- [ ] Test incident response procedures
- [ ] Update dependency versions

### Quarterly Checks
- [ ] Rotate all credentials
- [ ] Review and update security policies
- [ ] Conduct penetration testing
- [ ] Security training refresher

---

## Additional Resources

- [RustChain Documentation](https://docs.rustchain.io)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-12 | Security Team | Initial release |

---

## License

This guide is licensed under the same terms as the RustChain project.

**Contributing**: Submit improvements via PR to rustchain-bounties repository.
