import json

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.redis import RedisStorage

from tgbot.keyboards.inline import approve_request_keyboard


async def ask_if_active(bot: Bot, user_id: int, current_request_id: int, storage: RedisStorage):
    requests = await storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    current_request_id = str(current_request_id)
    request = requests.get(current_request_id)
    if not request:
        return
    request['status'] = 'to_check'
    requests[current_request_id] = request
    await storage.redis.set('requests', json.dumps(requests))

    await bot.send_message(user_id, f"Ваша заявка {current_request_id} еще актуальная?",
                           reply_markup=approve_request_keyboard(current_request_id))


async def check_if_active(bot: Bot, current_request_id: int, storage: RedisStorage):
    requests = await storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    current_request_id = str(current_request_id)
    request = requests.get(current_request_id)
    if not request:
        return
    if request['status'] in ('new', 'to_check'):
        chat_id = request['chat_id']
        channel_id = request['channel_id']
        message_id = request['message_id']

        await bot.send_message(channel_id, f'Заявка #{current_request_id} уже не актуальная',
                               reply_to_message_id=message_id)
        await bot.send_message(chat_id, f'Ваша заявка #{current_request_id} уже не актуальная')

        request['status'] = 'inactive'
        requests[current_request_id] = request
        await storage.redis.set('requests', json.dumps(requests))
