
import requests
import os
from typing import Dict, Any, Optional

ALLOWED_DOMAINS = ["github.com", "moltbook.com", "4claw.io", "bottube.com"]

class GitHubVerifier:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Bounty-Verification-Bot"
        }

    def check_following(self, user: str, target: str = "Scottcjn") -> bool:
        url = f"https://api.github.com/users/{user}/following/{target}"
        res = requests.get(url, headers=self.headers)
        return res.status_code == 204

    def count_stars(self, user: str, org: str = "Scottcjn") -> int:
        stars = 0
        page = 1
        while True:
            url = f"https://api.github.com/users/{user}/starred?per_page=100&page={page}"
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200: break
            data = res.json()
            if not data: break
            # FIXED: Use exact match for org/user instead of substring
            stars += sum(1 for repo in data if repo['full_name'].startswith(f"{org}/"))
            page += 1
        return stars

class WalletVerifier:
    def __init__(self, node_url: str = "https://50.28.86.131"):
        self.node_url = node_url

    def verify_wallet(self, wallet_id: str) -> Optional[float]:
        url = f"{self.node_url}/wallet/balance?miner_id={wallet_id}"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return float(res.json().get("amount_rtc", 0))
        except Exception:
            pass
        return None

class ContentVerifier:
    def _is_allowed(self, url: str) -> bool:
        # Basic SSRF protection: only allow whitelisted domains
        from urllib.parse import urlparse
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        domain = parsed.netloc.lower()
        return any(domain == d or domain.endswith("." + d) for d in ALLOWED_DOMAINS)

    def verify_url(self, url: str) -> bool:
        if not self._is_allowed(url):
            return False
        try:
            res = requests.head(url, timeout=10, allow_redirects=True)
            return res.status_code == 200
        except Exception:
            return False

    def get_word_count(self, url: str) -> int:
        if not self._is_allowed(url):
            return 0
        try:
            res = requests.get(url, timeout=10)
            text = res.text.lower()
            return len(text.split())
        except Exception:
            return 0
