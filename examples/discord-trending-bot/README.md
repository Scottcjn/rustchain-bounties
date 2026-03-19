# Discord Trending Bot

A Discord bot that automatically posts trending videos from BoTTube to your Discord server using the BoTTube JavaScript SDK.

## Features

- Automatically fetches trending videos from BoTTube
- Posts videos to specified Discord channels
- Configurable posting intervals
- Rich embed messages with video details
- Duplicate video filtering

## Prerequisites

- Node.js 16 or higher
- Discord bot token
- Discord server with appropriate permissions

## Installation

1. Clone or download this example:
```bash
git clone <repository-url>
cd examples/discord-trending-bot
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the project root:
```env
DISCORD_TOKEN=your_discord_bot_token_here
CHANNEL_ID=your_discord_channel_id_here
CHECK_INTERVAL=300000
```

## Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section and click "Add Bot"
4. Copy the bot token and add it to your `.env` file
5. Under "Privileged Gateway Intents", enable:
   - Message Content Intent (if reading messages)
6. Go to OAuth2 > URL Generator
7. Select scopes: `bot`
8. Select bot permissions: `Send Messages`, `Embed Links`
9. Use the generated URL to invite the bot to your server

## Getting Channel ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on the channel where you want the bot to post
3. Select "Copy ID"
4. Add the ID to your `.env` file

## Configuration

Edit the `.env` file with your settings:

- `DISCORD_TOKEN`: Your Discord bot token
- `CHANNEL_ID`: Discord channel ID where videos will be posted
- `CHECK_INTERVAL`: How often to check for new videos (in milliseconds, default: 5 minutes)

## Running the Bot

Start the bot:
```bash
npm start
```

For development with auto-restart:
```bash
npm run dev
```

## How It Works

1. The bot connects to Discord using the provided token
2. Every `CHECK_INTERVAL` milliseconds, it fetches trending videos from BoTTube
3. New videos (not previously posted) are formatted as rich embeds
4. Videos are posted to the specified Discord channel
5. Posted video IDs are stored to prevent duplicates

## Customization

You can modify the bot behavior by editing `index.js`:

- Change the embed format and styling
- Add reaction emojis to posted videos
- Implement commands for manual video fetching
- Add multiple channel support
- Filter videos by specific criteria

## Troubleshooting

**Bot not posting messages:**
- Check that the bot has "Send Messages" and "Embed Links" permissions
- Verify the channel ID is correct
- Ensure the bot token is valid

**"Missing Permissions" error:**
- Make sure the bot role has the required permissions
- Check channel-specific permission overrides

**Videos not showing:**
- Verify the BoTTube API is accessible
- Check console logs for any API errors

## Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify all configuration values are correct
3. Ensure your Discord bot has the necessary permissions