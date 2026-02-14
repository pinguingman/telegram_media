from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from bot.achievements.definitions import check_achievements
from bot.config import settings
from bot.db.repository import Repository
from bot.services.leetcode import LeetCodeClient

logger = logging.getLogger(__name__)


async def run_tracker(bot: Bot, repo: Repository, leetcode: LeetCodeClient) -> None:
    """Background task that polls LeetCode for completed assigned tasks."""
    logger.info("Tracker started (interval: %ds)", settings.tracker_interval_seconds)
    while True:
        try:
            await _poll_completions(bot, repo, leetcode)
        except Exception:
            logger.exception("Tracker poll error")
        await asyncio.sleep(settings.tracker_interval_seconds)


async def _poll_completions(
    bot: Bot, repo: Repository, leetcode: LeetCodeClient
) -> None:
    users = await repo.get_all_users_with_pending_tasks()
    for user in users:
        try:
            await _check_user(bot, repo, leetcode, user)
        except Exception:
            logger.exception("Error checking user %s", user["leetcode_username"])
        await asyncio.sleep(2)  # rate-limit between users


async def _check_user(
    bot: Bot, repo: Repository, leetcode: LeetCodeClient, user: dict
) -> None:
    recent = await leetcode.get_recent_submissions(user["leetcode_username"], limit=30)
    recent_slugs = {sub["titleSlug"] for sub in recent}

    pending = await repo.get_pending_tasks(user["id"])
    for task in pending:
        if task["leetcode_slug"] in recent_slugs:
            await repo.complete_task(task["id"])
            logger.info(
                "User %s completed %s",
                user["leetcode_username"],
                task["leetcode_slug"],
            )

            await bot.send_message(
                user["telegram_id"],
                f"Congrats! You completed **{task['leetcode_slug']}** "
                f"[{task['difficulty']}] 🎉",
                parse_mode="Markdown",
            )

            new_achievements = await check_achievements(repo, user["id"])
            for ach in new_achievements:
                await bot.send_message(
                    user["telegram_id"],
                    f"🏆 Achievement Unlocked: **{ach['name']}**\n"
                    f"_{ach['description']}_",
                    parse_mode="Markdown",
                )
