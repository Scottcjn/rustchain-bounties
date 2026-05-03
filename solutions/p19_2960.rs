#!/usr/bin/env python3
"""
Social Media Share Bot for elyanlabs.ai Launch
Reward: 3 RTC per unique post (first 20)
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration
WALLET = "TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
SHARE_LINK = "https://elyanlabs.ai"
SHARE_TEXT = (
    "Just discovered Elyan Labs - open-source infrastructure where vintage silicon matters! "
    "RustChain blockchain rewards old hardware. 44+ PRs merged. Check it out: " + SHARE_LINK
)

# Platform API endpoints and credentials (placeholder - replace with actual)
PLATFORMS = {
    "reddit": {
        "api_url": "https://oauth.reddit.com/api/submit",
        "subreddit": "cryptocurrency",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "username": "YOUR_USERNAME",
        "password": "YOUR_PASSWORD"
    },
    "hackernews": {
        "api_url": "https://hacker-news.firebaseio.com/v0",
        "username": "YOUR_HN_USERNAME"
    },
    "devto": {
        "api_url": "https://dev.to/api/articles",
        "api_key": "YOUR_DEVTO_API_KEY"
    },
    "twitter": {
        "api_url": "https://api.twitter.com/2/tweets",
        "bearer_token": "YOUR_TWITTER_BEARER_TOKEN"
    },
    "linkedin": {
        "api_url": "https://api.linkedin.com/v2/ugcPosts",
        "access_token": "YOUR_LINKEDIN_ACCESS_TOKEN"
    },
    "mastodon": {
        "api_url": "https://mastodon.social/api/v1/statuses",
        "access_token": "YOUR_MASTODON_ACCESS_TOKEN"
    },
    "lemmy": {
        "api_url": "https://lemmy.ml/api/v3/post",
        "auth_token": "YOUR_LEMMY_AUTH_TOKEN"
    },
    "lobsters": {
        "api_url": "https://lobste.rs/stories.json",
        "username": "YOUR_LOBSTERS_USERNAME"
    },
    "4claw": {
        "api_url": "https://4claw.com/api/posts",
        "api_key": "YOUR_4CLAW_API_KEY"
    },
    "moltbook": {
        "api_url": "https://moltbook.com/api/posts",
        "api_key": "YOUR_MOLTBOOK_API_KEY"
    }
}

class SocialShareBot:
    def __init__(self):
        self.posted_platforms = []
        self.proof_links = []
        
    def post_to_reddit(self):
        """Post to Reddit"""
        try:
            headers = {
                "User-Agent": "ElyanLabsShareBot/1.0"
            }
            auth = requests.auth.HTTPBasicAuth(
                PLATFORMS["reddit"]["client_id"],
                PLATFORMS["reddit"]["client_secret"]
            )
            data = {
                "grant_type": "password",
                "username": PLATFORMS["reddit"]["username"],
                "password": PLATFORMS["reddit"]["password"]
            }
            
            # Get token
            response = requests.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data,
                headers=headers
            )
            token = response.json()["access_token"]
            
            # Submit post
            headers["Authorization"] = f"bearer {token}"
            post_data = {
                "sr": PLATFORMS["reddit"]["subreddit"],
                "title": "Elyan Labs - Open Source Infrastructure for Vintage Silicon",
                "kind": "link",
                "url": SHARE_LINK,
                "resubmit": True
            }
            response = requests.post(
                PLATFORMS["reddit"]["api_url"],
                headers=headers,
                data=post_data
            )
            
            if response.status_code == 200:
                post_id = response.json()["json"]["data"]["id"]
                proof_url = f"https://reddit.com/r/{PLATFORMS['reddit']['subreddit']}/comments/{post_id}"
                self.proof_links.append(proof_url)
                self.posted_platforms.append("reddit")
                return True
        except Exception as e:
            print(f"Reddit post failed: {e}")
        return False
    
    def post_to_hackernews(self):
        """Post to Hacker News"""
        try:
            # HN doesn't have a public API for posting, so we'll use a workaround
            # This is a placeholder - actual implementation would require scraping
            print("Hacker News posting requires manual intervention")
            return False
        except Exception as e:
            print(f"HN post failed: {e}")
        return False
    
    def post_to_devto(self):
        """Post to Dev.to"""
        try:
            headers = {
                "api-key": PLATFORMS["devto"]["api_key"],
                "Content-Type": "application/json"
            }
            data = {
                "article": {
                    "title": "Elyan Labs: Open Source Infrastructure for Vintage Silicon",
                    "body_markdown": f"{SHARE_TEXT}\n\n#ElyanLabs #RustChain #OpenSource",
                    "published": True,
                    "tags": ["opensource", "blockchain", "rust", "vintage"]
                }
            }
            response = requests.post(
                PLATFORMS["devto"]["api_url"],
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                article_url = response.json()["url"]
                self.proof_links.append(article_url)
                self.posted_platforms.append("devto")
                return True
        except Exception as e:
            print(f"Dev.to post failed: {e}")
        return False
    
    def post_to_twitter(self):
        """Post to X/Twitter"""
        try:
            headers = {
                "Authorization": f"Bearer {PLATFORMS['twitter']['bearer_token']}",
                "Content-Type": "application/json"
            }
            data = {
                "text": SHARE_TEXT + " #ElyanLabs #RustChain"
            }
            response = requests.post(
                PLATFORMS["twitter"]["api_url"],
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                tweet_id = response.json()["data"]["id"]
                proof_url = f"https://twitter.com/user/status/{tweet_id}"
                self.proof_links.append(proof_url)
                self.posted_platforms.append("twitter")
                return True
        except Exception as e:
            print(f"Twitter post failed: {e}")
        return False
    
    def post_to_linkedin(self):
        """Post to LinkedIn"""
        try:
            headers = {
                "Authorization": f"Bearer {PLATFORMS['linkedin']['access_token']}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            data = {
                "author": f"urn:li:person:{PLATFORMS['linkedin']['access_token']}",
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
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                post_id = response.json()["id"]
                proof_url = f"https://linkedin.com/feed/update/{post_id}"
                self.proof_links.append(proof_url)
                self.posted_platforms.append("linkedin")
                return True
        except Exception as e:
            print(f"LinkedIn post failed: {e}")
        return False
    
    def post_to_mastodon(self):
        """Post to Mastodon"""
        try:
            headers = {
                "Authorization": f"Bearer {PLATFORMS['mastodon']['access_token']}"
            }
            data = {
                "status": SHARE_TEXT + " #ElyanLabs #RustChain #OpenSource",
                "visibility": "public"
            }
            response = requests.post(
                PLATFORMS["mastodon"]["api_url"],
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                status_id = response.json()["id"]
                proof_url = f"https://mastodon.social/@{PLATFORMS['mastodon']['access_token']}/{status_id}"
                self.proof_links.append(proof_url)
                self.posted_platforms.append("mastodon")
                return True
        except Exception as e:
            print(f"Mastodon post failed: {e}")
        return False
    
    def post_to_lemmy(self):
        """Post to Lemmy"""
        try:
            headers = {
                "Authorization": f"Bearer {PLATFORMS['lemmy']['auth_token']}",
                "Content-Type": "application/json"
            }
            data = {
                "name": "Elyan Labs - Open Source Infrastructure for Vintage Silicon",
                "url": SHARE_LINK,
                "body": SHARE_TEXT,
                "nsfw": False,
                "community_id": 1  # Replace with actual community ID
            }
            response = requests.post(
                PLATFORMS["lemmy"]["api_url"],
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                post_id = response.json()["post_view"]["post"]["id"]
                proof_url = f"https://lemmy.ml/post/{post_id}"
                self.proof_links.append(proof_url)
                self.posted_platforms.append("lemmy")
                return True
        except Exception as e:
            print(f"Lemmy post failed: {e}")
        return False
    
    def post_to_lobsters(self):
        """Post to Lobsters"""
        try:
            # Lobsters requires manual posting via web interface
            print("Lobsters posting requires manual intervention")
            return False
        except Exception as e:
            print(f"Lobsters post failed: {e}")
        return False
    
    def post_to_4claw(self):
        """Post to 4claw"""
        try:
            headers = {
                "Authorization": f"Bearer {PLATFORMS['4claw']['api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "title": "Elyan Labs - Open Source Infrastructure for Vintage Silicon",
                "content": SHARE_TEXT,
                "link": SHARE_LINK,
                "tags": ["opensource", "blockchain", "rust"]
            }
            response = requests.post(
                PLATFORMS["4claw"]["api_url"],
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                post_id = response.json()["id"]
                proof_url = f"https://4claw.com/post/{post_id}"
                self.proof_links.append(proof_url)
                self.posted_platforms.append("4claw")
                return True
        except Exception as e:
            print(f"4claw post failed: {e}")
        return False
    
    def post_to_moltbook(self):
        """Post to Moltbook"""
        try:
            headers = {
                "Authorization": f"Bearer {PLATFORMS['moltbook']['api_key']}",
                "Content-Type": "application/json"
            }
            data = {
                "title": "Elyan Labs - Open Source Infrastructure for Vintage Silicon",
                "body": SHARE_TEXT,
                "url": SHARE_LINK,
                "category": "technology"
            }
            response = requests.post(
                PLATFORMS["moltbook"]["api_url"],
                headers=headers,
                json=data
            )
            
            if response.status_code == 201:
                post_id = response.json()["id"]
                proof_url = f"https://moltbook.com/post/{post_id}"
                self.proof_links.append(proof_url)
                self.posted_platforms.append("moltbook")
                return True
        except Exception as e:
            print(f"Moltbook post failed: {e}")
        return False
    
    def run(self):
        """Execute all platform posts"""
        print(f"Starting social media share for elyanlabs.ai")
        print(f"Wallet: {WALLET}")
        print(f"Time: {datetime.now().isoformat()}")
        print("-" * 50)
        
        # Post to each platform
        post_methods = [
            self.post_to_reddit,
            self.post_to_hackernews,
            self.post_to_devto,
            self.post_to_twitter,
            self.post_to_linkedin,
            self.post_to_mastodon,
            self.post_to_lemmy,
            self.post_to_lobsters,
            self.post_to_4claw,
            self.post_to_moltbook
        ]
        
        for method in post_methods:
            platform_name = method.__name__.replace("post_to_", "")
            print(f"Posting to {platform_name}...")
            success = method()
            if success:
                print(f"✓ Successfully posted to {platform_name}")
            else:
                print(f"✗ Failed to post to {platform_name}")
            time.sleep(random.uniform(1, 3))  # Rate limiting
        
        # Generate proof
        print("\n" + "=" * 50)
        print("SHARE PROOF")
        print("=" * 50)
        print(f"Wallet: {WALLET}")
        print(f"Platforms posted: {', '.join(self.posted_platforms)}")
        print("Proof links:")
        for link in self.proof_links:
            print(f"  - {link}")
        
        # Save proof to file
        proof_data = {
            "wallet": WALLET,
            "timestamp": datetime.now().isoformat(),
            "platforms": self.posted_platforms,
            "proof_links": self.proof_links,
            "share_link": SHARE_LINK,
            "share_text": SHARE_TEXT
        }
        
        with open("share_proof.json", "w") as f:
            json.dump(proof_data, f, indent=2)
        
        print(f"\nProof saved to share_proof.json")
        print(f"Total platforms posted: {len(self.posted_platforms)}")
        
        return proof_data

if __name__ == "__main__":
    bot = SocialShareBot()
    result = bot.run()
    
    # Output for RTC reward claim
    print("\n" + "=" * 50)
    print("RTC REWARD CLAIM INFORMATION")
    print("=" * 50)
    print("To claim 3 RTC reward:")
    print(f"1. Wallet: {WALLET}")
    print("2. Submit proof links from above")
    print("3. First 20 unique posts qualify")
    print("4. Reward: 3 RTC (~$0.30 USD)")