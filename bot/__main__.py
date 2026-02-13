import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import TELEGRAM_BOT_TOKEN, DATABASE_PATH
from bot.db.models import init_db
from bot.db.repository import Repository
from bot.handlers import start, tasks, progress, achievements
from bot.services.gpt import GPTService
from bot.services.leetcode import LeetCodeClient
from bot.services.tracker import run_tracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    db = await init_db(DATABASE_PATH)
    repo = Repository(db)
    leetcode = LeetCodeClient()
    gpt = GPTService()

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(tasks.router)
    dp.include_router(progress.router)
    dp.include_router(achievements.router)

    # Inject dependencies via dispatcher workflow data
    dp["repo"] = repo
    dp["leetcode"] = leetcode
    dp["gpt"] = gpt

    # Start background tracker
    tracker_task = asyncio.create_task(run_tracker(bot, repo, leetcode))

    logger.info("Bot starting...")
    try:
        await dp.start_polling(bot)
    finally:
        tracker_task.cancel()
        await leetcode.close()
        await db.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
