from aiogram import Router
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(commands=["admin"])
async def admin_start(message: Message):
    await message.reply("Вітаю, адміне!")
