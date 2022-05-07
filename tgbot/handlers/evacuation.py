from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import hbold, hcode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.misc.functions import google_maps_url, create_new_request, create_jobs, post_new_request
from tgbot.misc.states import Evacuate

evacuation_router = Router()


@evacuation_router.message(F.text == 'Эвакуация')
async def evacuate_people(message: Message, state: FSMContext):
    await message.answer('Введите предполагаемый адрес человека или пришлите локацию этого человека',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(Evacuate.EnterAddress)


@evacuation_router.message(Evacuate.EnterAddress, ContentTypesFilter(content_types=ContentType.LOCATION))
async def evacuate_people_enter_address_location(message: Message, state: FSMContext):
    maps_url = google_maps_url(message.location.latitude, message.location.longitude)
    await state.update_data(address=maps_url)
    await message.answer('Введите имя человека')
    await state.set_state(Evacuate.EnterFullName)


@evacuation_router.message(Evacuate.EnterAddress)
async def evacuate_people_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите имя человека')
    await state.set_state(Evacuate.EnterFullName)


@evacuation_router.message(Evacuate.EnterFullName)
async def evacuate_people_enter_full_name(message: Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer('Введите описание проблем (инвалидность, раненный, лежачий, пожилой и тд)')
    await state.set_state(Evacuate.EnterSpecialConditions)


@evacuation_router.message(Evacuate.EnterSpecialConditions)
async def evacuate_people_enter_conditions(message: Message, state: FSMContext, bot: Bot, config: Config,
                                           scheduler: AsyncIOScheduler):
    data = await state.get_data()
    special_conditions = hbold(message.text)
    address = data['address']
    full_name = hbold(data['full_name'])
    text_format = '''
Адрес: {address}

Имя: {full_name}
Специальные условия: {special_conditions}
'''.format(special_conditions=special_conditions, address=address, full_name=full_name)

    current_request_id = await post_new_request(bot, text_format, config.channels.evacuation_channel_id,
                                                state.storage, message.from_user.id)
    create_jobs(scheduler, message.from_user.id, current_request_id)

    await message.answer(f'Спасибо, ваша заявка {current_request_id} была отправлена!')

    await state.clear()

