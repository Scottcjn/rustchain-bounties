#!/usr/bin/env python3
"""
RustChain Miner Status Notification System
Monitors miner status and sends alerts when miners go offline

Author: 小米粒 (Xiaomili) 🌾
Repository: github.com/zhaog100/xiaomili-skills
License: MIT
"""

import requests
import time
import json
import smtplib
import signal
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import logging
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('miner_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MinerStatus:
    """Miner status information"""
    miner_id: str
    last_attestation: datetime
    streak_days: int
    is_online: bool
    last_alert_time: Optional[datetime] = None

class MinerMonitor:
    """Main monitoring class"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.validate_config()
        self.miners: Dict[str, MinerStatus] = {}
        self.offline_miners: Set[str] = set()
        self.alert_cooldown: Dict[str, datetime] = {}
        self.shutdown_event = threading.Event()
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        logger.info("Signal handlers configured for graceful shutdown")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()
        
    def load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                "api_url": "https://rustchain.org/api",
                "poll_interval": 600,  # 10 minutes
                "offline_threshold": 2,  # 2 epochs (20 minutes)
                "alert_cooldown": 3600,  # 1 hour
                "retry_interval": 60,  # Retry interval on errors
                "ssl_verify": True,  # Enable SSL verification by default
                "discord_webhook": "",
                "email_config": {
                    "smtp_server": "",
                    "smtp_port": 587,
                    "sender_email": "",
                    "sender_password": "",
                    "recipients": []
                }
            }
    
    def validate_config(self):
        """Validate configuration values"""
        # Validate poll_interval
        if self.config.get('poll_interval', 600) <= 0:
            logger.warning("Invalid poll_interval, using default 600s")
            self.config['poll_interval'] = 600
        
        # Validate offline_threshold
        if self.config.get('offline_threshold', 2) <= 0:
            logger.warning("Invalid offline_threshold, using default 2")
            self.config['offline_threshold'] = 2
        
        # Validate alert_cooldown
        if self.config.get('alert_cooldown', 3600) <= 0:
            logger.warning("Invalid alert_cooldown, using default 3600s")
            self.config['alert_cooldown'] = 3600
        
        # Validate retry_interval
        if self.config.get('retry_interval', 60) <= 0:
            logger.warning("Invalid retry_interval, using default 60s")
            self.config['retry_interval'] = 60
        
        logger.info("Configuration validated successfully")
    
    def fetch_miners(self) -> List[dict]:
        """Fetch miner data from API"""
        ssl_verify = self.config.get('ssl_verify', True)
        
        if not ssl_verify:
            logger.warning("⚠️ SSL verification disabled - NOT RECOMMENDED for production!")
        
        try:
            response = requests.get(
                f"{self.config['api_url']}/miners",
                timeout=30,
                verify=ssl_verify
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch miners: {e}")
            return []
    
    def fetch_streak(self, miner_id: str) -> dict:
        """Fetch streak data for a specific miner"""
        ssl_verify = self.config.get('ssl_verify', True)
        
        try:
            response = requests.get(
                f"{self.config['api_url']}/miner/{miner_id}/streak",
                timeout=30,
                verify=ssl_verify
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to fetch streak for {miner_id}: {e}")
            return {}
    
    def update_miner_status(self, miner_data: dict):
        """Update status for a single miner"""
        miner_id = miner_data.get('id')
        last_attestation = datetime.fromisoformat(
            miner_data.get('last_attestation', datetime.now().isoformat())
        )
        
        # Check if offline (2 epochs = 20 minutes)
        time_since_attestation = datetime.now() - last_attestation
        is_online = time_since_attestation < timedelta(
            minutes=self.config['offline_threshold'] * 10
        )
        
        # Get streak info
        streak_data = self.fetch_streak(miner_id)
        streak_days = streak_data.get('streak_days', 0)
        
        # Update or create miner status
        if miner_id in self.miners:
            was_online = self.miners[miner_id].is_online
            self.miners[miner_id].last_attestation = last_attestation
            self.miners[miner_id].streak_days = streak_days
            self.miners[miner_id].is_online = is_online
            
            # Check for status change
            if was_online and not is_online:
                self.offline_miners.add(miner_id)
                logger.warning(f"Miner {miner_id} went offline (streak: {streak_days} days)")
            elif not was_online and is_online:
                self.offline_miners.discard(miner_id)
                logger.info(f"Miner {miner_id} is back online!")
                self.send_recovery_alert(miner_id, streak_days)
        else:
            self.miners[miner_id] = MinerStatus(
                miner_id=miner_id,
                last_attestation=last_attestation,
                streak_days=streak_days,
                is_online=is_online
            )
    
    def should_send_alert(self, miner_id: str) -> bool:
        """Check if alert should be sent (rate limiting)"""
        if miner_id not in self.alert_cooldown:
            return True
        
        time_since_last_alert = datetime.now() - self.alert_cooldown[miner_id]
        return time_since_last_alert > timedelta(seconds=self.config['alert_cooldown'])
    
    def send_discord_alert(self, miner_id: str, streak_days: int, offline_duration: int):
        """Send alert via Discord webhook"""
        if not self.config.get('discord_webhook'):
            logger.warning("Discord webhook not configured")
            return False
        
        embed = {
            "title": "⚠️ Miner Offline Alert",
            "color": 15158332,  # Red
            "fields": [
                {
                    "name": "Miner ID",
                    "value": miner_id,
                    "inline": True
                },
                {
                    "name": "Offline Duration",
                    "value": f"{offline_duration} minutes",
                    "inline": True
                },
                {
                    "name": "Streak Status",
                    "value": f"🔥 {streak_days} days",
                    "inline": True
                },
                {
                    "name": "⚠️ Warning",
                    "value": f"Your {streak_days}-day streak will reset in {26 - offline_duration//60} hours!",
                    "inline": False
                }
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        payload = {"embeds": [embed]}
        
        try:
            response = requests.post(
                self.config['discord_webhook'],
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Discord alert sent for miner {miner_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send Discord alert: {e}")
            return False
    
    def send_email_alert(self, miner_id: str, streak_days: int, offline_duration: int):
        """Send alert via email"""
        email_config = self.config.get('email_config', {})
        
        if not email_config.get('smtp_server'):
            logger.warning("Email not configured")
            return False
        
        recipients = email_config.get('recipients', [])
        if not recipients:
            logger.warning("No email recipients configured")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = email_config['sender_email']
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"⚠️ RustChain Miner Offline: {miner_id}"
        
        body = f"""
Miner Alert - Your miner is offline!

Miner ID: {miner_id}
Offline Duration: {offline_duration} minutes
Current Streak: {streak_days} days

⚠️ WARNING: Your {streak_days}-day streak will reset in {26 - offline_duration//60} hours!

Last Seen: {self.miners[miner_id].last_attestation}

Please check your mining hardware immediately to preserve your streak.

---
RustChain Mining Monitor
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(
                email_config['smtp_server'],
                email_config['smtp_port']
            ) as server:
                server.starttls()
                server.login(
                    email_config['sender_email'],
                    email_config['sender_password']
                )
                server.send_message(msg)
            
            logger.info(f"Email alert sent for miner {miner_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
            return False
    
    def send_recovery_alert(self, miner_id: str, streak_days: int):
        """Send recovery notification"""
        if not self.should_send_alert(miner_id):
            return
        
        # Send Discord notification
        if self.config.get('discord_webhook'):
            embed = {
                "title": "✅ Miner Back Online",
                "color": 3066993,  # Green
                "fields": [
                    {
                        "name": "Miner ID",
                        "value": miner_id,
                        "inline": True
                    },
                    {
                        "name": "Streak Preserved",
                        "value": f"🔥 {streak_days} days",
                        "inline": True
                    }
                ],
                "timestamp": datetime.now().isoformat()
            }
            
            requests.post(
                self.config['discord_webhook'],
                json={"embeds": [embed]},
                timeout=10
            )
        
        self.alert_cooldown[miner_id] = datetime.now()
    
    def send_offline_alert(self, miner_id: str):
        """Send offline alert through configured channels"""
        if not self.should_send_alert(miner_id):
            logger.info(f"Alert for {miner_id} skipped (cooldown)")
            return
        
        miner = self.miners[miner_id]
        offline_duration = int((datetime.now() - miner.last_attestation).total_seconds() / 60)
        
        # Send alerts
        discord_sent = self.send_discord_alert(miner_id, miner.streak_days, offline_duration)
        email_sent = self.send_email_alert(miner_id, miner.streak_days, offline_duration)
        
        if discord_sent or email_sent:
            self.alert_cooldown[miner_id] = datetime.now()
        elif not discord_sent and not email_sent:
            logger.error(f"All alert channels failed for miner {miner_id}")
    
    def monitor(self):
        """Main monitoring loop with graceful shutdown support"""
        logger.info("Starting RustChain Miner Monitor...")
        
        while not self.shutdown_event.is_set():
            try:
                # Fetch all miners
                miners_data = self.fetch_miners()
                
                if not miners_data:
                    logger.warning("No miners data received, retrying...")
                    # Use configurable retry interval
                    self.shutdown_event.wait(self.config.get('retry_interval', 60))
                    continue
                
                # Update status for each miner
                for miner_data in miners_data:
                    if self.shutdown_event.is_set():
                        break
                    self.update_miner_status(miner_data)
                
                # Send alerts for offline miners
                for miner_id in list(self.offline_miners):
                    if self.shutdown_event.is_set():
                        break
                    self.send_offline_alert(miner_id)
                
                logger.info(
                    f"Monitoring {len(self.miners)} miners, "
                    f"{len(self.offline_miners)} offline"
                )
                
                # Wait for next poll (interruptible by shutdown signal)
                self.shutdown_event.wait(self.config['poll_interval'])
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                # Use configurable retry interval
                self.shutdown_event.wait(self.config.get('retry_interval', 60))
        
        logger.info("Monitor shutdown complete")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RustChain Miner Monitor")
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to config file'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (single check)'
    )
    
    args = parser.parse_args()
    
    monitor = MinerMonitor(args.config)
    
    if args.test:
        # Test mode: single check
        miners = monitor.fetch_miners()
        print(f"Found {len(miners)} miners")
        for miner in miners[:5]:  # Show first 5
            monitor.update_miner_status(miner)
            status = monitor.miners[miner['id']]
            print(f"  {status.miner_id}: {'✅ Online' if status.is_online else '❌ Offline'} (Streak: {status.streak_days} days)")
    else:
        # Production mode: continuous monitoring
        monitor.monitor()

if __name__ == "__main__":
    main()
