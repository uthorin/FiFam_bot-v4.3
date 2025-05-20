from aiogram import BaseMiddleware
from typing import Callable, Dict, Any
from aiogram.types import TelegramObject
import asyncpg

class DBMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["db"] = self.pool
        return await handler(event, data)
