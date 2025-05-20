from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import ReceiptStates

router = Router()

@router.message(F.text.lower() == "🧾 загрузить чек")
async def trigger_receipt_upload(message: Message, state: FSMContext):
    await state.set_state(ReceiptStates.waiting_for_photo_or_document)
    await message.answer("📸 Отправь фото или PDF файла чека для распознавания.")
