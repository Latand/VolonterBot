from aiogram import Router
from aiogram.types import Message

from tgbot.keyboards.reply import choose_help_type_keyboard

user_router = Router()


@user_router.message(commands=["start"])
async def user_start(message: Message):
    await message.reply("Волонтёрский бот приветствует Вас! \n"
                        "Выберите один из вариантов помощи:", reply_markup=choose_help_type_keyboard)
