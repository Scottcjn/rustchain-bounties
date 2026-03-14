import requests
from typing import List, Tuple, Dict

class RustchainStarsCampaign:
    BASE_URL = "https://api.github.com"
    REPO_URL = "/repos/Scottcjn/Rustchain"
    USER_URL = "/users/{username}"
    STARRED_URL = "/user/starred/{username}/{repo}"

    def __init__(self, username: str):
        self.username = username

    def get_repo_star_count(self) -> int:
        response = requests.get(f"{self.BASE_URL}{self.REPO_URL}")
        if response.status_code == 200:
            return response.json().get('stargazers_count', 0)
        else:
            raise Exception(f"Failed to fetch repository data: {response.status_code}")

    def star_repo(self, repo_name: str) -> None:
        response = requests.put(f"{self.BASE_URL}{self.STARRED_URL.format(username=self.username, repo=repo_name)}")
        if response.status_code != 204:
            raise Exception(f"Failed to star repository {repo_name}: {response.status_code}")

    def get_user_starred_repos(self) -> List[str]:
        starred_repos = []
        page = 1
        while True:
            response = requests.get(f"{self.BASE_URL}{self.USER_URL.format(username=self.username)}?per_page=100&page={page}")
            if response.status_code == 200:
                for repo in response.json():
                    starred_repos.append(repo['name'])
                if len(response.json()) < 100:
                    break
                page += 1
            else:
                raise Exception(f"Failed to fetch starred repositories: {response.status_code}")
        return starred_repos

    def calculate_bounty(self, starred_repos: List[str]) -> int:
        reward = 0
        if "Rustchain" in starred_repos:
            reward += 2
        for repo in starred_repos:
            if repo != "Rustchain":
                reward += 3
        return reward

    def share_on_social_media(self) -> None:
        # Placeholder for social media sharing logic
        pass

    def refer_friend(self) -> None:
        # Placeholder for referral logic
        pass

    def get_bounty_pool(self) -> int:
        # Placeholder for bounty pool logic
        return 5000

    def claim_bounty(self, reward: int) -> None:
        if reward > 0:
            print(f"Congratulations! You have earned {reward} RTC.")
        else:
            print("No reward earned.")

# Test cases
if __name__ == "__main__":
    campaign = RustchainStarsCampaign("testuser")
    try:
        print(f"Current stars on Rustchain: {campaign.get_repo_star_count()}")
        campaign.star_repo("Rustchain")
        print(f"Rustchain starred successfully.")
        starred_repos = campaign.get_user_starred_repos()
        print(f"Starred repositories: {starred_repos}")
        reward = campaign.calculate_bounty(starred_repos)
        print(f"Calculated reward: {reward}")
        campaign.claim_bounty(reward)
    except Exception as e:
        print(f"An error occurred: {e}")