# Bounty Verification Bot

Automatically verifies bounty claims made in GitHub issue comments.

## How It Works

1. A user comments on a bounty issue with a claim in the format:
   - `Claim: star owner/repo` - Claims to have starred a repository
   - `Claim: follow username` - Claims to follow a GitHub user
   - `Claim: star owner/repo follow username` - Combined claim

2. The bot automatically:
   - Parses the claim from the comment
   - Verifies using the GitHub API
   - Posts a verification result as a reply comment

## Verification Types

### Star Verification
- Checks if the comment author has starred the specified repository
- Handles pagination for repositories with many stargazers
- Returns total star count as proof

### Follow Verification
- Checks if the comment author follows the specified GitHub user
- Validates that the target user exists
- Returns clear success/failure messages

## Setup

1. Add the workflow file to `.github/workflows/verify-claims.yml`
2. The bot uses the built-in `GITHUB_TOKEN` secret automatically
3. Ensure the workflow has `issues: write` permission

## Claim Format

Claims must start with "Claim:" and specify the type and target:
