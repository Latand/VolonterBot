from aiogram import Router, F, Bot
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold, hcode

from tgbot.config import Config
from tgbot.misc.functions import google_maps_url
from tgbot.misc.states import GetMedicine
from tgbot.services.json_storage import JSONStorage

medicine_router = Router()


@medicine_router.message(F.text == 'Лекарства')
async def get_medicine(message: Message, state: FSMContext):
    await message.answer('Введите точный адрес человека или пришлите локацию этого человека',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(GetMedicine.EnterAddress)


@medicine_router.message(GetMedicine.EnterAddress)
async def get_medicine_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите названия лекарств, дозировку и количества.')
    await state.set_state(GetMedicine.EnterPrescription)


@medicine_router.message(GetMedicine.EnterAddress, F.location)
async def get_medicine_enter_address_location(message: Message, state: FSMContext):
    maps_url = google_maps_url(message.location.latitude, message.location.longitude)
    await state.update_data(address=maps_url)
    await message.answer('Введите названия лекарств, дозировку и количества.')
    await state.set_state(GetMedicine.EnterPrescription)


@medicine_router.message(GetMedicine.EnterPrescription)
async def get_medicine_enter_prescription(message: Message, state: FSMContext, config: Config, bot: Bot,
                                          json_settings: JSONStorage):
    data = await state.get_data()
    counter = json_settings.get('counter') or 0
    counter += 1
    json_settings.set('counter', counter)

    counter = hcode(f'#{counter}')
    address = data['address']

    prescription = hbold(message.text)

    text_format = '''{counter}
Адрес: {address}

{prescription}
'''.format(address=address, prescription=prescription, counter=counter)
    await bot.send_message(config.channels.medicine_channel_id, text_format)
    await message.answer('Спасибо, ваша заявка была отправлена!')
    await state.clear()
