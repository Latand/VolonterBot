import json
import logging

from aiogram import Router, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tgbot.config import Config
from tgbot.keyboards.inline import RequestCD
from tgbot.misc.functions import create_jobs, get_mention_user

edit_request_router = Router()


@edit_request_router.callback_query(RequestCD.filter())
async def edit_request_callback(call: CallbackQuery, state: FSMContext, callback_data: RequestCD, bot: Bot,
                                scheduler, config: Config):
    requests = await state.storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    request_id = str(callback_data.request_id)
    request = requests.get(request_id)
    if not request:
        await call.message.edit_text(f'Заявка №{request_id} не найдена')
        return

    if request['status'] == 'inactive':
        await call.message.edit_text(f'Заявка №{request_id} не может быть изменена')
        return
    if request['chat_id'] != call.from_user.id:
        await call.message.edit_text(f'Произошла ошибка... Сообщение отправлено администратору')
        actual_text = 'Актуальная' if callback_data.active else 'Не актуальная'
        await bot.send_message(config.tg_bot.admin_ids[-1],
                               f'‼️ Заявка №{request_id} от {get_mention_user(call.from_user)} {actual_text}')
        return

    if callback_data.active:
        await call.message.edit_text(f'Заявка №{request_id} активна')
        request['status'] = 'active'

        create_jobs(scheduler, call.from_user.id, request_id)
    else:
        await call.message.edit_text(f'Заявка №{request_id} более не активна')
        request['status'] = 'inactive'
        channel_id = request['channel_id']
        message_id = request['message_id']
        request['status'] = 'inactive'

        await bot.send_message(channel_id, f'‼️ Заявка №{request_id} уже не актуальная',
                               reply_to_message_id=message_id)

    requests[request_id] = request
    await state.storage.redis.set('requests', json.dumps(requests))


@edit_request_router.message(commands=['cancel'])
async def cancel_request(message: Message, state: FSMContext):
    await message.answer('Вы отменили создание заявки')
    await state.set_state(None)


@edit_request_router.message(commands=['delete_request'])
async def delete_request(message: Message, state: FSMContext):
    await message.answer('Введите номер заявки для удаления')
    await state.set_state('delete_request')


@edit_request_router.message(state='delete_request')
async def delete_request_handler(message: Message, state: FSMContext, bot: Bot):
    requests = await state.storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    request_id = str(message.text)
    request = requests.get(request_id)
    if not request:
        await message.answer(f'Заявка №{request_id} не найдена')
        return
    elif request['chat_id'] != message.from_user.id:
        await message.answer(f'Заявка №{request_id} не ваша')
    elif request['status'] == 'inactive':
        await message.answer(f'Заявка №{request_id} не активна')
    else:
        await message.answer(f'Заявка №{request_id} удалена')
        requests.pop(request_id)
        await state.storage.redis.set('requests', json.dumps(requests))
        channel_id = request['channel_id']
        message_id = request['message_id']

        await bot.send_message(channel_id, f'‼️ Заявка №{request_id} уже не актуальная',
                               reply_to_message_id=message_id)
    await state.clear()
