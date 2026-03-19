import os
import requests
import time
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BountySubmission:
    user_id: str
    github_username: str
    wallet_address: str
    submission_time: datetime
    verified: bool = False
    reward_amount: float = 0.0

class GitHubVerifier:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.base_url = 'https://api.github.com'
    
    def verify_star(self, username: str, repo_owner: str, repo_name: str) -> bool:
        """Verify if user has starred the specified repository"""
        try:
            url = f"{self.base_url}/user/starred/{repo_owner}/{repo_name}"
            response = requests.get(url, headers=self.headers, auth=(username, ''))
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error verifying star for {username}: {e}")
            return False
    
    def verify_follow(self, username: str, target_user: str) -> bool:
        """Verify if user is following the target user"""
        try:
            url = f"{self.base_url}/user/following/{target_user}"
            response = requests.get(url, headers=self.headers, auth=(username, ''))
            return response.status_code == 204
        except Exception as e:
            logger.error(f"Error verifying follow for {username}: {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """Get basic user information"""
        try:
            url = f"{self.base_url}/users/{username}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Error getting user info for {username}: {e}")
            return None

class RTCRewardCalculator:
    def __init__(self):
        self.star_reward = 10.0  # RTC tokens per star
        self.follow_reward = 25.0  # RTC tokens per follow
        self.bonus_multiplier = 1.5  # Bonus for completing both actions
    
    def calculate_reward(self, has_starred: bool, has_followed: bool) -> float:
        """Calculate RTC reward based on actions completed"""
        reward = 0.0
        
        if has_starred:
            reward += self.star_reward
        
        if has_followed:
            reward += self.follow_reward
        
        # Apply bonus if both actions completed
        if has_starred and has_followed:
            reward *= self.bonus_multiplier
        
        return reward

class BountyProcessor:
    def __init__(self, github_token: str, target_repo: str, target_user: str):
        self.github_verifier = GitHubVerifier(github_token)
        self.reward_calculator = RTCRewardCalculator()
        self.target_repo = target_repo  # Format: "owner/repo"
        self.target_user = target_user
        self.submissions = []
        self.processed_users = set()
        self.data_file = 'bounty_submissions.json'
        
        # Load existing data
        self.load_submissions()
    
    def load_submissions(self):
        """Load existing submissions from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        submission = BountySubmission(
                            user_id=item['user_id'],
                            github_username=item['github_username'],
                            wallet_address=item['wallet_address'],
                            submission_time=datetime.fromisoformat(item['submission_time']),
                            verified=item.get('verified', False),
                            reward_amount=item.get('reward_amount', 0.0)
                        )
                        self.submissions.append(submission)
                        if submission.verified:
                            self.processed_users.add(submission.github_username.lower())
        except Exception as e:
            logger.error(f"Error loading submissions: {e}")
    
    def save_submissions(self):
        """Save submissions to file"""
        try:
            data = []
            for submission in self.submissions:
                data.append({
                    'user_id': submission.user_id,
                    'github_username': submission.github_username,
                    'wallet_address': submission.wallet_address,
                    'submission_time': submission.submission_time.isoformat(),
                    'verified': submission.verified,
                    'reward_amount': submission.reward_amount
                })
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving submissions: {e}")
    
    def submit_bounty(self, user_id: str, github_username: str, wallet_address: str) -> Dict:
        """Submit a new bounty claim"""
        # Check if user already processed
        if github_username.lower() in self.processed_users:
            return {
                'success': False,
                'message': 'User has already been processed for this bounty'
            }
        
        # Validate GitHub username exists
        user_info = self.github_verifier.get_user_info(github_username)
        if not user_info:
            return {
                'success': False,
                'message': 'Invalid GitHub username'
            }
        
        # Create submission
        submission = BountySubmission(
            user_id=user_id,
            github_username=github_username,
            wallet_address=wallet_address,
            submission_time=datetime.now()
        )
        
        self.submissions.append(submission)
        self.save_submissions()
        
        return {
            'success': True,
            'message': 'Bounty submission received. Verification will be processed shortly.',
            'submission_id': len(self.submissions) - 1
        }
    
    def process_pending_submissions(self):
        """Process all unverified submissions"""
        repo_owner, repo_name = self.target_repo.split('/')
        
        for submission in self.submissions:
            if not submission.verified and submission.github_username.lower() not in self.processed_users:
                logger.info(f"Processing submission for {submission.github_username}")
                
                # Verify star and follow
                has_starred = self.github_verifier.verify_star(
                    submission.github_username, repo_owner, repo_name
                )
                has_followed = self.github_verifier.verify_follow(
                    submission.github_username, self.target_user
                )
                
                # Calculate reward
                reward_amount = self.reward_calculator.calculate_reward(has_starred, has_followed)
                
                if reward_amount > 0:
                    submission.verified = True
                    submission.reward_amount = reward_amount
                    self.processed_users.add(submission.github_username.lower())
                    
                    logger.info(f"Verified {submission.github_username}: {reward_amount} RTC")
                    
                    # Here you would integrate with RTC token distribution system
                    self.distribute_reward(submission)
                else:
                    logger.info(f"No qualifying actions found for {submission.github_username}")
                
                # Rate limiting
                time.sleep(1)
        
        self.save_submissions()
    
    def distribute_reward(self, submission: BountySubmission):
        """Distribute RTC tokens to user wallet"""
        # This is where you would integrate with the actual RTC token smart contract
        # For now, just log the action
        logger.info(f"REWARD DISTRIBUTION:")
        logger.info(f"  User: {submission.github_username}")
        logger.info(f"  Wallet: {submission.wallet_address}")
        logger.info(f"  Amount: {submission.reward_amount} RTC")
        
        # TODO: Implement actual token distribution
        # Example:
        # rtc_contract.transfer(submission.wallet_address, submission.reward_amount)
    
    def get_stats(self) -> Dict:
        """Get bounty processing statistics"""
        total_submissions = len(self.submissions)
        verified_submissions = sum(1 for s in self.submissions if s.verified)
        total_rewards = sum(s.reward_amount for s in self.submissions if s.verified)
        
        return {
            'total_submissions': total_submissions,
            'verified_submissions': verified_submissions,
            'pending_submissions': total_submissions - verified_submissions,
            'total_rewards_distributed': total_rewards,
            'unique_users': len(self.processed_users)
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get top reward earners"""
        verified_submissions = [s for s in self.submissions if s.verified]
        sorted_submissions = sorted(verified_submissions, key=lambda x: x.reward_amount, reverse=True)
        
        leaderboard = []
        for i, submission in enumerate(sorted_submissions[:limit]):
            leaderboard.append({
                'rank': i + 1,
                'github_username': submission.github_username,
                'reward_amount': submission.reward_amount,
                'submission_time': submission.submission_time.isoformat()
            })
        
        return leaderboard

def main():
    """Main execution function for testing"""
    # Configuration
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')
    TARGET_REPO = "YourOrg/YourRepo"  # Update with actual repo
    TARGET_USER = "YourGitHubUsername"  # Update with actual username
    
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN environment variable is required")
        return
    
    # Initialize processor
    processor = BountyProcessor(GITHUB_TOKEN, TARGET_REPO, TARGET_USER)
    
    # Process pending submissions
    processor.process_pending_submissions()
    
    # Print stats
    stats = processor.get_stats()
    logger.info(f"Bounty Processing Stats: {stats}")
    
    # Print leaderboard
    leaderboard = processor.get_leaderboard()
    logger.info("Top Reward Earners:")
    for entry in leaderboard:
        logger.info(f"  {entry['rank']}. {entry['github_username']}: {entry['reward_amount']} RTC")

if __name__ == "__main__":
    main()