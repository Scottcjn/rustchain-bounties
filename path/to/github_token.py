# Complete code
import os

def get_github_token() -> str:
    """
    Retrieves the GitHub token from the environment variables.

    Returns:
    str: The GitHub token.
    """
    return os.environ.get("GITHUB_TOKEN")

def main() -> None:
    token = get_github_token()
    if token:
        print(f"GitHub token: {token}")
    else:
        print("GitHub token not found")

if __name__ == "__main__":
    main()