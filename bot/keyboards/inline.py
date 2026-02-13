from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Get Tasks", callback_data="get_tasks"),
                InlineKeyboardButton(text="Progress", callback_data="progress"),
            ],
            [
                InlineKeyboardButton(text="Achievements", callback_data="achievements"),
            ],
        ]
    )


def task_links(tasks: list[dict]) -> InlineKeyboardMarkup:
    """Build keyboard with links to LeetCode problems + navigation."""
    buttons = []
    for t in tasks:
        slug = t["titleSlug"]
        diff = t["difficulty"]
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{slug} [{diff}]",
                    url=f"https://leetcode.com/problems/{slug}/",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="Back to Menu", callback_data="main_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Get Tasks", callback_data="get_tasks"),
                InlineKeyboardButton(text="Back to Menu", callback_data="main_menu"),
            ]
        ]
    )
