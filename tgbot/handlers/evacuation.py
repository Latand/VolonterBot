from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import hbold
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.misc.functions import google_maps_url, create_jobs, post_new_request, get_mention_user
from tgbot.misc.states import Evacuate

evacuation_router = Router()


@evacuation_router.message(F.text == 'Эвакуация')
async def evacuate_people(message: Message, state: FSMContext):
    await message.answer('Введите точный адрес человека или пришлите его геолокацию',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(Evacuate.EnterAddress)


@evacuation_router.message(Evacuate.EnterAddress, ContentTypesFilter(content_types=ContentType.LOCATION))
async def evacuate_people_enter_address_location(message: Message, state: FSMContext):
    maps_url = google_maps_url(message.location.latitude, message.location.longitude)
    await state.update_data(address=maps_url)
    await message.answer('Введите Фамилию, Имя и Отчество человека')
    await state.set_state(Evacuate.EnterFullName)


@evacuation_router.message(Evacuate.EnterAddress)
async def evacuate_people_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите Фамилию, Имя и Отчество человека')
    await state.set_state(Evacuate.EnterFullName)


@evacuation_router.message(Evacuate.EnterFullName)
async def evacuate_people_enter_full_name(message: Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer('Введите описание проблем (инвалидность, раненный, лежачий, пожилой и тд)')
    await state.set_state(Evacuate.EnterSpecialConditions)


@evacuation_router.message(Evacuate.EnterSpecialConditions)
async def evacuate_people_enter_conditions(message: Message, state: FSMContext):
    special_conditions = hbold(message.text)
    await state.update_data(special_conditions=special_conditions)
    await message.answer('Тут напишите послание. Кто ищет, что передать?')
    await state.set_state(Evacuate.EnterAdditionalMessage)


@evacuation_router.message(Evacuate.EnterAdditionalMessage, F.text)
async def evacuate_people_enter_additional_message(message: Message, state: FSMContext, bot: Bot, config: Config,
                                                   scheduler: AsyncIOScheduler):
    additional_message = message.text

    data = await state.get_data()
    special_conditions = data['special_conditions']
    address = data['address']
    full_name = hbold(data['full_name'])
    sender = get_mention_user(message.from_user)
    text_format = '''
Адрес: {address}

Имя: {full_name}
Специальные условия: {special_conditions}
Послание: {additional_message}

Отправитель: {sender}
'''.format(special_conditions=special_conditions, address=address, full_name=full_name, sender=sender,
           additional_message=additional_message)

    current_request_id = await post_new_request(bot, config.channels.evacuation_channel_id, text_format,
                                                state.storage, message.from_user.id)
    create_jobs(scheduler, message.from_user.id, current_request_id)
    await message.answer(f'Ваша заявка №{current_request_id} была принята!' + '\n\n' + text_format)

    await state.clear()
