import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from bot.db.repository import Repository
from bot.keyboards.inline import main_menu, task_links
from bot.services.gpt import GPTService
from bot.services.leetcode import LeetCodeClient

router = Router()
logger = logging.getLogger(__name__)


async def _suggest_tasks(
    repo: Repository,
    leetcode: LeetCodeClient,
    gpt: GPTService,
    telegram_id: int,
) -> str | tuple[str, list[dict]]:
    """Fetch data, call GPT, validate, save tasks. Returns message or (message, tasks)."""
    user = await repo.get_user(telegram_id)
    if not user or not user["leetcode_username"]:
        return "Please register first with /start"

    username = user["leetcode_username"]

    solved_stats = await leetcode.get_problems_solved(username)
    skill_stats = await leetcode.get_skill_stats(username)

    completed = await repo.get_completed_tasks(user["id"])
    pending = await repo.get_pending_tasks(user["id"])
    completed_slugs = [t["leetcode_slug"] for t in completed]
    pending_slugs = [t["leetcode_slug"] for t in pending]

    result = await gpt.suggest_tasks(
        solved_stats, skill_stats, completed_slugs, pending_slugs
    )

    analysis = result.get("analysis", "")
    tasks = result.get("tasks", [])

    if not tasks:
        return "Couldn't generate task suggestions right now. Please try again later."

    valid_tasks: list[dict] = []
    for task in tasks[:3]:
        slug = task.get("titleSlug", "")
        problem = await leetcode.validate_problem(slug)
        if problem:
            difficulty = problem.get("difficulty", task.get("difficulty", "Medium"))
            tags = problem.get("topicTags", [])
            category = tags[0]["name"] if tags else task.get("category", "General")
            await repo.assign_task(user["id"], slug, difficulty, category)
            valid_tasks.append(
                {"titleSlug": slug, "difficulty": difficulty, "category": category}
            )

    if not valid_tasks:
        return "Couldn't validate suggested problems. Please try again."

    text = f"**Analysis:** {analysis}\n\nHere are your tasks:\n"
    for i, t in enumerate(valid_tasks, 1):
        text += f"\n{i}. **{t['titleSlug']}** [{t['difficulty']}] — {t['category']}"

    return text, valid_tasks


@router.message(Command("tasks"))
async def cmd_tasks(
    message: Message,
    repo: Repository,
    leetcode: LeetCodeClient,
    gpt: GPTService,
) -> None:
    await message.answer("Analyzing your profile and generating suggestions...")
    result = await _suggest_tasks(repo, leetcode, gpt, message.from_user.id)

    if isinstance(result, str):
        await message.answer(result, reply_markup=main_menu())
    else:
        text, tasks = result
        await message.answer(
            text, reply_markup=task_links(tasks), parse_mode="Markdown"
        )


@router.callback_query(F.data == "get_tasks")
async def callback_get_tasks(
    callback: CallbackQuery,
    repo: Repository,
    leetcode: LeetCodeClient,
    gpt: GPTService,
) -> None:
    await callback.message.edit_text(
        "Analyzing your profile and generating suggestions..."
    )
    await callback.answer()

    result = await _suggest_tasks(repo, leetcode, gpt, callback.from_user.id)

    if isinstance(result, str):
        await callback.message.edit_text(result, reply_markup=main_menu())
    else:
        text, tasks = result
        await callback.message.edit_text(
            text, reply_markup=task_links(tasks), parse_mode="Markdown"
        )
