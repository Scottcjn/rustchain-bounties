#!/usr/bin/env python3
"""
Miner Status Notification System
================================
Monitors RustChain miners and sends alerts when they go offline.

Supports: Discord, Email, Telegram, Webhook
Features: Status change detection, streak warnings, rate limiting
"""

import json
import time
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
import requests

# Optional imports for notification channels
try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

try:
    import tweepy
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

# Configuration
CONFIG_FILE = Path(__file__).parent / "config.json"
STATE_FILE = Path(__file__).parent / "state.json"
LOG_FILE = Path(__file__).parent / "miner_monitor.log"

# Constants
EPOCH_MINUTES = 10
MISSED_EPOCHS_THRESHOLD = 2  # 20 minutes offline
ALERT_COOLDOWN_HOURS = 1
STREAK_WARNING_HOURS = 2

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MinerState:
    """Tracks the state of a single miner"""
    miner_id: str
    last_seen: float = 0.0
    last_attest: float = 0.0
    is_online: bool = True
    last_alert_sent: float = 0.0
    alert_count: int = 0
    streak_days: int = 0
    streak_warned: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MinerState':
        return cls(**data)


@dataclass
class NotificationConfig:
    """Notification channel configuration"""
    discord_webhook: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    email_smtp_server: str = ""
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_from: str = ""
    email_to: List[str] = field(default_factory=list)
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    webhook_url: str = ""
    enabled_channels: List[str] = field(default_factory=lambda: ["discord", "telegram"])
    
    @classmethod
    def load(cls, path: Path) -> 'NotificationConfig':
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def save(self, path: Path):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)


class MinerMonitor:
    """Main monitoring class"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.miners: Dict[str, MinerState] = {}
        self.api_base = "https://rustchain.org/api"
        self.load_state()
    
    def load_state(self):
        """Load previous state from disk"""
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                data = json.load(f)
                self.miners = {
                    k: MinerState.from_dict(v) for k, v in data.get('miners', {}).items()
                }
                logger.info(f"Loaded state for {len(self.miners)} miners")
    
    def save_state(self):
        """Save current state to disk"""
        data = {
            'miners': {k: v.to_dict() for k, v in self.miners.items()},
            'last_update': time.time()
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def fetch_miners(self) -> List[Dict]:
        """Fetch current miner data from API"""
        try:
            response = requests.get(f"{self.api_base}/miners", timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('miners', []) if isinstance(data, dict) else data
        except Exception as e:
            logger.error(f"Failed to fetch miners: {e}")
            return []
    
    def fetch_streak(self, miner_id: str) -> int:
        """Fetch miner streak data"""
        try:
            response = requests.get(f"{self.api_base}/miner/{miner_id}/streak", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('streak_days', 0) if isinstance(data, dict) else 0
        except Exception as e:
            logger.debug(f"Failed to fetch streak for {miner_id}: {e}")
        return 0
    
    def check_miner_status(self, miner_data: Dict) -> MinerState:
        """Check if a miner is online or offline"""
        miner_id = miner_data.get('miner', '')
        last_attest = miner_data.get('last_attest', 0)
        current_time = time.time()
        
        # Calculate time since last attestation
        time_since_attest = current_time - last_attest
        epochs_missed = time_since_attest / (EPOCH_MINUTES * 60)
        
        # Get or create miner state
        if miner_id not in self.miners:
            self.miners[miner_id] = MinerState(
                miner_id=miner_id,
                last_seen=current_time,
                last_attest=last_attest,
                is_online=True
            )
        
        state = self.miners[miner_id]
        was_online = state.is_online
        
        # Update state
        state.last_attest = last_attest
        
        # Determine if miner is offline (missed 2+ epochs)
        is_offline = epochs_missed >= MISSED_EPOCHS_THRESHOLD
        
        if is_offline:
            state.is_online = False
            # Check if we should send alert
            time_since_alert = current_time - state.last_alert_sent
            if time_since_alert > (ALERT_COOLDOWN_HOURS * 3600):
                self.send_offline_alert(state, epochs_missed)
                state.last_alert_sent = current_time
                state.alert_count += 1
        else:
            # Miner is back online
            if not was_online:
                self.send_back_online_alert(state)
            state.is_online = True
            state.last_seen = current_time
        
        # Check streak warnings
        if state.is_online and not state.streak_warned:
            streak_days = self.fetch_streak(miner_id)
            state.streak_days = streak_days
            if streak_days > 0:
                # Check if streak is about to expire (within 2 hours)
                # Streak grace period is 26 hours, warn 2 hours before
                time_to_grace_end = (26 * 3600) - time_since_attest
                if time_to_grace_end < (2 * 3600):
                    self.send_streak_warning(state, time_to_grace_end)
                    state.streak_warned = True
        
        return state
    
    def send_offline_alert(self, state: MinerState, epochs_missed: float):
        """Send alert when miner goes offline"""
        message = f"""
🚨 **MINER OFFLINE ALERT** 🚨

