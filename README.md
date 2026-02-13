# LeetCode Interview Prep Bot

Telegram bot that helps you prepare for coding interviews by assigning LeetCode problems, tracking your progress, and rewarding achievements.

## Features

- **Smart Task Suggestions** — GPT-powered problem recommendations based on your skill level and history
- **Automatic Progress Tracking** — background worker monitors your LeetCode profile and detects completed problems
- **Statistics** — view completion stats by difficulty and category
- **Achievements** — unlock milestones like "Array Master" (10 array problems) or "Hard Hitter" (1 hard problem)

## Commands

| Command | Description |
|---------|-------------|
| `/start` | Register with your LeetCode username |
| `/tasks` | Get new problem suggestions |
| `/progress` | View your stats and pending tasks |
| `/achievements` | See achievement progress |

## Setup

### Prerequisites

- Docker & Docker Compose
- Telegram bot token (from [@BotFather](https://t.me/BotFather))
- OpenAI API key

### Run

1. Create a `.env` file:

```env
TELEGRAM_BOT_TOKEN=your-token
OPENAI_API_KEY=your-key
```

2. Start the bot:

```bash
docker compose up -d
```

The SQLite database is persisted in the `data/` volume.

### Run without Docker

Requires Python 3.14+.

```bash
pip install -r requirements.txt
python -m bot
```

## Tech Stack

- **aiogram 3** — async Telegram framework
- **aiosqlite** — async SQLite
- **OpenAI API** (gpt-4o-mini) — task suggestions
- **LeetCode GraphQL API** — profile & submission data
