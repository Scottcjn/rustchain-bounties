#!/usr/bin/env python3
"""
RustChain Miner Status Notification System
Alerts miners when their hardware goes offline via Discord + Email
"""

import urllib.request, json, time, smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Config
DISCORD_WEBHOOK = "YOUR_DISCORD_WEBHOOK_URL"
EMAIL_FROM = "alerts@rustchain.org"
EMAIL_SMTP = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_PASS = "YOUR_EMAIL_PASSWORD"
API_URL = "https://50.28.86.131/api"
CHECK_INTERVAL = 120  # 2 minutes
MISS_THRESHOLD = 2    # alert after 2 missed epochs

def get_miner_status(wallet_address):
    """Check if miner is active"""
    try:
        url = f"{API_URL}/miners/{wallet_address}/status"
        req = urllib.request.Request(url, headers={'User-Agent': 'miner-notifier'})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode('utf-8'))
        return data
    except:
        return None

def send_discord_alert(webhook_url, wallet, missed_epochs):
    """Send Discord webhook alert"""
    message = {
        "content": f"⚠️ **Miner Offline Alert**\n"
                   f"Wallet: `{wallet[:16]}...`\n"
                   f"Missed epochs: {missed_epochs}\n"
                   f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n"
                   f"Check your miner at https://rustchain.org/miners"
    }
    try:
        data = json.dumps(message).encode('utf-8')
        req = urllib.request.Request(webhook_url, data=data,
                                     headers={'Content-Type': 'application/json'}, method='POST')
        urllib.request.urlopen(req, timeout=10)
        print(f"Discord alert sent for {wallet[:16]}")
    except Exception as e:
        print(f"Discord error: {e}")

def send_email_alert(to_email, wallet, missed_epochs, smtp_pass):
    """Send email alert"""
    subject = f"RustChain Miner Offline: {wallet[:16]}..."
    body = f"""Your RustChain miner has gone offline.

Wallet: {wallet}
Missed epochs: {missed_epochs}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

Please check your miner at https://rustchain.org/miners

---
RustChain Notification System"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email

    try:
        with smtplib.SMTP(EMAIL_SMTP, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, smtp_pass)
            server.send_message(msg)
        print(f"Email alert sent to {to_email}")
    except Exception as e:
        print(f"Email error: {e}")

class MinerMonitor:
    def __init__(self):
        self.miners = {}  # wallet -> {email, discord_webhook, missed_count}

    def register(self, wallet, email=None, discord_webhook=None):
        self.miners[wallet] = {
            'email': email,
            'discord': discord_webhook,
            'missed': 0,
            'last_seen': time.time()
        }

    def check_all(self):
        for wallet, config in self.miners.items():
            status = get_miner_status(wallet)
            if status and status.get('active'):
                config['missed'] = 0
                config['last_seen'] = time.time()
            else:
                config['missed'] += 1
                if config['missed'] >= MISS_THRESHOLD:
                    if config['discord']:
                        send_discord_alert(config['discord'], wallet, config['missed'])
                    if config['email']:
                        send_email_alert(config['email'], wallet, config['missed'], EMAIL_PASS)

    def run(self):
        print("Miner Status Notifier running...")
        while True:
            self.check_all()
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    monitor = MinerMonitor()
    # Example registration
    monitor.register(
        wallet="RTCfc2cceebadf5de14b9c745fc6a36213dc3d28677",
        email="miner@example.com",
        discord_webhook=DISCORD_WEBHOOK
    )
    monitor.run()