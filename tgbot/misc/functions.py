import datetime
import json

from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.utils.markdown import hcode
from apscheduler.triggers.date import DateTrigger

from schedulers.jobs import ask_if_active, check_if_active


def google_maps_url(lat, lon):
    url = "https://maps.google.com/maps?q={lat},{lon}"
    return url.format(lat=lat, lon=lon)


async def create_new_request(storage: RedisStorage, user_id: int, channel_id: int, message_id: int):
    requests = await storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    current_request_id = len(requests) + 1
    requests[current_request_id] = {
        'chat_id': user_id,
        'channel_id': channel_id,
        'message_id': message_id,
        'status': 'new',
    }
    await storage.redis.set('requests', json.dumps(requests))
    return current_request_id


def create_jobs(scheduler, user_id, current_request_id):
    time_to_ask = datetime.datetime.now() + datetime.timedelta(minutes=1)
    # time_to_ask = datetime.datetime.now() + datetime.timedelta(hours=24)
    time_to_check = datetime.datetime.now() + datetime.timedelta(minutes=2)
    # time_to_check = datetime.datetime.now() + datetime.timedelta(hours=36)

    scheduler.add_job(
        ask_if_active,
        trigger=DateTrigger(time_to_ask),
        kwargs=dict(user_id=user_id, current_request_id=current_request_id)
    )
    scheduler.add_job(
        check_if_active,
        trigger=DateTrigger(time_to_check),
        kwargs=dict(current_request_id=current_request_id)
    )


async def post_new_request(bot, channel_id, text, storage, user_id):
    sent_message = await bot.send_message(channel_id, text)

    current_request_id = await create_new_request(storage, user_id,
                                                  channel_id,
                                                  sent_message.message_id)
    counter = hcode(f'#{current_request_id}')
    text_format_post = f'{counter}\n' + text
    await sent_message.edit_text(text_format_post)
    return current_request_id
