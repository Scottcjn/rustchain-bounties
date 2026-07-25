import requests
from github import Github

def review_pr():
    # Replace with your own GitHub token
    token = "your_github_token"
    g = Github(token)

    # Choose a repository
    repo_name = "Rustchain"
    repo = g.get_repo(f"Scottcjn/{repo_name}")

    # Get all open pull requests
    open_prs = repo.get_pulls(state="open")

    # Pick the first open PR
    pr = next(iter(open_prs))

    # Get the files changed in the PR
    files_changed = pr.get_files()

    # Leave a review comment
    review_comment = ""
    for file in files_changed:
        # Read the file contents
        file_contents = requests.get(file.raw_url).text

        # Check for potential issues
        lines = file_contents.splitlines()
        for i, line in enumerate(lines, start=1):
            # Check for SQL injection
            if "SQL" in line and "?" not in line:
                review_comment += f"Line {i}: this SQL query isn't parameterized, potential injection\n"

            # Check for duplicated logic
            if "def" in line:
                # This is a very basic check and would need to be improved
                review_comment += f"Line {i}: this function might duplicate logic already in another file\n"

            # Check for missing error handling
            if "requests" in line and ".json()" in line:
                review_comment += f"Line {i}: missing error handling if the API returns non-200\n"

            # Check for variable names
            if "=" in line and "_" not in line:
                review_comment += f"Line {i}: the variable name should describe what it holds\n"

    # Post the review comment
    pr.create_issue_comment(review_comment)

    # Print the link to the review comment
    print(pr.html_url)

review_pr()