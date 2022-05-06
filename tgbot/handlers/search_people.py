import logging

from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import hcode, hbold

from tgbot.config import Config
from tgbot.misc.functions import google_maps_url
from tgbot.misc.states import SearchPeople
from tgbot.services.json_storage import JSONStorage

search_people_router = Router()


@search_people_router.message(F.text == 'Поиск людей')
async def search_people(message: Message, state: FSMContext):
    await message.answer('Введите предполагаемый адрес человека или пришлите локацию этого человека',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(SearchPeople.EnterAddress)


@search_people_router.message(SearchPeople.EnterAddress, ContentTypesFilter(content_types=ContentType.LOCATION))
async def search_people_enter_address_location(message: Message, state: FSMContext):
    maps_url = google_maps_url(message.location.latitude, message.location.longitude)
    logging.info(maps_url)
    await state.update_data(address=maps_url)
    await message.answer('Введите имя человека')
    await state.set_state(SearchPeople.EnterFullName)


@search_people_router.message(SearchPeople.EnterAddress)
async def search_people_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите имя человека')
    await state.set_state(SearchPeople.EnterFullName)


@search_people_router.message(SearchPeople.EnterFullName)
async def search_people_enter_full_name(message: Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer('Отправьте фото человека')
    await state.set_state(SearchPeople.SendPhoto)


@search_people_router.message(SearchPeople.SendPhoto, F.photo)
async def search_people_send_photo(message: Message, state: FSMContext, bot: Bot, config: Config,
                                   json_settings: JSONStorage):
    data = await state.get_data()
    counter = json_settings.get('counter') or 0
    counter += 1
    json_settings.set('counter', counter)
    counter = hcode(f'#{counter}')
    address = data['address']
    full_name = hbold(data['full_name'])
    text_format = '''{counter}
Адрес: {address}

Имя: {full_name}
'''.format(counter=counter, address=address, full_name=full_name)

    await bot.send_photo(chat_id=config.channels.search_channel_id,
                         photo=message.photo[-1].file_id,
                         caption=text_format)

    await message.answer('Спасибо, ваша заявка была отправлена!')
    await state.clear()


@search_people_router.message(SearchPeople.SendPhoto)
async def search_people_send_photo_failed(message: Message, state: FSMContext):
    await message.answer('Вы не отправили фото. Попробуйте еще раз')
