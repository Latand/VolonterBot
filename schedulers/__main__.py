import asyncio
import logging

from .base import setup_scheduler


async def main():
    logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )

    scheduler = setup_scheduler()
    logging.info('Starting')

    scheduler.start()
    while True:
        await asyncio.sleep(1000)


if __name__ == '__main__':
    asyncio.run(main())
    logging.info('Exited ')
