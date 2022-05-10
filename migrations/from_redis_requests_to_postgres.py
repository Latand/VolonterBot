# from tgbot.config import load_config
import json
import logging

from tgbot.infrastructure.database.functions.requests import add_request, get_one_request
from tgbot.infrastructure.database.models import Request


async def migrate_requests(session_pool, storage):
    # Load dict from JSON file
    requests = await storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    if not requests:
        return

    async with session_pool() as session:
        requests_keys = list(map(int, requests.keys()))
        max_key = max(requests_keys)
        for i in range(1, max_key + 1):
            request = requests.get(str(i))
            request_db = await get_one_request(session, Request.id == i)
            if request_db:
                if request_db.id == i and request_db.chat_id == request['chat_id']:
                    return
            if not request:
                await add_request(
                    session,
                    0,
                    0,
                    0,
                    'deleted',
                )
                logging.info(f'Added skipped request {i}')
            else:

                request_id = await add_request(session,
                                               chat_id=request['chat_id'],
                                               channel_id=request['channel_id'],
                                               message_id=request['message_id'],
                                               status=request['status']
                                               )
                logging.info(f'Added request {i}, id: {request_id}')
                requests.pop(str(i))
                assert request_id == i
        await storage.redis.set('requests', json.dumps(requests))
