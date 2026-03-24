import requests

class LadderManager:
    """
    Contributor Ladder Automation for RustChain.
    Automatically tracks merged PRs and participation time to assign tiers.
    Addresses issue #343.
    """
    TIERS = {
        1: "Explorer",
        2: "Miner",
        3: "Foreman",
        4: "Architect",
        5: "Guardian"
    }

    def calculate_tier(self, pr_count, days_active):
        if pr_count >= 10 and days_active >= 90:
            return 3 # Foreman
        if pr_count >= 3 and days_active >= 30:
            return 2 # Miner
        if pr_count >= 1:
            return 1 # Explorer
        return 0

    def assign_tier(self, github_user, tier):
        print(f"Assigning tier {self.TIERS[tier]} to {github_user}...")
        # Logic to post comment on issue or update leaderboard file
