# GitHub Actions CI/CD Workflow

Automated CI/CD pipeline for RustChain projects.

## Features

- **Multi-version testing** - Node.js 18/20, Python 3.9/3.10/3.11
- **Automated testing** - Run on every push and PR
- **Code coverage** - Upload to Codecov
- **Auto deployment** - Deploy on main branch merge

## Files

- `.github/workflows/ci.yml` - CI/CD workflow configuration

## Usage

The workflow runs automatically on:
- Push to `main` or `develop` branches
- Pull requests to `main` branch

---

Fixes #1591
