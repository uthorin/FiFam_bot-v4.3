from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.handlers.statistics import cmd_statistics
from bot.handlers.entry_handler import start_entry_flow  # универсальный запуск дохода/расхода
from database.db import add_user


router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, **data):
    print("START COMMAND")
    user_id = message.from_user.id
    full_name = message.from_user.full_name

    await add_user(data['db'], user_id, full_name)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить доход", callback_data="start_income")],
        [InlineKeyboardButton(text="➖ Добавить расход", callback_data="start_expense")],
        [InlineKeyboardButton(text="📊 Посмотреть статистику", callback_data="start_stats")],
        [InlineKeyboardButton(text="ℹ️ Помощь", callback_data="start_help")]
    ])
    await message.answer(
        "🦾 Привет! Я — FiFam Bot, твой персональный ассистент по финансам.\n"

        "Не паникуй, мы всё разрулим:\n"
        "• Запишем доходы и расходы\n"
        "• Посмотрим, куда утекают деньги\n"
        "• Подскажем, как держать баланс\n\n"
        "• Можем распознавать чеки\n"
        "• Экспортировать данные в Excel\n"

        "🚀 Готов начать? Жми кнопку ниже.",
        reply_markup=keyboard
    )

@router.message(Command("help"))
@router.callback_query(F.data == "start_help")
async def cmd_help(event: Message | CallbackQuery, state: FSMContext):
    text = (
        "🆘 <b>Помощь:</b>\n\n"
        "— <b>/start</b> — главное меню\n"
        "— <b>/stats</b> — посмотреть отчёты\n"
        "— <b>/cancel</b> — отменить ввод\n"
        "— <b>/analysis</b> — анализ расходов\n\n"
        "— <b>/export</b> — экспорт в Excel\n"
        "👇 Или выбери действие:"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="start_menu")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="start_stats")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_entry")],
    ])

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=keyboard)
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboard)

@router.message(Command(commands=["отмена","cancel"]))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🚫 Ввод отменён.")

@router.callback_query(F.data == "start_income")
async def start_income_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await start_entry_flow(callback.message, state, entry_type="доход")
    await callback.answer()

@router.callback_query(F.data == "start_expense")
async def start_expense_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await start_entry_flow(callback.message, state, entry_type="расход")
    await callback.answer()

@router.callback_query(F.data == "start_stats")
async def start_stats_callback(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await cmd_statistics(callback.message)
    await callback.answer()

@router.callback_query(F.data == "start_help")
async def start_help_callback(callback: CallbackQuery):
    await callback.message.delete_reply_markup()
    await cmd_help(callback.message)
    await callback.answer()



