# bot/middlewares/error_handler.py
import logging
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramNetworkError
from typing import Callable, Any, Dict

logger = logging.getLogger(__name__)

class GlobalErrorHandler(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Any],
        event: Any,
        data: Dict[str, Any]
    ) -> Any:
        try:
            return await handler(event, data)

        except TelegramNetworkError as e:
            logger.error("Ошибка сети Telegram: %s", e)
            try:
                if isinstance(event, Message):
                    await event.answer("⚠️ Проблема с соединением. Попробуй позже.")
                elif isinstance(event, CallbackQuery):
                    await event.message.answer("⚠️ Проблема с соединением. Попробуй позже.")
            except Exception as inner_e:
                logger.error("Не удалось отправить сообщение об ошибке: %s", inner_e)

        except Exception as e:
            logger.exception("Необработанная ошибка:")
            try:
                if isinstance(event, Message):
                    await event.answer("🚨 Произошла внутренняя ошибка. Мы уже разбираемся.")
                elif isinstance(event, CallbackQuery):
                    await event.message.answer("🚨 Произошла внутренняя ошибка. Мы уже разбираемся.")
                # 💡 Рекомендация:
                # В будущем — добавить поддержку других типов событий (например, InlineQuery, ChatJoinRequest),
                # если бот будет расширяться, чтобы охватывать всё, что может вызвать ошибку.
            except Exception as inner_e:
                logger.error("Ошибка при отправке сообщения об исключении: %s", inner_e)
