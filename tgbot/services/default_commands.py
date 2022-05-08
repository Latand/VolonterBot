from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        BotCommand(command='start', description='Начать диалог'),
        BotCommand(command='cancel', description='Отменить создание заявки'),
        BotCommand(command='delete_request', description='Удалить заявку'),
    ])
