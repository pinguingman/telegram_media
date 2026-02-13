from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from bot.db.repository import Repository
from bot.keyboards.inline import back_to_menu, main_menu

router = Router()


async def _build_progress_text(repo: Repository, telegram_id: int) -> str | None:
    user = await repo.get_user(telegram_id)
    if not user or not user["leetcode_username"]:
        return None

    total = await repo.get_total_completed(user["id"])
    by_diff = await repo.get_completed_count_by_difficulty(user["id"])
    by_cat = await repo.get_completed_count_by_category(user["id"])
    pending = await repo.get_pending_tasks(user["id"])

    lines = [f"**Progress for {user['leetcode_username']}**\n"]
    lines.append(f"Total completed: {total}\n")

    if by_diff:
        lines.append("By difficulty:")
        for diff, cnt in sorted(by_diff.items()):
            lines.append(f"  {diff}: {cnt}")

    if by_cat:
        lines.append("\nBy category:")
        for cat, cnt in sorted(by_cat.items()):
            lines.append(f"  {cat}: {cnt}")

    if pending:
        lines.append(f"\nPending tasks ({len(pending)}):")
        for t in pending:
            lines.append(f"  - {t['leetcode_slug']} [{t['difficulty']}]")

    return "\n".join(lines)


@router.message(Command("progress"))
async def cmd_progress(message: Message, repo: Repository) -> None:
    text = await _build_progress_text(repo, message.from_user.id)
    if not text:
        await message.answer("Please register first with /start", reply_markup=main_menu())
        return
    await message.answer(text, reply_markup=back_to_menu(), parse_mode="Markdown")


@router.callback_query(F.data == "progress")
async def callback_progress(callback: CallbackQuery, repo: Repository) -> None:
    text = await _build_progress_text(repo, callback.from_user.id)
    if not text:
        await callback.message.edit_text(
            "Please register first with /start", reply_markup=main_menu()
        )
    else:
        await callback.message.edit_text(
            text, reply_markup=back_to_menu(), parse_mode="Markdown"
        )
    await callback.answer()
