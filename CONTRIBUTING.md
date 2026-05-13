# Contributing to RustChain Bounties

Thank you for your interest in contributing to the RustChain Bounties repository! This document provides guidelines for setting up your development environment, submitting pull requests, and maintaining code style. By following these guidelines, you help ensure a smooth and collaborative contribution process.

## Table of Contents

- [Getting Started](#getting-started)
- [Setup Instructions](#setup-instructions)
- [How to Contribute](#how-to-contribute)
- [Pull Request Guidelines](#pull-request-guidelines)
- [Code Style](#code-style)
- [Issue Reporting](#issue-reporting)
- [Community Guidelines](#community-guidelines)

## Getting Started

This repository manages bounties for the RustChain ecosystem. Contributions are rewarded with RTC (RustChain Tokens). Before contributing, ensure you have:

- A GitHub account
- Basic familiarity with Git and GitHub workflows
- Understanding of the RustChain ecosystem (optional but recommended)

## Setup Instructions

1. **Fork the repository**  
   Click the "Fork" button at the top-right of this repository's GitHub page.

2. **Clone your fork**  
   ```bash
   git clone https://github.com/<your-username>/rustchain-bounties.git
   cd rustchain-bounties
   ```

3. **Add the upstream remote**  
   ```bash
   git remote add upstream https://github.com/Scottcjn/rustchain-bounties.git
   ```

4. **Create a branch for your changes**  
   ```bash
   git checkout -b feature/your-feature-name
   ```

5. **Make your changes**  
   Edit files as needed. For documentation contributions, ensure your Markdown is valid.

6. **Commit your changes**  
   ```bash
   git add .
   git commit -m "Add CONTRIBUTING.md with setup and PR guidelines"
   ```

7. **Push to your fork**  
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Open a pull request**  
   Go to the original repository and click "New Pull Request."

## How to Contribute

### Finding a Bounty

1. Browse the [open bounties](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aissue+is%3Aopen+label%3Abounty) labeled with `bounty`.
2. Look for issues tagged with `easy`, `documentation`, or `contributing` for beginner-friendly tasks.
3. Comment on the issue to express interest and ask clarifying questions if needed.

### Claiming a Bounty

- Bounties are first-come, first-served. Comment on the issue to claim it.
- If the issue is unassigned, you may start working immediately after commenting.
- For assigned issues, wait for the assignee to unassign themselves or complete the task.

### Submitting Work

- Follow the [Pull Request Guidelines](#pull-request-guidelines) below.
- Ensure your contribution meets the issue requirements.
- Reference the issue number in your PR description (e.g., `Closes #123`).

## Pull Request Guidelines

### PR Title Format

Use clear, descriptive titles:
- `Add CONTRIBUTING.md to repository`
- `Fix typo in README.md`
- `Update bounty description for issue #45`

### PR Description

Include:
- A brief summary of changes
- Reference to the related issue (e.g., `Closes #123`)
- Any relevant notes for reviewers

### Review Process

1. A maintainer will review your PR within 3–5 business days.
2. Address any feedback or requested changes promptly.
3. Once approved, the PR will be merged, and the bounty reward will be processed.

### Merge Requirements

- All conversations must be resolved.
- The PR must pass any automated checks (if applicable).
- At least one maintainer approval is required.

## Code Style

### General Guidelines

- Use consistent formatting throughout the repository.
- For Markdown files, follow [GitHub Flavored Markdown](https://github.github.com/gfm/).
- Use descriptive variable names in code examples (if any).

### Markdown Style

- Use `#` for headings, with a space after `#`.
- Use `-` for unordered lists.
- Use `1.` for ordered lists.
- Wrap inline code in backticks (`` ` ``).
- Use fenced code blocks with language identifiers:
  ```markdown
  ```bash
  git status
  ```
  ```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 72 characters or less.
- Reference issues and pull requests liberally after the first line.

## Issue Reporting

If you find a bug or have a suggestion:

1. Check if the issue already exists in the [issue tracker](https://github.com/Scottcjn/rustchain-bounties/issues).
2. If not, create a new issue with:
   - A clear title
   - Steps to reproduce (if applicable)
   - Expected vs. actual behavior
   - Screenshots or logs (if relevant)

## Community Guidelines

- Be respectful and constructive in all interactions.
- Follow the [RustChain Code of Conduct](https://github.com/Scottcjn/RustChain/blob/main/CODE_OF_CONDUCT.md) (if available).
- For bounty-related questions, comment on the relevant issue.
- For general questions, use the [Discussions](https://github.com/Scottcjn/rustchain-bounties/discussions) tab.

## Reward Process

- Bounties are paid in RTC after the PR is merged.
- Rewards are processed within 7 days of merge.
- For disputes or questions about rewards, contact a maintainer via the issue.

Thank you for contributing to RustChain Bounties! Your efforts help grow the ecosystem.