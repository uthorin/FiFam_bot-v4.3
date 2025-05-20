from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_income"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_income")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_category")
        ]
    ])
