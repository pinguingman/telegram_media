from __future__ import annotations

from datetime import datetime
from typing import Any

import aiosqlite


class Repository:
    def __init__(self, db: aiosqlite.Connection) -> None:
        self.db = db

    # ── Users ──────────────────────────────────────────────

    async def get_or_create_user(self, telegram_id: int) -> dict[str, Any]:
        cur = await self.db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cur.fetchone()
        if row:
            return dict(row)
        await self.db.execute(
            "INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,)
        )
        await self.db.commit()
        cur = await self.db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        return dict(await cur.fetchone())

    async def set_leetcode_username(self, telegram_id: int, username: str) -> None:
        await self.db.execute(
            "UPDATE users SET leetcode_username = ? WHERE telegram_id = ?",
            (username, telegram_id),
        )
        await self.db.commit()

    async def get_user(self, telegram_id: int) -> dict[str, Any] | None:
        cur = await self.db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        row = await cur.fetchone()
        return dict(row) if row else None

    async def get_all_users_with_pending_tasks(self) -> list[dict[str, Any]]:
        cur = await self.db.execute(
            """
            SELECT DISTINCT u.* FROM users u
            JOIN assigned_tasks t ON t.user_id = u.id
            WHERE t.completed_at IS NULL AND u.leetcode_username IS NOT NULL
            """
        )
        return [dict(r) for r in await cur.fetchall()]

    # ── Assigned Tasks ─────────────────────────────────────

    async def assign_task(
        self,
        user_id: int,
        slug: str,
        difficulty: str,
        category: str,
    ) -> int:
        cur = await self.db.execute(
            """
            INSERT INTO assigned_tasks (user_id, leetcode_slug, difficulty, category)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, slug, difficulty, category),
        )
        await self.db.commit()
        return cur.lastrowid

    async def get_pending_tasks(self, user_id: int) -> list[dict[str, Any]]:
        cur = await self.db.execute(
            "SELECT * FROM assigned_tasks WHERE user_id = ? AND completed_at IS NULL",
            (user_id,),
        )
        return [dict(r) for r in await cur.fetchall()]

    async def get_completed_tasks(self, user_id: int) -> list[dict[str, Any]]:
        cur = await self.db.execute(
            "SELECT * FROM assigned_tasks WHERE user_id = ? AND completed_at IS NOT NULL",
            (user_id,),
        )
        return [dict(r) for r in await cur.fetchall()]

    async def complete_task(self, task_id: int) -> None:
        await self.db.execute(
            "UPDATE assigned_tasks SET completed_at = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), task_id),
        )
        await self.db.commit()

    async def get_completed_count_by_category(self, user_id: int) -> dict[str, int]:
        cur = await self.db.execute(
            """
            SELECT category, COUNT(*) as cnt FROM assigned_tasks
            WHERE user_id = ? AND completed_at IS NOT NULL
            GROUP BY category
            """,
            (user_id,),
        )
        return {row["category"]: row["cnt"] for row in await cur.fetchall()}

    async def get_completed_count_by_difficulty(self, user_id: int) -> dict[str, int]:
        cur = await self.db.execute(
            """
            SELECT difficulty, COUNT(*) as cnt FROM assigned_tasks
            WHERE user_id = ? AND completed_at IS NOT NULL
            GROUP BY difficulty
            """,
            (user_id,),
        )
        return {row["difficulty"]: row["cnt"] for row in await cur.fetchall()}

    async def get_total_completed(self, user_id: int) -> int:
        cur = await self.db.execute(
            "SELECT COUNT(*) as cnt FROM assigned_tasks WHERE user_id = ? AND completed_at IS NOT NULL",
            (user_id,),
        )
        row = await cur.fetchone()
        return row["cnt"]

    # ── Achievements ───────────────────────────────────────

    async def get_user_achievements(self, user_id: int) -> list[dict[str, Any]]:
        cur = await self.db.execute(
            "SELECT * FROM achievements WHERE user_id = ?", (user_id,)
        )
        return [dict(r) for r in await cur.fetchall()]

    async def unlock_achievement(self, user_id: int, key: str) -> bool:
        """Returns True if newly unlocked, False if already existed."""
        try:
            await self.db.execute(
                "INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)",
                (user_id, key),
            )
            await self.db.commit()
            return True
        except Exception:
            return False
