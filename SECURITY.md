# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| latest  | :white_check_mark: |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue:

1. **Do not** open a public GitHub issue.
2. Email the maintainers or use GitHub's private vulnerability reporting feature.
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will acknowledge your report within 48 hours and provide a resolution timeline within 7 days.

## Automated Dependency Updates

This project uses [Dependabot](https://docs.github.com/en/code-security/dependabot) to automatically check for dependency updates and security patches. Dependabot will:

- Check for outdated dependencies weekly
- Automatically create pull requests for updates
- Flag known security vulnerabilities

## Security Best Practices

- Keep dependencies up to date
- Review Dependabot PRs promptly
- Never commit secrets or credentials
- Use environment variables for sensitive configuration
