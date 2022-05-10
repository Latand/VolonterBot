from aiogram import Bot
from sqlalchemy.orm import sessionmaker

from tgbot.infrastructure.database.functions.requests import update_request, get_one_request
from tgbot.infrastructure.database.models import Request
from tgbot.keyboards.inline import approve_request_keyboard


async def ask_if_active(bot: Bot, user_id: int, current_request_id: int, session_pool: sessionmaker):
    async with session_pool() as session:
        await update_request(session, Request.id == int(current_request_id), status='to_check')

    await bot.send_message(user_id, f"Ваша заявка {current_request_id} еще актуальная?",
                           reply_markup=approve_request_keyboard(current_request_id))


async def check_if_active(bot: Bot, current_request_id: int, session_pool: sessionmaker):
    async with session_pool() as session:
        request = await get_one_request(session, Request.id == int(current_request_id))
        if not request:
            return
        if request.status in ('new', 'to_check'):
            await bot.send_message(request.channel_id, f'‼️ Заявка №{current_request_id} уже не актуальная',
                                   reply_to_message_id=request.message_id)
            await bot.send_message(request.chat_id, f'Ваша ‼️ Заявка №{current_request_id} уже не актуальная')
            await update_request(session, Request.id == int(current_request_id), status='inactive')
