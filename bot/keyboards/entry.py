from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.categories import income_categories, expense_categories




def get_categories(entry_type: str) -> list[str]:
    if entry_type in ("доход", "income"):
        return income_categories
    return expense_categories

back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="go_back")]
])

def type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Доход", callback_data="доход")],
        [InlineKeyboardButton(text="💸 Расход", callback_data="расход")]
    ])

def category_keyboard(entry_type: str):
    categories = get_categories(entry_type)
    buttons = [[InlineKeyboardButton(text=cat, callback_data=cat)] for cat in categories]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def date_choice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data="сегодня")],
        [InlineKeyboardButton(text="Другая дата", callback_data="другая")]
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_entry")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_category")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_entry")]
    ])

def post_entry_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить", callback_data="add_another")],
        [InlineKeyboardButton(text="📊 Посмотреть статистику", callback_data="start_stats")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="start_menu")],
        [InlineKeyboardButton(text="📈 Анализ", callback_data="start_analysis")],
        

    ])

