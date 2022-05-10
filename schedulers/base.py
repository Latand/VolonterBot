import logging

from aiogram import Bot
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from apscheduler.events import JobExecutionEvent
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.base import BaseScheduler
from apscheduler_di import ContextSchedulerDecorator
from rodi import Container
from sqlalchemy.orm import sessionmaker
from tzlocal import get_localzone

from schedulers.exceptions import DeleteRequest
from tgbot.config import load_config, Config


async def handle_job_error(event: JobExecutionEvent, ctx: Container):
    logging.error(f'{event.exception=}')
    if isinstance(event.exception, DeleteRequest):
        scheduler = ctx.build_provider().get(BaseScheduler)
        scheduler.remove_job(event.job_id)


def setup_scheduler(bot=None, config: Config = None, storage: RedisStorage = None, session_pool=None):
    if not config:
        config = load_config()

    job_stores = {
        "default": RedisJobStore(
            db=2,
            host='redis_cache',
            password=config.redis_config.password,
            port=config.redis_config.port,
            jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running"
        )
    }

    scheduler = ContextSchedulerDecorator(
        AsyncIOScheduler(jobstores=job_stores, timezone=str(get_localzone()))
    )
    if not bot:
        bot = Bot(config.tg_bot.token)
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(scheduler, declared_class=BaseScheduler)
    scheduler.ctx.add_instance(storage, declared_class=RedisStorage)
    scheduler.ctx.add_instance(session_pool, declared_class=sessionmaker)

    scheduler.on_job_error += handle_job_error
    return scheduler
