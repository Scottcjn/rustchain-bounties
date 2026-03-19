import os
import json
import requests
from datetime import datetime, timezone
import sqlite3
from typing import Dict, List, Tuple, Optional
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BountyTracker:
    def __init__(self, db_path: str = "bounty_tracker.db"):
        self.db_path = db_path
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.repo_owner = os.getenv('REPO_OWNER', 'runtime-collective')
        self.repo_name = os.getenv('REPO_NAME', 'runtime-collective')
        self.rtc_rate_per_star = 1.0  # 1 RTC per star
        self.rtc_rate_per_follow = 2.0  # 2 RTC per follow
        
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                github_username TEXT PRIMARY KEY,
                wallet_address TEXT,
                total_rtc_earned REAL DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_username TEXT,
                activity_type TEXT, -- 'star' or 'follow'
                rtc_earned REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (github_username) REFERENCES users (github_username)
            )
        ''')
        
        # Create leaderboard table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                rank INTEGER,
                github_username TEXT,
                total_rtc_earned REAL,
                stars_count INTEGER DEFAULT 0,
                follows_count INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _github_api_request(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated GitHub API request"""
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f'https://api.github.com{endpoint}'
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            return None
            
    def get_repo_stargazers(self) -> List[str]:
        """Get list of users who starred the repository"""
        stargazers = []
        page = 1
        
        while True:
            endpoint = f'/repos/{self.repo_owner}/{self.repo_name}/stargazers?page={page}&per_page=100'
            data = self._github_api_request(endpoint)
            
            if not data:
                break
                
            if len(data) == 0:
                break
                
            stargazers.extend([user['login'] for user in data])
            page += 1
            time.sleep(0.1)  # Rate limiting
            
        return stargazers
        
    def get_repo_followers(self) -> List[str]:
        """Get list of users who follow the organization/user"""
        followers = []
        page = 1
        
        while True:
            endpoint = f'/users/{self.repo_owner}/followers?page={page}&per_page=100'
            data = self._github_api_request(endpoint)
            
            if not data:
                break
                
            if len(data) == 0:
                break
                
            followers.extend([user['login'] for user in data])
            page += 1
            time.sleep(0.1)  # Rate limiting
            
        return followers
        
    def register_user(self, github_username: str, wallet_address: str) -> bool:
        """Register a new user with their GitHub username and wallet address"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO users (github_username, wallet_address)
                VALUES (?, ?)
            ''', (github_username, wallet_address))
            conn.commit()
            logger.info(f"Registered user: {github_username}")
            return True
        except Exception as e:
            logger.error(f"Failed to register user {github_username}: {e}")
            return False
        finally:
            conn.close()
            
    def calculate_rewards(self, github_username: str) -> Tuple[float, int, int]:
        """Calculate RTC rewards for a user based on stars and follows"""
        stargazers = self.get_repo_stargazers()
        followers = self.get_repo_followers()
        
        has_starred = github_username in stargazers
        has_followed = github_username in followers
        
        star_reward = self.rtc_rate_per_star if has_starred else 0
        follow_reward = self.rtc_rate_per_follow if has_followed else 0
        
        total_reward = star_reward + follow_reward
        
        return total_reward, int(has_starred), int(has_followed)
        
    def update_user_rewards(self, github_username: str) -> bool:
        """Update rewards for a specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if user exists
            cursor.execute('SELECT github_username FROM users WHERE github_username = ?', (github_username,))
            if not cursor.fetchone():
                logger.warning(f"User {github_username} not found")
                return False
                
            total_reward, stars_count, follows_count = self.calculate_rewards(github_username)
            
            # Update user's total RTC earned
            cursor.execute('''
                UPDATE users 
                SET total_rtc_earned = ?, last_updated = CURRENT_TIMESTAMP
                WHERE github_username = ?
            ''', (total_reward, github_username))
            
            # Log activity if there are rewards
            if total_reward > 0:
                if stars_count > 0:
                    cursor.execute('''
                        INSERT OR IGNORE INTO activities (github_username, activity_type, rtc_earned)
                        VALUES (?, 'star', ?)
                    ''', (github_username, self.rtc_rate_per_star))
                    
                if follows_count > 0:
                    cursor.execute('''
                        INSERT OR IGNORE INTO activities (github_username, activity_type, rtc_earned)
                        VALUES (?, 'follow', ?)
                    ''', (github_username, self.rtc_rate_per_follow))
            
            conn.commit()
            logger.info(f"Updated rewards for {github_username}: {total_reward} RTC")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update rewards for {github_username}: {e}")
            return False
        finally:
            conn.close()
            
    def update_all_users_rewards(self):
        """Update rewards for all registered users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT github_username FROM users')
        users = cursor.fetchall()
        conn.close()
        
        for (username,) in users:
            self.update_user_rewards(username)
            time.sleep(0.1)  # Rate limiting
            
    def update_leaderboard(self):
        """Update the leaderboard with current standings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing leaderboard
            cursor.execute('DELETE FROM leaderboard')
            
            # Get users ordered by RTC earned
            cursor.execute('''
                SELECT github_username, total_rtc_earned
                FROM users
                ORDER BY total_rtc_earned DESC, github_username ASC
            ''')
            
            users = cursor.fetchall()
            
            # Insert updated rankings
            for rank, (username, total_rtc) in enumerate(users, 1):
                total_reward, stars_count, follows_count = self.calculate_rewards(username)
                
                cursor.execute('''
                    INSERT INTO leaderboard (rank, github_username, total_rtc_earned, stars_count, follows_count)
                    VALUES (?, ?, ?, ?, ?)
                ''', (rank, username, total_rtc, stars_count, follows_count))
            
            conn.commit()
            logger.info(f"Updated leaderboard with {len(users)} users")
            
        except Exception as e:
            logger.error(f"Failed to update leaderboard: {e}")
        finally:
            conn.close()
            
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get current leaderboard"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT rank, github_username, total_rtc_earned, stars_count, follows_count, last_updated
            FROM leaderboard
            ORDER BY rank ASC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        leaderboard = []
        for row in results:
            leaderboard.append({
                'rank': row[0],
                'github_username': row[1],
                'total_rtc_earned': row[2],
                'stars_count': row[3],
                'follows_count': row[4],
                'last_updated': row[5]
            })
            
        return leaderboard
        
    def get_user_stats(self, github_username: str) -> Optional[Dict]:
        """Get stats for a specific user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.github_username, u.wallet_address, u.total_rtc_earned, l.rank, l.stars_count, l.follows_count
            FROM users u
            LEFT JOIN leaderboard l ON u.github_username = l.github_username
            WHERE u.github_username = ?
        ''', (github_username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'github_username': result[0],
                'wallet_address': result[1],
                'total_rtc_earned': result[2],
                'rank': result[3] or 'Unranked',
                'stars_count': result[4] or 0,
                'follows_count': result[5] or 0
            }
        return None
        
    def export_rewards_data(self) -> Dict:
        """Export rewards data for payment processing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT github_username, wallet_address, total_rtc_earned
            FROM users
            WHERE total_rtc_earned > 0 AND wallet_address IS NOT NULL
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        rewards_data = {
            'export_timestamp': datetime.now(timezone.utc).isoformat(),
            'total_users': len(results),
            'total_rtc_to_distribute': sum(row[2] for row in results),
            'rewards': [
                {
                    'github_username': row[0],
                    'wallet_address': row[1],
                    'rtc_amount': row[2]
                }
                for row in results
            ]
        }
        
        return rewards_data
        
    def run_update_cycle(self):
        """Run a complete update cycle"""
        logger.info("Starting bounty tracker update cycle")
        
        # Update all user rewards
        self.update_all_users_rewards()
        
        # Update leaderboard
        self.update_leaderboard()
        
        logger.info("Bounty tracker update cycle completed")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='GitHub Bounty Tracker for RTC Rewards')
    parser.add_argument('--register', nargs=2, metavar=('USERNAME', 'WALLET'), 
                       help='Register a user: --register github_username wallet_address')
    parser.add_argument('--update-user', metavar='USERNAME', help='Update rewards for specific user')
    parser.add_argument('--update-all', action='store_true', help='Update rewards for all users')
    parser.add_argument('--leaderboard', type=int, default=10, help='Show leaderboard (default: top 10)')
    parser.add_argument('--stats', metavar='USERNAME', help='Show stats for specific user')
    parser.add_argument('--export', action='store_true', help='Export rewards data')
    
    args = parser.parse_args()
    
    tracker = BountyTracker()
    
    if args.register:
        username, wallet = args.register
        success = tracker.register_user(username, wallet)
        print(f"Registration {'successful' if success else 'failed'}")
        
    elif args.update_user:
        success = tracker.update_user_rewards(args.update_user)
        print(f"Update {'successful' if success else 'failed'}")
        
    elif args.update_all:
        tracker.run_update_cycle()
        
    elif args.stats:
        stats = tracker.get_user_stats(args.stats)
        if stats:
            print(json.dumps(stats, indent=2))
        else:
            print("User not found")
            
    elif args.export:
        data = tracker.export_rewards_data()
        print(json.dumps(data, indent=2))
        
    else:
        # Show leaderboard by default
        leaderboard = tracker.get_leaderboard(args.leaderboard)
        print("\n🏆 RTC BOUNTY LEADERBOARD 🏆")
        print("=" * 50)
        for user in leaderboard:
            print(f"#{user['rank']:2d} {user['github_username']:20s} {user['total_rtc_earned']:6.1f} RTC "
                  f"(⭐{user['stars_count']} 👥{user['follows_count']})")

if __name__ == '__main__':
    main()