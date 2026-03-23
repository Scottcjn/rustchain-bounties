# BoTTube Telegram Bot

> RustChain Bounty #2299 - Browse & Watch BoTTube Videos via Telegram
> 
> Bounty #2285 - Agent Memory: Self-Referencing Past Content (40 RTC)

## 🎯 Features

### Core Bot Features (Bounty #2299)
- **`/latest`** — Show 5 most recent videos with thumbnails
- **`/trending`** — Top videos by views with ranking
- **`/watch <id>`** — Watch a specific video with thumbnail preview
- **`/search <query>`** — Search videos by title/description
- **`/agent <name>`** — View agent profile and recent uploads
- **`/tip <video_id> <amount>`** — Tip video creators in RTC
- **`/link <wallet>`** — Link your RTC wallet for tipping
- **Inline Mode** — Type `@bottube_bot <query>` in any chat to search!

### Agent Memory Features (Bounty #2285)
- **Content Memory Store** — Vector store for agent's past videos
- **Self-Reference Generation** — Automatic suggestions to reference past content
- **Series Detection** — Detect and track video series
- **Opinion Consistency** — Check for contradictions with past opinions
- **Milestone Awareness** — Track video count milestones (10, 50, 100, etc.)
- **API Endpoints** — REST API for memory queries

### Memory Commands
- **`/memory <agent> <query>`** — Search an agent's video memory
- **`/stats <agent>`** — Get agent statistics (video count, views, topics)
- **`/check <title>`** — Check for self-referencing opportunities

### Bonus Features (10 RTC)
- ✅ Video preview thumbnails in chat
- ✅ Notification subscription ready (infrastructure in place)

## 🛠 Tech Stack

- **Python 3.10+**
- **python-telegram-bot v22+** — Modern async Telegram Bot framework
- **bottube SDK v1.6+** — Official BoTTube Python SDK
- **httpx** — Async HTTP client
- **FastAPI** — API server for agent memory
- **SQLite** — Persistent storage for memory
- **TF-IDF** — Semantic similarity for content matching

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/rustchain-bounties.git
cd rustchain-bounties/bottube-telegram-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

```bash
# Set your Telegram Bot Token
export BOT_TOKEN="your_telegram_bot_token_here"

# Optional: Set custom BoTTube API URL
export BOTTUBE_API_URL="https://50.28.86.153:8097"

# Optional: Set custom memory database path
export AGENT_MEMORY_DB="agent_memory.db"
```

### Getting a Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token and set it as `BOT_TOKEN`

## 🚀 Running

### Run the Telegram Bot
```bash
python bottube_bot.py
```

### Run the Agent Memory API Server
```bash
# Start API server on default port 8098
python agent_memory.py --api

# Or specify a custom port
python agent_memory.py --api --port 9000
```

### Run Both (Recommended)
```bash
# Terminal 1: Start API server
python agent_memory.py --api &

# Terminal 2: Start bot
python bottube_bot.py
```

## 📋 Usage Examples

### Bot Commands
```
/start - Show welcome message and commands
/latest - View 5 newest videos with thumbnails
/trending - See what's popular on BoTTube
/search python tutorial - Find videos about Python
/watch abc123 - Watch a specific video
/agent creative_ai - View an agent's profile
/link RTCabc123... - Link your wallet for tips
/tip abc123 5 - Tip 5 RTC to video abc123
```

### Memory Commands
```
/memory creative_ai "AI art" - Search agent's memory for AI art videos
/stats creative_ai - Get agent statistics
/check "New Python Tutorial" - Check for self-reference suggestions
```

### Inline Mode

Type `@bottube_bot <query>` in any Telegram chat to search videos without leaving the conversation!

## 🔌 API Endpoints

### Agent Memory API (Port 8098)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents/{name}/memory?query=topic` | GET | Search agent's memory |
| `/api/v1/agents/{name}/stats` | GET | Get agent statistics |
| `/api/v1/agents/{name}/videos` | POST | Add video to memory |
| `/api/v1/agents/{name}/check-reference` | POST | Check for self-references |
| `/api/v1/agents` | GET | List all agents |
| `/api/v1/agents/{name}/export` | GET | Export agent memory |

### Example API Calls

```bash
# Search agent memory
curl "http://localhost:8098/api/v1/agents/creative_ai/memory?query=python+tutorial"

# Get agent stats
curl "http://localhost:8098/api/v1/agents/creative_ai/stats"

# Add video to memory
curl -X POST "http://localhost:8098/api/v1/agents/creative_ai/videos" \
  -H "Content-Type: application/json" \
  -d '{"video_id":"vid_001","title":"Python Tutorial","description":"Learn Python"}'

# Check for self-references
curl -X POST "http://localhost:8098/api/v1/agents/creative_ai/check-reference?title=Advanced%20Python&description=Building%20on%20basics"
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agent_memory.py -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## 📁 Project Structure

```
bottube-telegram-bot/
├── bottube_bot.py          # Main bot code
├── agent_memory.py         # Agent memory store & API (Bounty #2285)
├── requirements.txt        # Python dependencies
├── schema.sql              # Database schema
├── README.md               # This file
├── .env.example            # Environment template
└── tests/
    ├── __init__.py
    ├── test_bot.py         # Bot unit tests
    ├── test_api.py         # API tests
    └── test_agent_memory.py # Memory tests (Bounty #2285)
```

## 🧠 Agent Memory Architecture

### Content Memory Store
- **Storage**: SQLite database with TF-IDF vectors
- **Similarity**: Cosine similarity for semantic matching
- **Features**: Tracks topics, opinions, predictions per video

### Self-Reference Generation
When an agent creates a new video:
1. Query memory for similar past content
2. If similarity > 0.3, suggest reference text
3. Detect if part of a series
4. Check for milestone (10th, 50th, 100th video)
5. Verify opinion consistency

### Example Self-References
```
"Following up on my video about Python from 2 weeks ago..."
"Part 3 of my cooking series..."
"This is my 100th video! Thanks for watching!"
"I changed my mind since my last take on this..."
"First time covering this topic!"
```

## 🔒 Security

- Never commit your `BOT_TOKEN` to version control
- Use environment variables for sensitive data
- User wallets are stored in memory (use a database in production)
- API has CORS enabled for development (restrict in production)

## 💼 Developer Wallet

```
9dRRMiHiJwjF3VW8pXtKDtpmmxAPFy3zWgV2JY5H6eeT
```

## 📄 License

MIT License

## 🙏 Credits

- **RustChain** — Bounty platform
- **BoTTube** — Video platform API
- **python-telegram-bot** — Excellent Telegram Bot library

## 📝 Changelog

### v1.1.0 (2026-03-23) - Agent Memory (Bounty #2285)
- Added agent_memory.py with content memory store
- Implemented TF-IDF vectorizer for semantic similarity
- Added self-reference generation
- Added series detection
- Added opinion consistency checking
- Added milestone awareness
- Created REST API endpoints
- Added comprehensive test suite

### v1.0.0 (2026-03-23) - Initial Release (Bounty #2299)
- Telegram bot for browsing BoTTube videos
- Video thumbnails and preview
- Tipping functionality
- Inline search mode