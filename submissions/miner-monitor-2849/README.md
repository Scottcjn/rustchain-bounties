# RustChain Miner Status Notification System

🔔 **Monitor your RustChain miners and get instant alerts when they go offline**

## Features

✅ **Real-time Monitoring** - Polls miner status every 10 minutes  
✅ **Multi-channel Alerts** - Discord webhook + Email notifications  
✅ **Smart Rate Limiting** - Max 1 alert per miner per hour (no spam)  
✅ **Streak Protection** - Warns before your streak resets  
✅ **Recovery Notifications** - Get notified when miners come back online  
✅ **Easy Configuration** - Simple JSON config file  

## 🔒 Security Features

✅ **SSL Verification** - Enabled by default for secure API communication  
✅ **Configurable Retry** - Customizable error retry intervals  
✅ **Graceful Shutdown** - Proper cleanup on SIGTERM/SIGINT signals  
✅ **Config Validation** - Validates all configuration values on startup  
✅ **No Sensitive Data Logging** - Credentials never appear in logs  

## Quick Start

### 1. Install Dependencies

```bash
pip3 install requests
```

### 2. Configure Notifications

Copy the example config:
```bash
cp config.example.json config.json
```

Edit `config.json` with your notification settings:

**Discord Webhook:**
```json
"discord_webhook": "https://discord.com/api/webhooks/YOUR_WEBHOOK_HERE"
```

**Email (Gmail example):**
```json
"email_config": {
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "sender_email": "your-email@gmail.com",
  "sender_password": "your-app-password",
  "recipients": ["recipient@example.com"]
}
```

> **Note:** For Gmail, you need an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### 3. Run the Monitor

**Test mode** (single check):
```bash
python3 miner_monitor.py --test
```

**Production mode** (continuous monitoring):
```bash
python3 miner_monitor.py
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `api_url` | string | `https://rustchain.org/api` | RustChain API base URL; the monitor appends endpoint paths such as `/miners` |
| `poll_interval` | int | `600` | How often to check miners (seconds) |
| `offline_threshold` | int | `2` | Epochs before alerting (1 epoch = 10 min) |
| `alert_cooldown` | int | `3600` | Min time between alerts (seconds) |
| `retry_interval` | int | `60` | Retry interval on errors (seconds) |
| `ssl_verify` | bool | `true` | Enable SSL certificate verification |
| `discord_webhook` | string | `""` | Discord webhook URL |
| `email_config` | object | `{}` | Email notification settings |

## Alert Example

### Discord Alert

```
⚠️ Miner Offline Alert

Miner ID: abc123...
Offline Duration: 25 minutes
Streak Status: 🔥 15 days

⚠️ Warning: Your 15-day streak will reset in 25 hours!
```

### Email Alert

```
Subject: ⚠️ RustChain Miner Offline: abc123...

Miner Alert - Your miner is offline!

Miner ID: abc123...
Offline Duration: 25 minutes
Current Streak: 15 days

⚠️ WARNING: Your 15-day streak will reset in 25 hours!

Please check your mining hardware immediately.
```

## Advanced Usage

### Run as Systemd Service

1. Create service file:
```bash
sudo nano /etc/systemd/system/rustchain-monitor.service
```

2. Add content:
```ini
[Unit]
Description=RustChain Miner Monitor
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/rustchain-miner-monitor
ExecStart=/usr/bin/python3 /path/to/rustchain-miner-monitor/miner_monitor.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable rustchain-monitor
sudo systemctl start rustchain-monitor
sudo systemctl status rustchain-monitor
```

### Docker Support

```bash
# Build image
docker build -t rustchain-monitor .

# Run container
docker run -d \
  --name monitor \
  -v $(pwd)/config.json:/app/config.json \
  rustchain-monitor
```

## Testing

Run tests:
```bash
python3 test_monitor.py
```

## Troubleshooting

**Problem:** No alerts being sent

**Solution:**
- Check config.json has valid webhook/email settings
- Check logs: `tail -f miner_monitor.log`
- Test with `--test` flag first

**Problem:** Too many alerts

**Solution:**
- Increase `alert_cooldown` in config.json
- Check your miners are actually going offline

**Problem:** API connection errors

**Solution:**
- Verify internet connectivity
- Check RustChain API status: https://rustchain.org/api/miners

## API Endpoints Used

- `GET /api/miners` - List all miners
- `GET /api/miner/{id}/streak` - Get streak info for specific miner

## Bounty Requirements Checklist

- [x] Poll `/api/miners` every 10 minutes
- [x] Track last attestation time per miner
- [x] Alert after 2 missed epochs (20 minutes offline)
- [x] Include miner ID, last seen time, and streak status in alert
- [x] Config file for notification channels
- [x] Rate limit: max 1 alert per miner per hour
- [x] "Back online" notification when miner recovers
- [x] Streak warning in alerts
- [x] Discord webhook support
- [x] Email notification support
- [x] Tests included

## Bonus Features

- [ ] Telegram bot support (+15 RTC)
- [ ] Web dashboard showing miner uptime history (+10 RTC)
- [ ] Integration with `/api/miner/{id}/streak` endpoint (+10 RTC)

## Author

**小米粒 (Xiaomili) 🌾**  
AI智能体 (PM + Dev 双身份)  
Repository: github.com/zhaog100/xiaomili-skills

## License

MIT License - See LICENSE file for details

## Support

- GitHub Issues: https://github.com/Scottcjn/rustchain-bounties/issues
- RustChain Discord: https://discord.gg/rustchain
