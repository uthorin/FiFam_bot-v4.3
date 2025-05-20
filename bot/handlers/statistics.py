from pathlib import Path
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from datetime import date, timedelta, datetime
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from bot.states import CustomStatsStates
from bot.keyboards.entry import post_entry_keyboard
from database.db import get_detailed_statistics  
import sentry_sdk

router = Router()

def get_period_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Сегодня", callback_data="stats_today")],
        [InlineKeyboardButton(text="🗓 Неделя", callback_data="stats_week")],
        [InlineKeyboardButton(text="📆 Текущий месяц", callback_data="stats_month")],
        [InlineKeyboardButton(text="📈 Год", callback_data="stats_year")],
        [InlineKeyboardButton(text="🔀 Другое", callback_data="stats_custom")],
    ])

@router.message(Command(commands=["статистика", "stats"]))
async def cmd_statistics(message: Message):
    await message.answer("Выбери период для статистики:", reply_markup=get_period_keyboard())

@router.callback_query(F.data.startswith("stats_"))
async def handle_stats_period(callback: CallbackQuery, state: FSMContext, **data):
    user_id = callback.from_user.id
    today = date.today()

    period = callback.data
    start_date = None
    end_date = today

    if period == "stats_today":
        start_date = today
    elif period == "stats_week":
        start_date = today - timedelta(days=7)
    elif period == "stats_month":
        start_date = today.replace(day=1)
    elif period == "stats_year":
        start_date = today - timedelta(days=365)
    elif period == "stats_custom":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer("Выбери дату начала:", reply_markup=await SimpleCalendar().start_calendar())
        await state.set_state(CustomStatsStates.choosing_start_date)
        await callback.answer()
        return

    db = data.get('db')
    if not db:
        await callback.message.answer("❌ Ошибка: не удалось получить подключение к базе данных.")
        await callback.answer()
        return

    stats = await get_detailed_statistics(db, user_id, start_date, end_date)

    income_lines = "\n".join([f"• {k} — {v:,.2f}".replace(",", " ") for k, v in stats["income"].items()]) or "–"
    expense_lines = "\n".join([f"• {k} — {v:,.2f}".replace(",", " ") for k, v in stats["expense"].items()]) or "–"

    income_total = stats.get("total_income", 0)
    expense_total = stats.get("total_expense", 0)
    balance = stats.get("balance", 0)

    text = (
        f"📊 Статистика за выбранный период:\nс {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}:\n\n"
        f"💰 Доходы: {income_total:,.2f}".replace(",", " ") + "\n\n"
        f"{income_lines}\n\n"
        f"💸 Расходы: {expense_total:,.2f}".replace(",", " ") + "\n\n"
        f"{expense_lines}\n\n"
        f"📈 Баланс: {balance:,.2f}".replace(",", " ")
    )

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text)
    await callback.message.answer("Хочешь продолжить?", reply_markup=post_entry_keyboard())
    await callback.answer()

@router.callback_query(SimpleCalendarCallback.filter(), CustomStatsStates.choosing_start_date)
async def process_start_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext, **data):
    print(f"Processing start date act={callback_data.act} year={callback_data.year} month={callback_data.month} day={callback_data.day}")
    selected, result = await SimpleCalendar().process_selection(callback, callback_data)
    print(f"Result: {result}, selected: {selected}, type={type(result)}")

    if not selected:
        await callback.answer()
        return

    if isinstance(result, datetime):
        result = result.date()

    await state.update_data(start_date=result)
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        sentry_sdk.capture_exception(e)

    await callback.message.answer("Теперь выбери дату окончания:", reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(CustomStatsStates.choosing_end_date)
    await callback.answer()

@router.callback_query(SimpleCalendarCallback.filter(), CustomStatsStates.choosing_end_date)
async def process_end_date(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext, **data):
    print(f"Processing end date act={callback_data.act} year={callback_data.year} month={callback_data.month} day={callback_data.day}")
    selected, result = await SimpleCalendar().process_selection(callback, callback_data)
    print(f"Result: {result}, selected: {selected}, type={type(result)}")

    if not selected:
        await callback.answer()
        return

    if isinstance(result, datetime):
        result = result.date()

    fsm_data = await state.get_data()
    start_date = fsm_data.get("start_date")

    if result < start_date:
        await callback.message.answer("❌ Дата окончания не может быть раньше даты начала.")
        await callback.answer()
        return

    db = data.get('db')
    if not db:
        await callback.message.answer("❌ Ошибка: не удалось получить подключение к базе данных.")
        await callback.answer()
        return

    stats = await get_detailed_statistics(db, callback.from_user.id, start_date, result)

    income_lines = "\n".join([f"• {k} — {v:,.2f}".replace(",", " ") for k, v in stats["income"].items()]) or "–"
    expense_lines = "\n".join([f"• {k} — {v:,.2f}".replace(",", " ") for k, v in stats["expense"].items()]) or "–"

    text = (
        f"📊 Статистика за выбранный период:\n"
        f"с {start_date.strftime('%d.%m.%Y')} по {result.strftime('%d.%m.%Y')}:\n\n"
        f"💰 Доходы: {stats['total_income']:,.2f}".replace(",", " ") + "\n\n"
        f"{income_lines}\n\n"
        f"💸 Расходы: {stats['total_expense']:,.2f}".replace(",", " ") + "\n\n"
        f"{expense_lines}\n\n"
        f"📈 Баланс: {stats['balance']:,.2f}".replace(",", " ")
    )

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        sentry_sdk.capture_exception(e)

    await callback.message.answer(text)
    await callback.message.answer("Хочешь продолжить?", reply_markup=post_entry_keyboard())
    await state.clear()
    await callback.answer()
