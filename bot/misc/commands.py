from aiogram import Bot
from aiogram.types import BotCommand

async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="stats", description="Посмотреть статистику"),
        BotCommand(command="cancel", description="Отменить ввод"),
        BotCommand(command="help", description="Помощь по функциям"),
        BotCommand(command="analysis", description="Анализ расходов"),
        BotCommand(command="export", description="Экспорт в Excel"),
    ])
