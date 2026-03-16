import os
import time
import base64
import random
import string
import requests

# Constants and configuration
API_BASE = "https://api.github.com"
REPO_NAME = "Scottcjn/rustchain-bounties"
RTC_WALLET = f"RTC-agent-{''.join(random.choices(string.ascii_uppercase + string.digits, k=10))}"

# Optional token from environment (do not fail at import time)
TOKEN = os.getenv("GH_TOKEN") or os.getenv("GIT_TOKEN")

# Prepare a requests session
_session = requests.Session()
_session.headers.update({"Accept": "application/vnd.github+json"})
if TOKEN:
    _session.headers.update({"Authorization": f"token {TOKEN}"})


def _get_repo_info(full_name: str):
    resp = _session.get(f"{API_BASE}/repos/{full_name}")
    resp.raise_for_status()
    return resp.json()


def _get_authenticated_user():
    # Returns None if not authenticated
    resp = _session.get(f"{API_BASE}/user")
    if resp.status_code == 401:
        return None
    resp.raise_for_status()
    return resp.json()


def get_open_bounties():
    """
    Returns a list of open issues (excluding PRs and hardware-related) as dicts.
    """
    issues = []
    url = f"{API_BASE}/repos/{REPO_NAME}/issues"
    params = {"state": "open", "per_page": 100}
    while url:
        resp = _session.get(url, params=params)
        resp.raise_for_status()
        batch = resp.json()
        for issue in batch:
            if "pull_request" in issue:
                continue
            body = issue.get("body") or ""
            if "hardware" in body.lower():
                continue
            issues.append(issue)
        # Pagination
        next_url = None
        if "link" in resp.headers:
            links = resp.headers["link"].split(",")
            for link in links:
                parts = link.split(";")
                if len(parts) < 2:
                    continue
                href = parts[0].strip()[1:-1]
                rel = parts[1].strip()
                if rel == 'rel="next"':
                    next_url = href
                    break
        url = next_url
        params = None  # only needed on first request
    return issues


def claim_bounty(issue):
    """
    Posts a comment to claim a bounty on the provided issue dict.
    Requires authentication via GH_TOKEN or GIT_TOKEN.
    """
    if not TOKEN:
        raise RuntimeError("Missing GitHub API token. Set GH_TOKEN or GIT_TOKEN in environment.")
    number = issue["number"]
    comment = f"Claiming this bounty with AI agent. Wallet: {RTC_WALLET}"
    url = f"{API_BASE}/repos/{REPO_NAME}/issues/{number}/comments"
    resp = _session.post(url, json={"body": comment})
    resp.raise_for_status()
    print(f"Claimed bounty: {issue.get('title', f'#{number}')}")


def fork_repo_and_create_branch():
    """
    Forks the base repository into the authenticated user's account and creates a new branch.
    Returns (fork_full_name, branch_name).
    """
    if not TOKEN:
        raise RuntimeError("Missing GitHub API token. Set GH_TOKEN or GIT_TOKEN in environment.")

    # Initiate fork
    fork_url = f"{API_BASE}/repos/{REPO_NAME}/forks"
    resp = _session.post(fork_url)
    resp.raise_for_status()

    # Determine fork owner
    me = _get_authenticated_user()
    if not me:
        raise RuntimeError("Authentication required to fork repository.")
    fork_owner = me["login"]
    base_repo_info = _get_repo_info(REPO_NAME)
    fork_full_name = f"{fork_owner}/{base_repo_info['name']}"

    # Wait for fork to be ready
    for _ in range(30):
        r = _session.get(f"{API_BASE}/repos/{fork_full_name}")
        if r.status_code == 200:
            break
        time.sleep(1)
    else:
        raise RuntimeError("Timed out waiting for fork to become available.")

    # Determine default branch on the fork (usually same as source)
    fork_info = _get_repo_info(fork_full_name)
    default_branch = fork_info.get("default_branch") or "main"

    # Get SHA of default branch
    ref_resp = _session.get(f"{API_BASE}/repos/{fork_full_name}/git/ref/heads/{default_branch}")
    ref_resp.raise_for_status()
    sha = ref_resp.json()["object"]["sha"]

    # Create new branch
    branch_name = f"ai-agent-{RTC_WALLET}"
    create_ref_url = f"{API_BASE}/repos/{fork_full_name}/git/refs"
    payload = {"ref": f"refs/heads/{branch_name}", "sha": sha}
    ref_create = _session.post(create_ref_url, json=payload)
    if ref_create.status_code not in (201, 422):
        # 422 can be "Reference already exists"
        ref_create.raise_for_status()
    print(f"Created branch: {branch_name}")
    return fork_full_name, branch_name


def implement_solution(fork_full_name, branch_name):
    """
    Creates or updates a simple placeholder solution.py in the fork on the specified branch.
    """
    file_path = "solution.py"
    file_content = """# AI Agent Solution
# This is a simple placeholder solution by AI agent.
def hello():
    return "Hello from AI Agent"
"""
    b64 = base64.b64encode(file_content.encode("utf-8")).decode("ascii")

    get_url = f"{API_BASE}/repos/{fork_full_name}/contents/{file_path}"
    params = {"ref": branch_name}
    get_resp = _session.get(get_url, params=params)

    message = "Implementing solution"
    put_url = f"{API_BASE}/repos/{fork_full_name}/contents/{file_path}"

    if get_resp.status_code == 200:
        sha = get_resp.json()["sha"]
        payload = {
            "message": message,
            "content": b64,
            "branch": branch_name,
            "sha": sha,
        }
        resp = _session.put(put_url, json=payload)
        resp.raise_for_status()
        print(f"Updated solution in {file_path}")
    elif get_resp.status_code == 404:
        payload = {
            "message": message,
            "content": b64,
            "branch": branch_name,
        }
        resp = _session.put(put_url, json=payload)
        resp.raise_for_status()
        print(f"Implemented solution in {file_path}")
    else:
        get_resp.raise_for_status()


def submit_pull_request(base_repo_full_name, fork_full_name, branch_name, issue_number=None):
    """
    Submits a pull request from fork:branch_name to base repo's default branch.
    """
    base_info = _get_repo_info(base_repo_full_name)
    base_default_branch = base_info.get("default_branch") or "main"

    fork_owner = fork_full_name.split("/")[0]
    head = f"{fork_owner}:{branch_name}"

    title = "AI Agent Solution"
    body_parts = [
        f"Automated PR by AI Agent. Wallet: {RTC_WALLET}",
    ]
    if issue_number is not None:
        body_parts.append(f"Closes #{issue_number}")
    body = "\n\n".join(body_parts)

    url = f"{API_BASE}/repos/{base_repo_full_name}/pulls"
    payload = {
        "title": title,
        "head": head,
        "base": base_default_branch,
        "body": body,
        "maintainer_can_modify": True,
    }
    resp = _session.post(url, json=payload)
    resp.raise_for_status()
    pr = resp.json()
    print(f"Submitted PR: {pr.get('html_url')}")
    return pr


if __name__ == "__main__":
    # Example flow (will only run when executed as a script)
    try:
        open_bounties = get_open_bounties()
        issue_to_claim = open_bounties[0] if open_bounties else None

        if issue_to_claim and TOKEN:
            claim_bounty(issue_to_claim)
            fork_full, branch = fork_repo_and_create_branch()
            implement_solution(fork_full, branch)
            submit_pull_request(REPO_NAME, fork_full, branch, issue_number=issue_to_claim["number"])
        else:
            print("No open bounties found or missing token; nothing to do.")
    except Exception as e:
        print(f"Error: {e}")