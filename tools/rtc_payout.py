import os
import sys
import json
import github
from rustchain_sdk.wallet import RustChainWallet

def payout_rtc(wallet, password, github_token, pr_number, approved_bounty, dedupe):
    # Set up the GitHub API
    g = github.Github(github_token)
    repo = g.get_repo("Scottcjn/rustchain-bounties")
    pr = repo.get_pull(pr_number)

    # Check if the PR has an approved bounty
    if not approved_bounty:
        print("PR does not have an approved bounty")
        return

    # Check if the PR has a valid RTC wallet address
    wallet_address = None
    for comment in pr.get_comments():
        if comment.body.startswith("RTC Wallet:"):
            wallet_address = comment.body.split(":")[1].strip()
            break
    if wallet_address is None:
        print("PR does not have a valid RTC wallet address")
        return

    # Check for duplicates
    if dedupe:
        # Check if a payout has already been made for this PR
        payouts = json.loads(open("payouts.json").read())
        if pr_number in payouts:
            print("Payout has already been made for this PR")
            return

    # Make the payout
    wallet = RustChainWallet(wallet, password)
    tx_hash = wallet.send(wallet_address, 1)
    print(f"Payout made: {tx_hash}")

    # Update the payouts JSON file
    payouts = json.loads(open("payouts.json").read())
    payouts[pr_number] = tx_hash
    open("payouts.json", "w").write(json.dumps(payouts))

if __name__ == "__main__":
    if len(sys.argv) != 7:
        print("Usage: python rtc_payout.py <wallet> <password> <github_token> <pr_number> <approved_bounty> <dedupe>")
        sys.exit(1)

    wallet = sys.argv[1]
    password = sys.argv[2]
    github_token = sys.argv[3]
    pr_number = int(sys.argv[4])
    approved_bounty = sys.argv[5].lower() == "true"
    dedupe = sys.argv[6].lower() == "true"

    payout_rtc(wallet, password, github_token, pr_number, approved_bounty, dedupe)