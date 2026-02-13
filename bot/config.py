import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
OPENAI_API_KEY: str = os.environ["OPENAI_API_KEY"]
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/bot.db")

# Ensure the data directory exists
Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql/"
TRACKER_INTERVAL_SECONDS = 300  # 5 minutes
