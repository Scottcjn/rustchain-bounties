import os
import sys
import requests
import json
from github import Github


def verify_poa(commit_sha, poa_hash, rpc_url):
    """Verify a PoA-Signature hash by calling the RustChain attest/verify RPC.

    Previously this was a stub that returned True whenever the value
    started with the literal prefix `poa_`. That bypass let any contributor
    mark their PR as PoA-verified without actually presenting evidence
    to the chain. This implementation:

    * POSTs {commit_sha, poa_hash} to {rpc_url}/api/v1/attest/verify.
    * Requires the response to declare `ok=true` and `verified=true`.
    * Treats every RPC error, timeout, or shape mismatch as a fail-closed
      rejection (returns False, not None).
    * Honors RUSTCHAIN_INSECURE_SKIP_TLS_VERIFY=1 for operators running the
      action against an internal HTTP-only RPC; the default is verify=True.
    """
    print(f"Verifying PoA Hash {poa_hash} for commit {commit_sha}...")
    if not (rpc_url and poa_hash):
        return False
    insecure = os.environ.get("RUSTCHAIN_INSECURE_SKIP_TLS_VERIFY") == "1"
    if insecure:
        print("::warning::RUSTCHAIN_INSECURE_SKIP_TLS_VERIFY=1 — TLS verify disabled for PoA RPC")
    url = f"{rpc_url.rstrip('/')}/api/v1/attest/verify"
    try:
        resp = requests.post(
            url,
            json={"commit_sha": commit_sha, "poa_hash": poa_hash},
            timeout=15,
            verify=not insecure,
        )
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.SSLError) as exc:
        print(f"PoA RPC request failed: {exc.__class__.__name__}: {exc}")
        return False
    if resp.status_code != 200:
        print(f"PoA RPC returned HTTP {resp.status_code}; treating as fail-closed")
        return False
    try:
        data = resp.json()
    except ValueError:
        print("PoA RPC returned non-JSON body; treating as fail-closed")
        return False
    if not isinstance(data, dict):
        return False
    return bool(data.get("ok")) and bool(data.get("verified"))


def main():
    # GitHub Actions normalizes hyphenated input names to underscored env vars.
    token = os.environ.get("INPUT_GITHUB_TOKEN") or os.environ.get("INPUT_GITHUB-TOKEN")
    rpc_url = os.environ.get("INPUT_RPC_URL") or os.environ.get("INPUT_RPC-URL")

    if not token:
        print("Missing GITHUB-TOKEN")
        sys.exit(1)

    github_event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not github_event_path or not os.path.exists(github_event_path):
        print("Missing GITHUB_EVENT_PATH")
        sys.exit(1)

    # Windows runners default to cp1252; GitHub event JSON is always UTF-8.
    with open(github_event_path, "r", encoding="utf-8") as f:
        event_data = json.load(f)

    if not isinstance(event_data, dict) or "pull_request" not in event_data:
        print("Not a pull request event. Skipping.")
        sys.exit(0)

    pr_data = event_data.get("pull_request") or {}
    repo_name = ((event_data.get("repository") or {}).get("full_name") or "")
    pr_number = pr_data.get("number")
    if not (repo_name and pr_number):
        print("Malformed pull_request event payload (missing repo/number). Failing closed.")
        sys.exit(1)

    g = Github(token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    commits = list(pr.get_commits())
    if not commits:
        print("No commits found in this PR. Failing closed.")
        sys.exit(1)
    latest_commit = commits[-1]
    commit_msg = latest_commit.commit.message

    poa_hash = None
    sig_lines = 0
    for line in commit_msg.splitlines():
        if line.startswith("PoA-Signature: "):
            sig_lines += 1
            if sig_lines > 1:
                print("Multiple PoA-Signature lines in commit message. Rejecting.")
                sys.exit(1)
            poa_hash = line.split("PoA-Signature: ", 1)[1].strip()

    if not poa_hash:
        print("No PoA signature found. Skipping verification (optional).")
        sys.exit(0)

    is_valid = verify_poa(latest_commit.sha, poa_hash, rpc_url)

    if is_valid:
        pr.create_issue_comment(
            "✅ **Glassworm Protocol Verified** ✅\n\nProof of Antiquity signature successfully validated. Hardware fingerprint confirmed."
        )
        pr.add_to_labels("poa-verified")
        try:
            pr.remove_from_labels("poa-failed")
        except:
            pass
        print("PoA signature valid.")
        sys.exit(0)
    else:
        pr.create_issue_comment(
            "🛑 **Glassworm Protocol Alert** 🛑\n\nInvalid Proof of Antiquity signature detected. Hardware Sybil attempt flagged."
        )
        pr.add_to_labels("poa-failed")
        try:
            pr.remove_from_labels("poa-verified")
        except:
            pass
        print("Invalid PoA signature.")
        sys.exit(1)


if __name__ == "__main__":
    main()
