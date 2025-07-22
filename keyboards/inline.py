from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def pagination_keyboard(entity: str, page: int, has_next: bool) -> InlineKeyboardMarkup | None:
    buttons = []

    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"{entity}_page:{page - 1}"))

    if has_next:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"{entity}_page:{page + 1}"))

    if buttons:
        return InlineKeyboardMarkup(inline_keyboard=[buttons])
    return None
