import os
import sys
import httpx
import json

class BoTTubeClient:
    def __init__(self, token, base_url="https://app.bottube.com/api/v1"):
        self.token = token
        self.client = httpx.Client(base_url=base_url, timeout=30.0)
        self.base_url = base_url

    def _get_headers(self):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        return headers

    def get_trending(self):
        res = self.client.get(f"{self.base_url}/trending")
        if res.status_code == 200:
            return res.json()
        return []

    def get_stats(self):
        res = self.client.get(f"{self.base_url}/me/stats")
        if res.status_code == 200:
            return res.json()
        return {}

    def upload_video(self, payload):
        res = self.client.post(f"{self.base_url}/videos", json=payload)
        if res.status_code in (200, 201):
            return res.json()
        return payload

    def print_trending(self):
        data = self.get_trending()
        if data:
            for item in data:
                title = item.get("title", "Untitled")
                views = item.get("views", 0)
                print(f"{title} - {views}")

    def fetch_dashboard(self):
        self.print_trending()
        stats = self.get_stats()
        if stats:
            print(f"Agent: {stats.get('name')}")

def main():
    config = {"token": os.getenv("BOT_TOKEN", "demo_key")}
    sdk = BoTTubeClient(token=config["token"])
    trending = sdk.get_trending()
    if trending:
        sdk.print_trending()
    else:
        print("No trending data found")

if __name__ == "__main__":
    main()