# complete code
import os
from github_reviewer import GitHubReviewer
from config import GITHUB_TOKEN, REPO_OWNER, REPO_NAME, PR_NUMBER, COMMENT

def main():
    reviewer = GitHubReviewer(GITHUB_TOKEN)
    try:
        reviewer.leave_comment(REPO_OWNER, REPO_NAME, PR_NUMBER, COMMENT)
        print('Comment left successfully!')
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    main()