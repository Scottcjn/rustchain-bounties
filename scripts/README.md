# Star ClawHub Repositories Script

This script automates the process of starring the repositories listed in bounty #165 and leaving review comments with the required disclosure statement.

## Usage

1. Set up a GitHub Personal Access Token with the necessary permissions
2. Set the `GITHUB_TOKEN` environment variable
3. Run the script:

```bash
python scripts/star_clawhub_repos.py
```

## Requirements

- Python 3.6+
- `requests` library (will be installed automatically)

## Repositories

The script will star the following repositories:
- Scottcjn/beacon-skill
- Scottcjn/grazer-skill
- Scottcjn/bottube
- Scottcjn/Rustchain

## Workflow

The script can also be run using the GitHub Actions workflow:

1. Go to the Actions tab
2. Select "Star ClawHub Repositories"
3. Click "Run workflow"
4. Enter your GitHub username
5. Click "Run workflow"

## Verification

The bounty claim workflow will automatically verify that all repositories have been starred and appropriate comments have been left.