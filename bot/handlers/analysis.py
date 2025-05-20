from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards.analysis import analysis_nav_keyboard
from bot.states import AnalysisStates
from database.db import get_transactions_for_analysis
from bot.utils.ai import get_ai_financial_advice
from bot.keyboards.entry import post_entry_keyboard
from aiogram.filters import Command
router = Router()

async def start_analysis_base(user_id: int, sender: Message | CallbackQuery, state: FSMContext, **data):
    transactions = await get_transactions_for_analysis(data['db'], user_id)

    if not transactions:
        await sender.answer("📭 Недостаточно данных для анализа.") if isinstance(sender, Message) \
            else await sender.message.answer("📭 Недостаточно данных для анализа.")
        return

    loading_msg = await sender.answer("🔄 Идёт анализ...") if isinstance(sender, Message) \
        else await sender.message.answer("🔄 Идёт анализ...")

    steps = await get_ai_financial_advice(transactions)
    await state.set_state(AnalysisStates.in_progress)
    await state.update_data(steps=steps, step_index=0)

    first_step = steps[0]
    keyboard = analysis_nav_keyboard(0, len(steps))
    await loading_msg.edit_text(first_step, reply_markup=keyboard)

@router.callback_query(F.data == "analysis_next")
async def next_analysis_step(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    steps = data["steps"]
    index = data["step_index"] + 1

    if index >= len(steps):
        await callback.message.edit_text("✅ Анализ завершён.")
        await state.clear()
        await callback.answer()
        return

    await state.update_data(step_index=index)
    await callback.message.edit_text(
        steps[index],
        reply_markup=analysis_nav_keyboard(index, len(steps))
    )
    await callback.answer()

@router.callback_query(F.data == "analysis_cancel")
async def cancel_analysis(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Анализ отменён.")
    await callback.message.answer("Что дальше?", reply_markup=post_entry_keyboard())
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "analysis_done")
async def finish_analysis(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✅ Анализ завершён. Успехов в управлении финансами!")
    await callback.message.answer("Что дальше?", reply_markup=post_entry_keyboard())
    await state.clear()
    await callback.answer()




@router.message(Command("analysis"))
async def cmd_analysis(message: Message, state: FSMContext, **data):
    await start_analysis_base(
        user_id=message.from_user.id,
        sender=message,
        state=state,
        **data
    )