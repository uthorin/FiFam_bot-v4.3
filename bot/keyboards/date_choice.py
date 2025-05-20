from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def date_choice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Сегодня", callback_data="use_today_date"),
            InlineKeyboardButton(text="📅 Указать дату", callback_data="custom_date")
        ]
    ])
