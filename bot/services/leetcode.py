from __future__ import annotations

import logging
from typing import Any

import aiohttp

from bot.config import LEETCODE_GRAPHQL_URL

logger = logging.getLogger(__name__)


class LeetCodeClient:
    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._session = session

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def _query(self, query: str, variables: dict[str, Any] | None = None) -> dict:
        session = await self._get_session()
        payload: dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        async with session.post(
            LEETCODE_GRAPHQL_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()
            if "errors" in data:
                logger.error("GraphQL errors: %s", data["errors"])
            return data.get("data", {})

    # 1. Validate user + get profile
    async def get_user_profile(self, username: str) -> dict | None:
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """
        data = await self._query(query, {"username": username})
        return data.get("matchedUser")

    # 2. Recent accepted submissions
    async def get_recent_submissions(
        self, username: str, limit: int = 20
    ) -> list[dict]:
        query = """
        query recentAcSubmissions($username: String!, $limit: Int!) {
            recentAcSubmissionList(username: $username, limit: $limit) {
                titleSlug
                title
                timestamp
            }
        }
        """
        data = await self._query(query, {"username": username, "limit": limit})
        return data.get("recentAcSubmissionList") or []

    # 3. Problems solved by difficulty
    async def get_problems_solved(self, username: str) -> list[dict]:
        query = """
        query userProblemsSolved($username: String!) {
            matchedUser(username: $username) {
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """
        data = await self._query(query, {"username": username})
        user = data.get("matchedUser")
        if not user:
            return []
        return user["submitStatsGlobal"]["acSubmissionNum"]

    # 4. Skill tags breakdown
    async def get_skill_stats(self, username: str) -> dict:
        query = """
        query skillStats($username: String!) {
            matchedUser(username: $username) {
                tagProblemCounts {
                    advanced { tagName problemsSolved }
                    intermediate { tagName problemsSolved }
                    fundamental { tagName problemsSolved }
                }
            }
        }
        """
        data = await self._query(query, {"username": username})
        user = data.get("matchedUser")
        if not user:
            return {}
        return user.get("tagProblemCounts", {})

    # 5. Validate a problem exists by slug
    async def validate_problem(self, slug: str) -> dict | None:
        query = """
        query getQuestion($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                titleSlug
                title
                difficulty
                topicTags { name }
            }
        }
        """
        data = await self._query(query, {"titleSlug": slug})
        return data.get("question")
