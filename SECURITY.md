# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.8.x   | :white_check_mark: |
| < 0.8   | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue:

1. **Do NOT** open a public GitHub issue
2. Email the maintainers or use GitHub's private vulnerability reporting
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Security Considerations

- RustChain uses self-signed TLS certificates for node communication
- All API endpoints should use HTTPS
- Wallet private keys should never be shared or committed
- Bridge operations require additional verification

## Known Security Advisories

See [SECURITY.md](./SECURITY.md) for the latest advisories.
