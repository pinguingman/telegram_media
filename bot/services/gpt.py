from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from bot.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a coding interview coach. You analyze a user's LeetCode profile \
and recommend specific problems to work on to improve their weak areas.

Always respond with valid JSON in the following format:
{
  "analysis": "Brief analysis of the user's strengths and weaknesses",
  "tasks": [
    {"titleSlug": "two-sum", "difficulty": "Easy", "category": "Array"},
    {"titleSlug": "add-two-numbers", "difficulty": "Medium", "category": "Linked List"},
    {"titleSlug": "longest-substring-without-repeating-characters", "difficulty": "Medium", "category": "Sliding Window"}
  ]
}

Rules:
- Suggest exactly 3 problems.
- Each problem must be a real LeetCode problem with a valid titleSlug.
- Don't suggest problems the user has already solved.
- Focus on weak areas — categories where the user has solved fewer problems.
- Mix difficulties appropriately for the user's level.
"""


class GPTService:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def suggest_tasks(
        self,
        solved_stats: list[dict],
        skill_stats: dict,
        completed_slugs: list[str],
        pending_slugs: list[str],
    ) -> dict[str, Any]:
        already_assigned = set(completed_slugs) | set(pending_slugs)
        user_prompt = f"""\
User's solved problems by difficulty:
{json.dumps(solved_stats, indent=2)}

User's skill tag breakdown:
{json.dumps(skill_stats, indent=2)}

Already assigned/completed problem slugs (do NOT suggest these):
{json.dumps(sorted(already_assigned))}

Analyze this profile, identify 2-3 weak areas, and suggest exactly 3 \
specific LeetCode problems to work on. Return valid JSON."""

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
        )

        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            logger.error("Failed to parse GPT response: %s", content)
            return {"analysis": "Error parsing response", "tasks": []}
