import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from datetime import date
from bot.handlers.analysis import start_analysis_base
from bot.categories import income_categories, expense_categories

from bot.states import EntryStates
from bot.keyboards.entry import (
    type_keyboard,
    category_keyboard,
    date_choice_keyboard,
    confirm_keyboard,
    back_keyboard,
    post_entry_keyboard,
)
from database.db import add_transaction
from utils.type_mapping import to_internal_type, to_display_type

router = Router()

async def start_entry_flow(message: Message, state: FSMContext, entry_type: str):
    internal_type = to_internal_type(entry_type)
    await state.set_state(EntryStates.choosing_amount)
    await state.update_data(type=internal_type)
    await message.answer("Введи сумму:")

@router.message(F.text.lower() == "добавить запись")
async def start_entry_from_text(message: Message, state: FSMContext):
    await state.set_state(EntryStates.choosing_type)
    await message.answer("Что ты хочешь добавить?", reply_markup=type_keyboard())

@router.callback_query(F.data.in_(["доход", "расход"]))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    entry_type = callback.data
    internal_type = to_internal_type(callback.data)
    await state.update_data(type=internal_type)
    await state.set_state(EntryStates.choosing_amount)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(f"Введи сумму {entry_type.lower()}а:")
    await callback.answer()

@router.message(EntryStates.choosing_amount)
async def choose_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text.replace(",", "."))
        if amount <= 0:
            await message.reply("Сумма должна быть больше 0.")
            return
    except ValueError:
        await message.reply("Некорректная сумма. Введи число.")
        return

    await state.update_data(amount=amount)
    await state.set_state(EntryStates.choosing_category)
    fsm_data = await state.get_data()
    display_type = to_display_type(fsm_data['type'])
    await message.answer(
        f"Выбери категорию для {display_type}а:",
        reply_markup=category_keyboard(fsm_data['type'])
    )

@router.callback_query(EntryStates.choosing_category)
async def choose_category(callback: CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    entry_type = fsm_data.get("type")  # "income" или "expense"

    valid = income_categories if entry_type == "income" else expense_categories

    # 💡 Валидация
    if callback.data not in valid:
        await callback.answer("❌ Неверная категория.")
        return

    await state.update_data(category=callback.data)
    await state.set_state(EntryStates.choosing_date)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("За какую дату?", reply_markup=date_choice_keyboard())
    await callback.answer()

@router.callback_query(EntryStates.choosing_date, F.data == "сегодня")
async def choose_today(callback: CallbackQuery, state: FSMContext):
    await state.update_data(date=date.today())
    await callback.message.edit_reply_markup(reply_markup=None)
    await show_confirm(callback.message, state)
    await state.set_state(EntryStates.confirming)
    await callback.answer()

@router.callback_query(EntryStates.choosing_date, F.data == "другая")
async def choose_custom_date(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Выбери дату:", reply_markup=await SimpleCalendar().start_calendar())
    await callback.answer()

@router.callback_query(SimpleCalendarCallback.filter(), EntryStates.choosing_date)
async def process_calendar(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    selected = date(callback_data.year, callback_data.month, callback_data.day)
    await state.update_data(date=selected)
    await callback.message.edit_reply_markup(reply_markup=None)
    await show_confirm(callback.message, state)
    await state.set_state(EntryStates.confirming)
    await callback.answer()

async def show_confirm(message: Message, state: FSMContext):
    fsm_data = await state.get_data()
    display_type = to_display_type(fsm_data['type'])
    text = (
        f"Подтверди добавление записи:\n\n"
        f"Тип: {display_type.capitalize()}\n"
        f"Сумма: {fsm_data['amount']}\n"
        f"Категория: {fsm_data['category']}\n"
        f"Дата: {fsm_data['date']}"
    )
    await message.answer(text, reply_markup=confirm_keyboard())

@router.callback_query(F.data == "confirm_entry")
async def confirm_entry(callback: CallbackQuery, state: FSMContext, **data):
    """
    Обработчик подтверждения добавления записи.
    Сохраняет запись в базу данных и уведомляет пользователя о результате.

    Args:
        callback (CallbackQuery): Объект callback-запроса.
        state (FSMContext): Контекст состояния FSM.
        data (dict): Дополнительные данные.
    """
    fsm_data = await state.get_data()

    # Проверка корректности данных перед добавлением
    if not isinstance(fsm_data.get("amount"), (int, float)) or fsm_data["amount"] <= 0:
        await callback.message.answer("❌ Некорректная сумма. Попробуй снова.")
        return
    if not isinstance(fsm_data.get("date"), date):
        await callback.message.answer("❌ Некорректная дата. Попробуй снова.")
        return

    try:
        # Добавление записи в базу данных
        await add_transaction(
            data['db'],
            user_id=callback.from_user.id,
            type_=fsm_data["type"],
            amount=fsm_data["amount"],
            category=fsm_data["category"],
            date_=fsm_data["date"],
            description=""
        )

        # Формирование текста для подтверждения
        display_type = to_display_type(fsm_data["type"])
        text = (
            "✅ Запись добавлена!\n\n"
            f"Тип: {display_type.capitalize()}\n"
            f"Сумма: {fsm_data['amount']}\n"
            f"Категория: {fsm_data['category']}\n"
            f"Дата: {fsm_data['date'].strftime('%d.%m.%Y')}"
        )
    except Exception as e:
        # Логирование ошибки и уведомление пользователя
        logging.error(f"Ошибка при добавлении записи для пользователя {callback.from_user.id}: {e}")
        await callback.message.answer("❌ Ошибка при добавлении записи. Попробуй снова.")
        return

    # Удаление клавиатуры и отправка подтверждения
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(text, reply_markup=post_entry_keyboard())

    # Очистка состояния и завершение callback-запроса
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "cancel_entry")
async def cancel_entry(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("❌ Запись отменена!", reply_markup=post_entry_keyboard())
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "back_to_category")
async def back_to_category(callback: CallbackQuery, state: FSMContext):
    fsm_data = await state.get_data()
    display_type = to_display_type(fsm_data['type'])
    await state.set_state(EntryStates.choosing_category)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        f"Выбери категорию для {display_type}а:",
        reply_markup=category_keyboard(fsm_data['type'])
    )
    await callback.answer()

@router.callback_query(F.data == "add_another")
async def handle_add_another(callback: CallbackQuery, state: FSMContext):
    await state.set_state(EntryStates.choosing_type)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Что ты хочешь добавить?", reply_markup=type_keyboard())
    await callback.answer()

@router.callback_query(F.data == "start_stats")
async def handle_go_stats(callback: CallbackQuery, state: FSMContext):
    from bot.handlers.statistics import cmd_statistics
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await cmd_statistics(callback.message)
    await callback.answer()

@router.callback_query(F.data == "start_menu")
async def handle_go_menu(callback: CallbackQuery, state: FSMContext, **data):
    from bot.handlers.common import cmd_start
    await state.clear()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("👋 Возврат в главное меню.")  # Можно вызвать cmd_start, если убрать циклический импорт
    await cmd_start(callback.message, state, **data)
    await state.clear()
    await callback.answer()

@router.message(F.data == "crash")
async def crash(msg: Message):
    1 / 0  # Ошибка для теста Sentry

@router.callback_query(F.data == "start_analysis")
async def start_analysis_callback(callback: CallbackQuery, state: FSMContext, **data):
    await callback.answer("🔄 Идёт анализ...")
    user_id = callback.from_user.id
    await start_analysis_base(user_id, callback, state, **data)





