# Discord BoTTube Bot Example

A Discord bot that integrates with BoTTube to create interactive video experiences in your Discord server.

## Features

- Play YouTube videos with synchronized viewing
- Create watch parties with your Discord community
- Queue management for video playlists
- Real-time chat integration during video playback

## Prerequisites

- Node.js 16.0 or higher
- A Discord application/bot token
- BoTTube API credentials

## Setup Instructions

### 1. Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give your bot a name
3. Navigate to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Copy the bot token (keep this secure!)
6. Under "Privileged Gateway Intents", enable:
   - Message Content Intent
   - Server Members Intent

### 2. Bot Permissions

Your bot needs the following permissions:
- Send Messages
- Read Message History
- Use Slash Commands
- Connect (for voice channels)
- Speak (for voice channels)
- Embed Links
- Add Reactions

Use this permission integer: `2048` or generate a custom invite link in the OAuth2 section.

### 3. Environment Configuration

Create a `.env` file in this directory:

```env
DISCORD_TOKEN=your_discord_bot_token_here
BOTTUBE_API_KEY=your_bottube_api_key
BOTTUBE_API_URL=https://api.bottube.com
```

### 4. Installation

```bash
npm install
```

### 5. Running the Bot

```bash
npm start
```

## Usage

### Commands

- `/play <youtube_url>` - Start playing a YouTube video
- `/queue <youtube_url>` - Add a video to the queue
- `/skip` - Skip current video
- `/stop` - Stop playback and clear queue
- `/party` - Create a watch party room
- `/join <party_id>` - Join an existing watch party

### Example Usage

```
/play https://www.youtube.com/watch?v=dQw4w9WgXcQ
/party
/queue https://www.youtube.com/watch?v=example
```

## Bot Invite Link

Replace `YOUR_CLIENT_ID` with your bot's client ID from the Discord Developer Portal:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2048&scope=bot%20applications.commands
```

## Troubleshooting

### Bot Not Responding
- Verify your bot token is correct
- Check that the bot has proper permissions in your server
- Ensure the bot is online in the Discord Developer Portal

### Permission Errors
- Make sure the bot has the required permissions listed above
- Check that the bot role is positioned high enough in your server's role hierarchy

### API Errors
- Verify your BoTTube API credentials
- Check the API URL is correct
- Ensure you have sufficient API quota

## Support

For issues specific to this Discord bot example, please check the logs for error messages. For BoTTube SDK issues, refer to the main SDK documentation.