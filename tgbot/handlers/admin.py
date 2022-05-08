import json

from aiogram import Router
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile

from tgbot.filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(commands=["admin"])
async def admin_start(message: Message):
    await message.reply("Вітаю, адміне!")


@admin_router.message(commands=["show_requests"])
async def admin_show_requests(message: Message, state: FSMContext):
    requests = await state.storage.redis.get('requests') or '{}'
    requests = json.loads(requests)
    with open('requests_dump.json', 'w') as f:
        json.dump(requests, f)
    document = FSInputFile('requests_dump.json')
    await message.reply_document(document=document, caption="Заявки")
