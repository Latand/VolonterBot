from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import hbold
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import Config
from tgbot.misc.functions import google_maps_url, post_new_request, create_jobs, get_mention_user
from tgbot.misc.states import GetMedicine

medicine_router = Router()


@medicine_router.message(F.text == 'Лекарства')
async def get_medicine(message: Message, state: FSMContext):
    await message.answer('Введите точный адрес человека или пришлите локацию этого человека',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(GetMedicine.EnterAddress)


@medicine_router.message(GetMedicine.EnterAddress, ContentTypesFilter(content_types=ContentType.LOCATION))
async def get_medicine_enter_address_location(message: Message, state: FSMContext):
    maps_url = google_maps_url(message.location.latitude, message.location.longitude)
    await state.update_data(address=maps_url)
    await message.answer('Введите названия лекарств, дозировку и количества.')
    await state.set_state(GetMedicine.EnterFullName)


@medicine_router.message(GetMedicine.EnterAddress, F.text)
async def get_medicine_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите Фамилию, Имя и Отчество человека.')
    await state.set_state(GetMedicine.EnterFullName)


@medicine_router.message(GetMedicine.EnterFullName, F.text)
async def get_medicine_enter_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer('Введите названия лекарств, дозировку и количества.')
    await state.set_state(GetMedicine.EnterPrescription)


@medicine_router.message(GetMedicine.EnterPrescription, F.text)
async def get_medicine_enter_prescription(message: Message, state: FSMContext):
    await state.update_data(prescription=message.text)
    await message.answer('Тут напишите послание. Кто ищет, что передать?')
    await state.set_state(GetMedicine.EnterAdditionalMessage)


@medicine_router.message(GetMedicine.EnterAdditionalMessage, F.text)
async def get_medicine_enter_additional_message(message: Message, state: FSMContext, config: Config, bot: Bot,
                                                scheduler: AsyncIOScheduler, session):
    data = await state.get_data()

    address = data['address']
    prescription = data['prescription']
    sender = get_mention_user(message.from_user)
    additional_message = message.text
    full_name = hbold(data['full_name'])

    text_format = '''
Адрес: {address}
ФИО: {full_name}

{prescription}
Послание: {additional_message}

Отправитель: {sender}
'''.format(address=address, prescription=prescription, full_name=full_name, sender=sender,
           additional_message=additional_message)

    current_request_id = await post_new_request(bot, config.channels.medicine_channel_id, text_format,
                                                session, message.from_user.id)
    create_jobs(scheduler, message.from_user.id, current_request_id)
    await message.answer(f'Ваша заявка №{current_request_id} была принята!' + '\n\n' + text_format)
    await state.clear()
