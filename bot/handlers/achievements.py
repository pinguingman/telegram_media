from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.achievements.definitions import ACHIEVEMENTS, get_achievement_progress
from bot.db.repository import Repository
from bot.keyboards.inline import back_to_menu, main_menu

router = Router()

FILLED = "\u2588"
EMPTY = "\u2591"
BAR_LENGTH = 10


def _progress_bar(current: int, required: int) -> str:
    ratio = min(current / required, 1.0)
    filled = round(ratio * BAR_LENGTH)
    return FILLED * filled + EMPTY * (BAR_LENGTH - filled)


async def _build_achievements_text(repo: Repository, telegram_id: int) -> str | None:
    user = await repo.get_user(telegram_id)
    if not user or not user["leetcode_username"]:
        return None

    unlocked = await repo.get_user_achievements(user["id"])
    unlocked_keys = {a["achievement_key"] for a in unlocked}

    by_cat = await repo.get_completed_count_by_category(user["id"])
    by_diff = await repo.get_completed_count_by_difficulty(user["id"])
    total = await repo.get_total_completed(user["id"])

    lines = ["**Achievements**\n"]

    for ach in ACHIEVEMENTS:
        progress = get_achievement_progress(ach, by_cat, by_diff, total)
        required = ach["required"]
        bar = _progress_bar(progress, required)
        status = " ✅" if ach["key"] in unlocked_keys else ""
        lines.append(
            f"{ach['name']}: {progress}/{required} {bar}{status}\n"
            f"  _{ach['description']}_"
        )

    return "\n".join(lines)


@router.message(Command("achievements"))
async def cmd_achievements(message: Message, repo: Repository) -> None:
    text = await _build_achievements_text(repo, message.from_user.id)
    if not text:
        await message.answer("Please register first with /start", reply_markup=main_menu())
        return
    await message.answer(text, reply_markup=back_to_menu(), parse_mode="Markdown")


@router.callback_query(F.data == "achievements")
async def callback_achievements(callback: CallbackQuery, repo: Repository) -> None:
    text = await _build_achievements_text(repo, callback.from_user.id)
    if not text:
        await callback.message.edit_text(
            "Please register first with /start", reply_markup=main_menu()
        )
    else:
        await callback.message.edit_text(
            text, reply_markup=back_to_menu(), parse_mode="Markdown"
        )
    await callback.answer()
