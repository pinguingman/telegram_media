from __future__ import annotations

from typing import Any

from bot.db.repository import Repository

ACHIEVEMENTS: list[dict[str, Any]] = [
    {
        "key": "array_10",
        "name": "Array Master",
        "description": "Complete 10 Array problems",
        "category": "Array",
        "required": 10,
    },
    {
        "key": "medium_1",
        "name": "Medium Starter",
        "description": "Complete 1 Medium problem",
        "difficulty": "Medium",
        "required": 1,
    },
    {
        "key": "hard_1",
        "name": "Hard Hitter",
        "description": "Complete 1 Hard problem",
        "difficulty": "Hard",
        "required": 1,
    },
    {
        "key": "dp_5",
        "name": "DP Apprentice",
        "description": "Complete 5 Dynamic Programming problems",
        "category": "Dynamic Programming",
        "required": 5,
    },
    {
        "key": "total_25",
        "name": "Quarter Century",
        "description": "Complete 25 total problems",
        "required": 25,
    },
]


async def check_achievements(repo: Repository, user_id: int) -> list[dict[str, Any]]:
    """Check and unlock any new achievements. Returns list of newly unlocked."""
    by_category = await repo.get_completed_count_by_category(user_id)
    by_difficulty = await repo.get_completed_count_by_difficulty(user_id)
    total = await repo.get_total_completed(user_id)

    newly_unlocked: list[dict[str, Any]] = []

    for ach in ACHIEVEMENTS:
        progress = _get_progress(ach, by_category, by_difficulty, total)
        if progress >= ach["required"]:
            if await repo.unlock_achievement(user_id, ach["key"]):
                newly_unlocked.append(ach)

    return newly_unlocked


def get_achievement_progress(
    ach: dict[str, Any],
    by_category: dict[str, int],
    by_difficulty: dict[str, int],
    total: int,
) -> int:
    return _get_progress(ach, by_category, by_difficulty, total)


def _get_progress(
    ach: dict[str, Any],
    by_category: dict[str, int],
    by_difficulty: dict[str, int],
    total: int,
) -> int:
    if "category" in ach:
        return by_category.get(ach["category"], 0)
    if "difficulty" in ach:
        return by_difficulty.get(ach["difficulty"], 0)
    return total
