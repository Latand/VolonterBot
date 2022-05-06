import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

from tgbot.config import load_config
from tgbot.handlers.admin import admin_router
from tgbot.handlers.evacuation import evacuation_router
from tgbot.handlers.get_medicine import medicine_router
from tgbot.handlers.provision import provision_router
from tgbot.handlers.search_people import search_people_router
from tgbot.handlers.user import user_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.services import broadcaster
from tgbot.services.default_commands import set_default_commands
from tgbot.services.json_storage import JSONStorage

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот був запущений")
    await set_default_commands(bot)


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)
    json_settings = JSONStorage("storage.json")  # Insert the path to our JSON storage, created automatically

    dp['config'] = config
    dp['json_settings'] = json_settings

    for router in [
        # admin_router,
        user_router,
        evacuation_router,
        medicine_router,
        provision_router,
        search_people_router,
    ]:
        dp.include_router(router)

    register_global_middlewares(dp, config)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Бот був вимкнений!")
