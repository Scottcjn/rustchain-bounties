# Configuration for Silicon Obituary system

# Database configuration
DATABASE_URL = "postgresql://user:password@localhost/rustchain"

# BoTTube integration
BOT_TUBE_API_KEY = "your_bot_tube_api_key"
BOT_TUBE_UPLOAD_URL = "https://api.bottube.com/v1/upload"

# Discord notification
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_id/your_webhook_token"

# Eulogy generation
EULOGY_TEMPLATES = [
    "Here lies {model}, a {type}. It attested for {epochs} epochs and earned {rtc} RTC.",
    "{model} served faithfully for {years} years, earning {rtc} RTC in its lifetime.",
    "Rest in silicon, {model}. You served for {epochs} epochs and earned {rtc} RTC."
]