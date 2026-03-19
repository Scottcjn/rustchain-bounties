# Discord BoTTube Bot

A Discord bot that integrates with BoTTube to provide tube management functionality directly in Discord servers.

## Features

- Create and manage tubes
- Subscribe to tube notifications
- Search and filter tube content
- Real-time updates in Discord channels

## Setup Instructions

### Prerequisites

- Node.js 16.0.0 or higher
- A Discord application and bot token
- BoTTube SDK credentials

### Installation

1. Clone this repository and navigate to the bot directory:
```bash
cd examples/discord-bottube-bot
npm install
```

2. Create a Discord application and bot:
   - Go to https://discord.com/developers/applications
   - Click "New Application" and give it a name
   - Navigate to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token

3. Configure environment variables:
```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:
```
DISCORD_TOKEN=your_discord_bot_token_here
BOTTUBE_API_KEY=your_bottube_api_key_here
BOTTUBE_BASE_URL=https://api.bottube.example.com
```

4. Invite the bot to your Discord server:
   - In the Discord Developer Portal, go to OAuth2 > URL Generator
   - Select "bot" scope
   - Select required permissions:
     - Send Messages
     - Embed Links
     - Read Message History
     - Use Slash Commands
   - Copy the generated URL and open it to invite the bot

### Running the Bot

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm start
```

### Deployment

#### Using PM2 (Recommended)

1. Install PM2 globally:
```bash
npm install -g pm2
```

2. Start the bot with PM2:
```bash
pm2 start ecosystem.config.js
```

3. Save PM2 configuration:
```bash
pm2 save
pm2 startup
```

#### Using Docker

1. Build the Docker image:
```bash
docker build -t discord-bottube-bot .
```

2. Run the container:
```bash
docker run -d --env-file .env --name bottube-bot discord-bottube-bot
```

#### Deploy to Heroku

1. Create a new Heroku app:
```bash
heroku create your-bot-name
```

2. Set environment variables:
```bash
heroku config:set DISCORD_TOKEN=your_token_here
heroku config:set BOTTUBE_API_KEY=your_api_key_here
heroku config:set BOTTUBE_BASE_URL=your_api_url_here
```

3. Deploy:
```bash
git push heroku main
```

## Bot Commands

- `/tube create <name>` - Create a new tube
- `/tube list` - List your tubes
- `/tube subscribe <tube-id>` - Subscribe to tube updates
- `/tube search <query>` - Search tube content
- `/tube status` - Check bot status and connection

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Discord bot token | Yes |
| `BOTTUBE_API_KEY` | BoTTube API key | Yes |
| `BOTTUBE_BASE_URL` | BoTTube API base URL | Yes |
| `PREFIX` | Bot command prefix (default: !) | No |
| `NODE_ENV` | Environment (development/production) | No |

### Permissions

The bot requires the following Discord permissions:
- Send Messages
- Embed Links
- Read Message History
- Use Slash Commands
- Manage Messages (for cleanup features)

## Troubleshooting

### Common Issues

1. **Bot not responding to commands**
   - Verify the bot token is correct
   - Check that the bot has required permissions
   - Ensure the bot is online in your server

2. **BoTTube API errors**
   - Verify your API key is valid
   - Check the base URL configuration
   - Ensure you have sufficient API quota

3. **Missing dependencies**
   - Run `npm install` to install all dependencies
   - Check Node.js version compatibility

### Logs

View bot logs:
```bash
# PM2
pm2 logs discord-bottube-bot

# Docker
docker logs bottube-bot

# Direct execution
npm run dev
```

## Development

### Project Structure

```
examples/discord-bottube-bot/
├── src/
│   ├── commands/          # Slash commands
│   ├── events/            # Discord event handlers
│   ├── services/          # BoTTube integration
│   └── utils/             # Helper functions
├── config/                # Configuration files
├── tests/                 # Test files
└── package.json
```

### Adding New Commands

1. Create a new file in `src/commands/`
2. Export a command object with `data` and `execute` properties
3. The command will be automatically registered

### Testing

Run tests:
```bash
npm test
```

Run tests with coverage:
```bash
npm run test:coverage
```

## Support

For issues and questions:
- Check the troubleshooting section above
- Open an issue in the repository
- Join our Discord support server

## License

This project is licensed under the MIT License - see the LICENSE file for details.