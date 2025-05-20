from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils.ai import generate_financial_analysis


def analysis_nav_keyboard(step: int, total: int) -> InlineKeyboardMarkup:
    buttons = []
    if step < total - 1:
        buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data="analysis_next"))
        buttons.append(InlineKeyboardButton(text="❌ Отмена", callback_data="analysis_cancel"))
    else:
        buttons.append(InlineKeyboardButton(text="✅ Окей", callback_data="analysis_done"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

