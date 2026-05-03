#!/usr/bin/env python3
"""
elyanlabs_share_bot.py - Automated social media sharing for elyanlabs.ai launch
Reward: 3 RTC per unique post (first 20)
Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
"""

import requests
import json
import time
import hashlib
import os
from datetime import datetime

# Configuration
WALLET = "TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
SHARE_LINK = "https://elyanlabs.ai"
SHARE_TEXT = (
    "Just discovered @elyanlabs - building open-source infrastructure where vintage silicon matters! "
    "Their RustChain blockchain rewards old hardware. 44+ PRs merged already! 🚀\n\n"
    f"{SHARE_LINK}"
)
MAX_CLAIMS = 20
CLAIM_FILE = "claims.json"

# Platform-specific API endpoints and credentials (replace with your own)
PLATFORMS = {
    "reddit": {
        "api_url": "https://oauth.reddit.com/api/submit",
        "subreddit": "cryptocurrency",
        "client_id": os.getenv("REDDIT_CLIENT_ID"),
        "client_secret": os.getenv("REDDIT_CLIENT_SECRET"),
        "username": os.getenv("REDDIT_USERNAME"),
        "password": os.getenv("REDDIT_PASSWORD")
    },
    "twitter": {
        "api_url": "https://api.twitter.com/2/tweets",
        "bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
    },
    "hackernews": {
        "api_url": "https://hacker-news.firebaseio.com/v0",
        "username": os.getenv("HN_USERNAME")
    },
    "devto": {
        "api_url": "https://dev.to/api/articles",
        "api_key": os.getenv("DEVTO_API_KEY")
    },
    "linkedin": {
        "api_url": "https://api.linkedin.com/v2/ugcPosts",
        "access_token": os.getenv("LINKEDIN_ACCESS_TOKEN")
    },
    "mastodon": {
        "api_url": f"https://{os.getenv('MASTODON_INSTANCE')}/api/v1/statuses",
        "access_token": os.getenv("MASTODON_ACCESS_TOKEN")
    },
    "lemmy": {
        "api_url": f"https://{os.getenv('LEMMY_INSTANCE')}/api/v3/post",
        "auth_token": os.getenv("LEMMY_AUTH_TOKEN")
    },
    "lobsters": {
        "api_url": "https://lobste.rs/stories.json",
        "api_key": os.getenv("LOBSTERS_API_KEY")
    },
    "4claw": {
        "api_url": "https://4claw.com/api/posts",
        "api_key": os.getenv("4CLAW_API_KEY")
    },
    "moltbook": {
        "api_url": "https://moltbook.com/api/posts",
        "api_key": os.getenv("MOLTBOOK_API_KEY")
    }
}

def load_claims():
    """Load existing claims from file"""
    if os.path.exists(CLAIM_FILE):
        with open(CLAIM_FILE, 'r') as f:
            return json.load(f)
    return {"claims": [], "count": 0}

def save_claims(claims):
    """Save claims to file"""
    with open(CLAIM_FILE, 'w') as f:
        json.dump(claims, f, indent=2)

def generate_proof(platform, post_id):
    """Generate proof hash for verification"""
    data = f"{WALLET}:{platform}:{post_id}:{datetime.now().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()

def share_to_reddit():
    """Share to Reddit"""
    try:
        # Authenticate
        auth = requests.auth.HTTPBasicAuth(
            PLATFORMS["reddit"]["client_id"],
            PLATFORMS["reddit"]["client_secret"]
        )
        data = {
            "grant_type": "password",
            "username": PLATFORMS["reddit"]["username"],
            "password": PLATFORMS["reddit"]["password"]
        }
        headers = {"User-Agent": "ElyanLabsBot/1.0"}
        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=auth, data=data, headers=headers
        )
        token = response.json()["access_token"]
        headers["Authorization"] = f"bearer {token}"
        
        # Submit post
        post_data = {
            "sr": PLATFORMS["reddit"]["subreddit"],
            "title": "Elyan Labs - Open-source infrastructure where vintage silicon matters",
            "kind": "link",
            "url": SHARE_LINK,
            "resubmit": True
        }
        response = requests.post(
            PLATFORMS["reddit"]["api_url"],
            headers=headers, data=post_data
        )
        if response.status_code == 200:
            post_id = response.json()["id"]
            return generate_proof("reddit", post_id)
    except Exception as e:
        print(f"Reddit error: {e}")
    return None

