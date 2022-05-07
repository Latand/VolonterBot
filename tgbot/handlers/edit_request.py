import json
import logging

from aiogram import Router, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from tgbot.keyboards.inline import RequestCD

edit_request_router = Router()


@edit_request_router.callback_query(RequestCD.filter())
async def edit_request_callback(call: CallbackQuery, state: FSMContext, callback_data: RequestCD, bot: Bot):
    requests = await state.storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    request_id = str(callback_data.request_id)
    request = requests.get(request_id)
    if not request:
        await call.message.edit_text(f'Заявка №{request_id} не найдена')
        return

    if request['status'] != 'new':
        await call.message.edit_text(f'Заявка №{request_id} не может быть изменена')
        return

    if callback_data.active:
        await call.message.edit_text(f'Заявка №{request_id} активна')
        request['status'] = 'active'
    else:
        await call.message.edit_text(f'Заявка №{request_id} более не активна')
        request['status'] = 'inactive'
        channel_id = request['channel_id']
        message_id = request['message_id']

        await bot.send_message(channel_id, f'Заявка #{request_id} уже не актуальная',
                               reply_to_message_id=message_id)

        request['status'] = 'inactive'
    requests[request_id] = request
    await state.storage.redis.set('requests', json.dumps(requests))
