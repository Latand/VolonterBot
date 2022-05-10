import datetime

from aiogram.types import User
from aiogram.utils.markdown import hcode
from apscheduler.triggers.date import DateTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from schedulers.jobs import ask_if_active, check_if_active
from tgbot.infrastructure.database.functions.requests import add_request


def google_maps_url(lat, lon):
    url = "https://maps.google.com/maps?q={lat},{lon}"
    return url.format(lat=lat, lon=lon)


async def create_new_request(session: AsyncSession, user_id: int, channel_id: int, message_id: int):
    request_id = await add_request(session, user_id, channel_id, message_id)

    return request_id


def create_jobs(scheduler, user_id, current_request_id):
    # time_to_ask = datetime.datetime.now() + datetime.timedelta(minutes=1)
    time_to_ask = datetime.datetime.now() + datetime.timedelta(hours=24)
    # time_to_check = datetime.datetime.now() + datetime.timedelta(minutes=2)
    time_to_check = datetime.datetime.now() + datetime.timedelta(hours=36)
    #
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


async def post_new_request(bot, channel_id, text, session, user_id):
    sent_message = await bot.send_message(channel_id, text)

    current_request_id = await create_new_request(session, user_id,
                                                  channel_id,
                                                  sent_message.message_id)
    counter = hcode(f'#{current_request_id}')
    text_format_post = f'{counter}\n' + text
    await sent_message.edit_text(text_format_post)
    return current_request_id


def get_mention_user(user: User):
    username = f"@{user.username}" if user.username else ''
    return f"<a href='tg://user?id={user.id}'>{user.full_name}</a> {username}"
