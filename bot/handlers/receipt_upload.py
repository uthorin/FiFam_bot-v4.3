from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from bot.keyboards.entry import post_entry_keyboard
from bot.states import ReceiptStates
from config import load_config
config = load_config()
from database.receipt import add_receipt, add_receipt_item
from uuid import uuid4
import os

from bot.utils.ocr.google_ocr import run_ocr_google
from bot.utils.extractors.gpt import ReceiptItemExtractorGPT
from bot.utils.parsers.regex_parser import extract_items_multiline

router = Router()

# Клавиатура подтверждения
def confirmation_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_receipt")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_receipt")]
    ])

# Загрузка фото или PDF
@router.message(ReceiptStates.waiting_for_photo_or_document, F.photo | F.document)
async def handle_receipt_upload(message: Message, state: FSMContext):
    file = message.photo[-1] if message.photo else message.document
    ext = ".jpg" if message.photo else ".pdf"

    # 🔐 Проверка размера файла (макс. 5 МБ)
    if file.file_size > 5 * 1024 * 1024:
        await message.answer("❌ Файл слишком большой. Максимальный размер — 5 МБ.")
        return

    # 🔐 Проверка MIME-типа (для документов)
    if message.document:
        allowed_mime = ["application/pdf"]
        if file.mime_type not in allowed_mime:
            await message.answer("❌ Неверный формат файла. Отправь PDF или фото чека.")
            return

    file_name = f"receipt_{uuid4()}{ext}"
    temp_path = f"./tmp/{file_name}"
    os.makedirs("./tmp", exist_ok=True)

    await message.bot.download(file, destination=temp_path)

    try:
        ocr_text = run_ocr_google(temp_path)

        gpt = ReceiptItemExtractorGPT(api_key=config.openai_api_key)
        items = gpt.extract_items(ocr_text)

        # Если GPT не справился — fallback на regex
        if not items:
            items = extract_items_multiline(ocr_text)

    except Exception as e:
        await message.answer("❌ Ошибка при обработке чека. Попробуй позже.")
        print(f"[ERROR] Receipt OCR/Parsing failed: {e}")
        items = []

    finally:
        # 🔐 Обязательная очистка файла
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"[WARNING] Не удалось удалить временный файл: {e}")

    if not items:
        await message.answer("❌ Не удалось распознать покупки. Попробуй снова.")
        return

    await state.update_data(receipt_items=items)
    await state.set_state(ReceiptStates.waiting_for_user_confirm)

    preview = "\n".join([
        f"- {item['name']} — {item['price']} ({item.get('category', '❔')})"
        for item in items
    ])

    await message.answer(
        f"🧾 Найденные покупки:\n\n{preview}\n\nПодтвердить сохранение?",
        reply_markup=confirmation_keyboard()
    )

    

# Подтверждение пользователем
@router.callback_query(F.data == "confirm_receipt")
async def confirm_receipt(callback: CallbackQuery, state: FSMContext, **data):
    fsm_data = await state.get_data()
    items = fsm_data.get("receipt_items")
    db = data.get("db")
    if not db:
        await callback.message.edit_text("❌ Ошибка базы данных.")
        await state.clear()
        return
    user_id = callback.from_user.id

    if not items:
        await callback.message.edit_text("❌ Данные чека не найдены.")
        await state.clear()
        return

    total = sum(item["price"] for item in items)
    receipt_id = await add_receipt(db, user_id=user_id, total=total)

    for item in items:
        await add_receipt_item(db, receipt_id, item["name"], item["category"], item["price"])

    await callback.message.edit_text("✅ Чек успешно сохранён!")
    await state.clear()
    await callback.message.answer("Что дальше?", reply_markup=post_entry_keyboard())

# Отмена
@router.callback_query(F.data == "cancel_receipt")
async def cancel_receipt(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("🚫 Добавление чека отменено.")

@router.message(F.photo | F.document)
async def process_uploaded_file(message: Message, state: FSMContext):
    current_state = await state.get_state()

    # Если FSM уже в состоянии — пусть сработает целевой хендлер
    if current_state == ReceiptStates.waiting_for_photo_or_document.state:
        return  # Не мешаем FSM-хендлеру

    # Иначе — запускаем процесс как будто пользователь начал "вне команды"
    await state.set_state(ReceiptStates.waiting_for_photo_or_document)
    await message.answer("📥 Чек принят! Распознаю данные...")

    # Прокинь в FSM данные, если нужно (например, метку или время)
    # await state.update_data(source="auto")

    # Импортируй и вызови вручную твой основной обработчик
    from .receipt_upload import handle_receipt_upload
    await handle_receipt_upload(message, state)

