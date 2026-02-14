from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    openai_api_key: str
    database_path: str = "data/bot.db"
    leetcode_graphql_url: str = "https://leetcode.com/graphql/"
    tracker_interval_seconds: int = 300

    model_config = {"env_file": ".env"}


settings = Settings()

# Ensure the data directory exists
Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