**Miner ID**: `{state.miner_id}`
**Status**: OFFLINE
**Epochs Missed**: {epochs_missed:.1f}
**Last Seen**: {datetime.fromtimestamp(state.last_attest).strftime('%Y-%m-%d %H:%M:%S')}
**Alert Count**: {state.alert_count}

Your miner has been offline for {epochs_missed * EPOCH_MINUTES:.0f} minutes.
Please check your mining setup to avoid losing your streak!
        """.strip()
        
        self.send_notification("Miner Offline Alert", message, priority="high")
    
    def send_back_online_alert(self, state: MinerState):
        """Send alert when miner comes back online"""
        message = f"""
✅ **MINER BACK ONLINE** ✅

**Miner ID**: `{state.miner_id}`
**Status**: ONLINE
**Recovery Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Your miner has recovered and is now submitting attestations.
        """.strip()
        
        self.send_notification("Miner Back Online", message, priority="normal")
    
    def send_streak_warning(self, state: MinerState, time_remaining: float):
        """Send warning about streak expiration"""
        hours_remaining = time_remaining / 3600
        message = f"""
⚠️ **STREAK WARNING** ⚠️

**Miner ID**: `{state.miner_id}`
**Current Streak**: {state.streak_days} days
**Time Remaining**: {hours_remaining:.1f} hours

Your mining streak will reset in {hours_remaining:.1f} hours if no attestation is submitted.
Submit an attestation soon to preserve your {state.streak_days}-day streak!
        """.strip()
        
        self.send_notification("Streak Warning", message, priority="high")
    
    def send_notification(self, title: str, message: str, priority: str = "normal"):
        """Send notification through all enabled channels"""
        for channel in self.config.enabled_channels:
            try:
                if channel == "discord" and self.config.discord_webhook:
                    self._send_discord(title, message, priority)
                elif channel == "telegram" and self.config.telegram_bot_token:
                    self._send_telegram(title, message, priority)
                elif channel == "email" and self.config.email_smtp_server:
                    self._send_email(title, message, priority)
                elif channel == "webhook" and self.config.webhook_url:
                    self._send_webhook(title, message, priority)
            except Exception as e:
                logger.error(f"Failed to send {channel} notification: {e}")
    
    def _send_discord(self, title: str, message: str, priority: str):
        """Send Discord webhook notification"""
        color = 0xff0000 if priority == "high" else 0xffa500
        payload = {
            "embeds": [{
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }]
        }
        response = requests.post(self.config.discord_webhook, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Discord notification sent")
    
    def _send_telegram(self, title: str, message: str, priority: str):
        """Send Telegram notification"""
        url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.config.telegram_chat_id,
            "text": f"*{title}*\n\n{message}",
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Telegram notification sent")
    
    def _send_email(self, title: str, message: str, priority: str):
        """Send email notification"""
        if not EMAIL_AVAILABLE:
            logger.warning("Email library not available")
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.config.email_from
        msg['To'] = ', '.join(self.config.email_to)
        msg['Subject'] = f"[RustChain] {title}"
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(self.config.email_smtp_server, self.config.email_smtp_port)
        server.starttls()
        server.login(self.config.email_username, self.config.email_password)
        server.send_message(msg)
        server.quit()
        logger.info("Email notification sent")
    
    def _send_webhook(self, title: str, message: str, priority: str):
        """Send generic webhook notification"""
        payload = {
            "title": title,
            "message": message,
            "priority": priority,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = requests.post(self.config.webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Webhook notification sent")
    
    def run_once(self):
        """Run a single monitoring cycle"""
        logger.info("Starting monitoring cycle...")
        miners_data = self.fetch_miners()
        
        if not miners_data:
            logger.warning("No miner data received")
            return
        
        online_count = 0
        offline_count = 0
        
        for miner_data in miners_data:
            state = self.check_miner_status(miner_data)
            if state.is_online:
                online_count += 1
            else:
                offline_count += 1
        
        self.save_state()
        logger.info(f"Cycle complete: {online_count} online, {offline_count} offline")
    
    def run_continuous(self, interval_minutes: int = 10):
        """Run continuous monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval_minutes}min)")
        while True:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
            
            time.sleep(interval_minutes * 60)


def create_config_template():
    """Create a configuration template file"""
    config = NotificationConfig()
    config.save(CONFIG_FILE)
    print(f"Configuration template created: {CONFIG_FILE}")
    print("Edit this file to add your notification channel credentials")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--init":
            create_config_template()
        elif sys.argv[1] == "--once":
            config = NotificationConfig.load(CONFIG_FILE)
            monitor = MinerMonitor(config)
            monitor.run_once()
        elif sys.argv[1] == "--help":
            print("""
Miner Status Notification System
================================

Usage:
  python miner_monitor.py --init     Create config template
  python miner_monitor.py --once     Run single monitoring cycle
  python miner_monitor.py            Run continuous monitoring

Configuration:
  Edit config.json to set up notification channels

Supported Channels:
  - Discord webhooks
  - Telegram bot
  - Email (SMTP)
  - Generic webhooks
            """)
    else:
        config = NotificationConfig.load(CONFIG_FILE)
        monitor = MinerMonitor(config)
        monitor.run_continuous()
