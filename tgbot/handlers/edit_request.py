import json
import logging

from aiogram import Router, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.config import Config
from tgbot.infrastructure.database.functions.requests import get_one_request, update_request, delete_request_by_id
from tgbot.infrastructure.database.models import Request
from tgbot.keyboards.inline import RequestCD
from tgbot.misc.functions import create_jobs, get_mention_user

edit_request_router = Router()


@edit_request_router.callback_query(RequestCD.filter())
async def edit_request_callback(call: CallbackQuery, state: FSMContext, callback_data: RequestCD, bot: Bot,
                                scheduler, config: Config, session):
    request = await get_one_request(session, Request.id == callback_data.request_id)
    if not request:
        await call.message.edit_text(f'Заявка №{request.id} не найдена')
        return

    if request.status == 'inactive':
        await call.message.edit_text(f'Заявка №{request.id} не может быть изменена')
        return
    if request.chat_id != call.from_user.id:
        await call.message.edit_text(f'Произошла ошибка... Сообщение отправлено администратору')
        if not callback_data.active:
            await bot.send_message(config.tg_bot.admin_ids[-1],
                                   f'‼️ Заявка №{request.id} от {get_mention_user(call.from_user)} не актуальная')
        return

    if callback_data.active:
        await call.message.edit_text(f'Заявка №{request.id} активна')
        await update_request(session, Request.id == request.id, status='active')

        create_jobs(scheduler, call.from_user.id, request.id)
    else:
        await call.message.edit_text(f'Заявка №{request.id} более не активна')
        await update_request(session, Request.id == request.id, status='inactive')

        await bot.send_message(request.channel_id,
                               f'‼️ Пользователь: {get_mention_user(call.from_user)} отменил заявку №{request.id}',
                               reply_to_message_id=request.message_id)


@edit_request_router.message(commands=['cancel'])
async def cancel_request(message: Message, state: FSMContext):
    await message.answer('Вы отменили создание заявки')
    await state.set_state(None)


@edit_request_router.message(commands=['delete_request'])
async def delete_request(message: Message, state: FSMContext):
    await message.answer('Введите номер заявки для удаления')
    await state.set_state('delete_request')


@edit_request_router.message(state='delete_request')
async def delete_request_handler(message: Message, state: FSMContext, bot: Bot, session):
    try:
        request_id = int(message.text)
    except ValueError:
        await message.answer('Неверный формат номера заявки. Введите снова или нажмите /cancel')
        return
    request = await get_one_request(session, Request.id == request_id)
    if not request:
        await message.answer(f'Заявка №{request_id} не найдена')
        return
    elif request.chat_id != message.from_user.id:
        await message.answer(f'Заявка №{request_id} не ваша')
    elif request.status == 'inactive':
        await message.answer(f'Заявка №{request_id} не активна')
    else:
        await message.answer(f'Заявка №{request_id} удалена')
        await delete_request_by_id(session, request_id)

        await bot.send_message(request.channel_id,
                               f'‼️ Заявку №{request_id} удалил пользователь {get_mention_user(message.from_user)}',
                               reply_to_message_id=request.message_id)
    await state.clear()