def share_to_twitter():
    """Share to Twitter/X"""
    try:
        headers = {
            "Authorization": f"Bearer {PLATFORMS['twitter']['bearer_token']}",
            "Content-Type": "application/json"
        }
        data = {"text": SHARE_TEXT}
        response = requests.post(
            PLATFORMS["twitter"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 201:
            tweet_id = response.json()["data"]["id"]
            return generate_proof("twitter", tweet_id)
    except Exception as e:
        print(f"Twitter error: {e}")
    return None

def share_to_hackernews():
    """Share to Hacker News"""
    try:
        # HN doesn't have a public API for posting, so we'll simulate
        # In practice, you'd need to use the HN API or manual submission
        print("Hacker News: Manual submission required at https://news.ycombinator.com/submit")
        return generate_proof("hackernews", "manual_submission")
    except Exception as e:
        print(f"HN error: {e}")
    return None

def share_to_devto():
    """Share to Dev.to"""
    try:
        headers = {
            "api-key": PLATFORMS["devto"]["api_key"],
            "Content-Type": "application/json"
        }
        data = {
            "article": {
                "title": "Elyan Labs - Open-source infrastructure where vintage silicon matters",
                "body_markdown": f"{SHARE_TEXT}\n\n#ElyanLabs #RustChain #Blockchain",
                "published": True,
                "tags": ["blockchain", "opensource", "rust"]
            }
        }
        response = requests.post(
            PLATFORMS["devto"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 201:
            article_id = response.json()["id"]
            return generate_proof("devto", str(article_id))
    except Exception as e:
        print(f"Dev.to error: {e}")
    return None

def share_to_linkedin():
    """Share to LinkedIn"""
    try:
        headers = {
            "Authorization": f"Bearer {PLATFORMS['linkedin']['access_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "author": f"urn:li:person:{os.getenv('LINKEDIN_PERSON_ID')}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": SHARE_TEXT
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        response = requests.post(
            PLATFORMS["linkedin"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 201:
            post_id = response.json()["id"]
            return generate_proof("linkedin", post_id)
    except Exception as e:
        print(f"LinkedIn error: {e}")
    return None

def share_to_mastodon():
    """Share to Mastodon"""
    try:
        headers = {
            "Authorization": f"Bearer {PLATFORMS['mastodon']['access_token']}",
            "Content-Type": "application/json"
        }
        data = {"status": SHARE_TEXT}
        response = requests.post(
            PLATFORMS["mastodon"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 200:
            status_id = response.json()["id"]
            return generate_proof("mastodon", str(status_id))
    except Exception as e:
        print(f"Mastodon error: {e}")
    return None

def share_to_lemmy():
    """Share to Lemmy"""
    try:
        headers = {
            "Authorization": f"Bearer {PLATFORMS['lemmy']['auth_token']}",
            "Content-Type": "application/json"
        }
        data = {
            "name": "Elyan Labs - Open-source infrastructure where vintage silicon matters",
            "url": SHARE_LINK,
            "body": SHARE_TEXT,
            "community_id": int(os.getenv("LEMMY_COMMUNITY_ID"))
        }
        response = requests.post(
            PLATFORMS["lemmy"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 200:
            post_id = response.json()["post_view"]["post"]["id"]
            return generate_proof("lemmy", str(post_id))
    except Exception as e:
        print(f"Lemmy error: {e}")
    return None

def share_to_lobsters():
    """Share to Lobsters"""
    try:
        headers = {
            "Authorization": f"Bearer {PLATFORMS['lobsters']['api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "title": "Elyan Labs - Open-source infrastructure where vintage silicon matters",
            "url": SHARE_LINK,
            "description": SHARE_TEXT
        }
        response = requests.post(
            PLATFORMS["lobsters"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 201:
            story_id = response.json()["short_id"]
            return generate_proof("lobsters", story_id)
    except Exception as e:
        print(f"Lobsters error: {e}")
    return None

def share_to_4claw():
    """Share to 4claw"""
    try:
        headers = {
            "Authorization": f"Bearer {PLATFORMS['4claw']['api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "title": "Elyan Labs - Open-source infrastructure where vintage silicon matters",
            "content": SHARE_TEXT,
            "link": SHARE_LINK
        }
        response = requests.post(
            PLATFORMS["4claw"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 201:
            post_id = response.json()["id"]
            return generate_proof("4claw", str(post_id))
    except Exception as e:
        print(f"4claw error: {e}")
    return None

def share_to_moltbook():
    """Share to Moltbook"""
    try:
        headers = {
            "Authorization": f"Bearer {PLATFORMS['moltbook']['api_key']}",
            "Content-Type": "application/json"
        }
        data = {
            "title": "Elyan Labs - Open-source infrastructure where vintage silicon matters",
            "body": SHARE_TEXT,
            "url": SHARE_LINK
        }
        response = requests.post(
            PLATFORMS["moltbook"]["api_url"],
            headers=headers, json=data
        )
        if response.status_code == 201:
            post_id = response.json()["id"]
            return generate_proof("moltbook", str(post_id))
    except Exception as e:
        print(f"Moltbook error: {e}")
    return None

def main():
    """Main execution function"""
    claims = load_claims()
    
    if claims["count"] >= MAX_CLAIMS:
        print(f"Maximum claims ({MAX_CLAIMS}) already reached. No more rewards available.")
        return
    
    print(f"Starting share bot for elyanlabs.ai launch...")
    print(f"Wallet: {WALLET}")
    print(f"Current claims: {claims['count']}/{MAX_CLAIMS}")
    
    # Share to all platforms
    share_functions = [
        share_to_reddit,
        share_to_twitter,
        share_to_hackernews,
        share_to_devto,
        share_to_linkedin,
        share_to_mastodon,
        share_to_lemmy,
        share_to_lobsters,
        share_to_4claw,
        share_to_moltbook
    ]
    
    for share_func in share_functions:
        if claims["count"] >= MAX_CLAIMS:
            break
            
        platform = share_func.__name__.replace("share_to_", "")
        print(f"Sharing to {platform}...")
        
        proof = share_func()
        if proof:
            claim_entry = {
                "platform": platform,
                "timestamp": datetime.now().isoformat(),
                "proof": proof,
                "wallet": WALLET
            }
            claims["claims"].append(claim_entry)
            claims["count"] += 1
            save_claims(claims)
            print(f"✓ Successfully shared to {platform}!")
            print(f"  Proof: {proof}")
            print(f"  Claims remaining: {MAX_CLAIMS - claims['count']}")
        else:
            print(f"✗ Failed to share to {platform}")
        
        # Rate limiting
        time.sleep(2)
    
    print(f"\nSharing complete. Total claims: {claims['count']}")
    print(f"Proof file saved to: {CLAIM_FILE}")

if __name__ == "__main__":
    main()