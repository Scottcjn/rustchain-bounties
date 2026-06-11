
import requests
import json

BASE_URL = "https://bottube.ai"

def health_check():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def get_videos(limit=5, category=None):
    params = {"limit": limit}
    if category:
        params["category"] = category
    try:
        r = requests.get(f"{BASE_URL}/api/videos", params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def get_agents(limit=5):
    try:
        r = requests.get(f"{BASE_URL}/api/agents", params={"limit": limit}, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("BoTTube API Integration Example")
    print("=" * 40)
    health = health_check()
    print(f"Health: {json.dumps(health, indent=2)[:200]}")
    print()
    videos = get_videos(3)
    print(f"Videos: {json.dumps(videos, indent=2)[:300]}")
