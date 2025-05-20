from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import ReceiptStates
from database.receipt import add_receipt, add_receipt_item


router = Router()

@router.message(F.text == "✅ Подтвердить")
async def confirm_receipt(message: Message, state: FSMContext):
    data = await state.get_data()
    items = data.get("receipt_items")
    db = data["db"]

    if not items:
        await message.answer("❌ Не удалось найти данные чека. Попробуй снова.")
        await state.clear()
        return

    user_id = message.from_user.id
    total = sum(item["price"] for item in items)

    receipt_id = await add_receipt(db, user_id=user_id, total=total)

    for item in items:
        await add_receipt_item(
            db,
            receipt_id=receipt_id,
            name=item["name"],
            category=item["category"],
            price=item["price"]
        )

    await message.answer("✅ Чек успешно сохранён!")
    await state.clear()

