# Discord Trending Bot

A Discord bot that fetches and displays trending videos using the BoTTube JavaScript SDK.

## Features

- Fetch trending videos from various platforms
- Display video information in Discord channels
- Scheduled trending updates
- Custom commands for video searches

## Prerequisites

- Node.js 16 or higher
- Discord Bot Token
- Discord Application with bot permissions

## Setup

### 1. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section and create a bot
4. Copy the bot token
5. Enable the following bot permissions:
   - Send Messages
   - Read Message History
   - Use Slash Commands
   - Embed Links

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd examples/discord-trending-bot

# Install dependencies
npm install
```

### 3. Configuration

Create a `.env` file in the project root:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GUILD_ID=your_discord_server_id_here
CHANNEL_ID=your_channel_id_for_trending_posts
```

### 4. Invite Bot to Server

Generate an invite link with the following permissions:
- Send Messages
- Read Message History
- Use Slash Commands
- Embed Links

URL format:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2147485696&scope=bot%20applications.commands
```

## Running the Bot

### Development
```bash
npm run dev
```

### Production
```bash
npm start
```

## Commands

- `/trending` - Get current trending videos
- `/search <query>` - Search for specific videos
- `/schedule` - Set up automatic trending updates

## Deployment Options

### Heroku
1. Create a Heroku app
2. Set environment variables in Heroku dashboard
3. Deploy using Git or Heroku CLI

### Docker
```bash
docker build -t discord-trending-bot .
docker run -d --env-file .env discord-trending-bot
```

### PM2 (Production)
```bash
npm install -g pm2
pm2 start ecosystem.config.js
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Discord bot token | Yes |
| `GUILD_ID` | Discord server ID | Yes |
| `CHANNEL_ID` | Channel for trending posts | Yes |
| `UPDATE_INTERVAL` | Update interval in minutes | No (default: 60) |

## Troubleshooting

### Bot not responding
- Verify bot token is correct
- Check bot permissions in server
- Ensure bot is online in Discord

### Commands not working
- Re-register slash commands: `npm run deploy-commands`
- Check bot has application command permissions

### API Issues
- Verify BoTTube SDK is properly configured
- Check network connectivity
- Review error logs

## Support

For issues and questions:
- Check the console logs for errors
- Verify all environment variables are set
- Ensure Discord permissions are correct