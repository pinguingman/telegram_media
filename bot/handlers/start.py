from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.db.repository import Repository
from bot.keyboards.inline import main_menu
from bot.services.leetcode import LeetCodeClient

router = Router()


class Registration(StatesGroup):
    waiting_for_username = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, repo: Repository) -> None:
    user = await repo.get_user(message.from_user.id)
    if user and user["leetcode_username"]:
        await message.answer(
            f"Welcome back! Your LeetCode username: {user['leetcode_username']}",
            reply_markup=main_menu(),
        )
        return

    await repo.get_or_create_user(message.from_user.id)
    await state.set_state(Registration.waiting_for_username)
    await message.answer(
        "Welcome to LeetCode Interview Prep Bot!\n\n"
        "Please enter your LeetCode username:"
    )


@router.message(Registration.waiting_for_username)
async def process_username(
    message: Message,
    state: FSMContext,
    repo: Repository,
    leetcode: LeetCodeClient,
) -> None:
    username = message.text.strip()
    profile = await leetcode.get_user_profile(username)

    if not profile:
        await message.answer(
            f"Username '{username}' not found on LeetCode. Please try again:"
        )
        return

    await repo.set_leetcode_username(message.from_user.id, username)
    await state.clear()

    stats = profile.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
    stats_text = "\n".join(
        f"  {s['difficulty']}: {s['count']}" for s in stats if s["difficulty"] != "All"
    )

    await message.answer(
        f"Connected to LeetCode as **{username}**!\n\n"
        f"Your current stats:\n{stats_text}\n\n"
        "Use the buttons below to get started.",
        reply_markup=main_menu(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "What would you like to do?", reply_markup=main_menu()
    )
    await callback.answer()
