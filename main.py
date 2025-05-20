import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from sentry_sdk.integrations.logging import LoggingIntegration
import sentry_sdk
import asyncpg

from config import load_config
from bot.misc import commands
from bot.middlewares.error_handler import GlobalErrorHandler
from bot.middlewares.db import DBMiddleware
from bot.handlers import receipt_upload, receipt_trigger, export

print("MAIN FILE:", __file__)

# 🔧 Конфигурация
config = load_config()

bot = Bot(
    token=config.bot_token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML) 
)

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR
)

sentry_sdk.init(
    dsn=config.db_dsn,
    integrations=[sentry_logging],
    traces_sample_rate=0.1,
    send_default_pii=True,
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# 🔁 Точка входа
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запускается...")

    pool = await asyncpg.create_pool(config.database_url)

    dp.message.middleware(DBMiddleware(pool))
    dp.callback_query.middleware(DBMiddleware(pool))

    dp.message.middleware(GlobalErrorHandler())
    dp.callback_query.middleware(GlobalErrorHandler())

    # Импорты хендлеров строго здесь, после middleware
    from bot.handlers import common, statistics, entry_handler, receipt_handler, analysis

    dp.include_router(entry_handler.router)
    dp.include_router(common.router)
    dp.include_router(statistics.router)
    dp.include_router(analysis.router)
    dp.include_router(receipt_handler.router)
    dp.include_router(receipt_upload.router)
    dp.include_router(receipt_trigger.router)
    dp.include_router(export.router)
    await commands.set_default_commands(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())