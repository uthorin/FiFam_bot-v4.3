from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from bot.keyboards.entry import post_entry_keyboard
from utils.export_excel import export_transactions_to_excel



router = Router()

@router.message(Command("export"))
async def export_excel_handler(message: Message, **data):
    db = data.get("db")
    if not db:
        await message.answer("❌ Ошибка подключения к базе данных.")
        return

    file_path = await export_transactions_to_excel(db, message.from_user.id)
    try:
        await message.answer_document(FSInputFile(file_path), caption="📦 Ваши финансы в Excel")
        await message.answer("✅ Экспорт завершён! Проверьте файл.")
        await message.answer("Что дальше?", reply_markup=post_entry_keyboard())
    finally:
        # Удаляем файл после отправки
        import os
        if os.path.exists(file_path):
            os.remove(file_path)

            