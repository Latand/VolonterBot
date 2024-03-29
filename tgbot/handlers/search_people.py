import logging

from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import hcode, hbold

from tgbot.config import Config
from tgbot.misc.functions import google_maps_url, create_jobs, create_new_request, get_mention_user
from tgbot.misc.states import SearchPeople

search_people_router = Router()


@search_people_router.message(F.text == 'Навестить человека')
async def search_people(message: Message, state: FSMContext):
    await message.answer('Введите точный адрес человека или пришлите геолокацию',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(SearchPeople.EnterAddress)


@search_people_router.message(SearchPeople.EnterAddress, ContentTypesFilter(content_types=ContentType.LOCATION))
async def search_people_enter_address_location(message: Message, state: FSMContext):
    maps_url = google_maps_url(message.location.latitude, message.location.longitude)
    logging.info(maps_url)
    await state.update_data(address=maps_url)
    await message.answer('Введите Фамилию, Имя и Отчество человека')
    await state.set_state(SearchPeople.EnterFullName)


@search_people_router.message(SearchPeople.EnterAddress, F.text)
async def search_people_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите Фамилию, Имя и Отчество человека')
    await state.set_state(SearchPeople.EnterFullName)


@search_people_router.message(SearchPeople.EnterFullName, F.text)
async def search_people_enter_full_name(message: Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer('Отправьте фото человека в анфас. В хорошем качестве')
    await state.set_state(SearchPeople.SendPhoto)


@search_people_router.message(SearchPeople.SendPhoto, F.photo[-1].as_("photo"))
async def search_people_send_photo(message: Message, state: FSMContext, photo):
    await state.update_data(photo=photo.file_id)
    await message.answer('Куда сообщить, если найдётся? Введите номер телефона, к которому привязан Телеграм-аккаунт')
    await state.set_state(SearchPeople.EnterFeedbackAddress)


@search_people_router.message(SearchPeople.SendPhoto)
async def search_people_send_photo_failed(message: Message, state: FSMContext):
    await message.answer('Вы не отправили фото. Отправьте фото человека в анфас. В хорошем качестве')


@search_people_router.message(SearchPeople.EnterFeedbackAddress, F.text)
async def search_people_enter_feedback_address(message: Message, state: FSMContext):
    feedback_address = hbold(message.text)
    await state.update_data(feedback_address=feedback_address)
    await message.answer('Тут напишите послание. Кто ищет, что передать?')
    await state.set_state(SearchPeople.EnterAdditionalMessage)


@search_people_router.message(SearchPeople.EnterAdditionalMessage, F.text)
async def search_people_enter_additional_message(message: Message, state: FSMContext, bot: Bot, config: Config,
                                                 scheduler, session):
    data = await state.get_data()

    address = data['address']
    photo = data['photo']
    feedback_address = data['feedback_address']
    full_name = hbold(data['full_name'])
    sender = get_mention_user(message.from_user)

    text_format = '''
Адрес: {address}

Имя: {full_name}
Обратная связь: {feedback_address}

Послание: {additional_message}

Отправитель: {sender}
'''.format(address=address, full_name=full_name, feedback_address=feedback_address, sender=sender,
           additional_message=message.text)

    sent_message = await bot.send_photo(chat_id=config.channels.search_channel_id,
                                        photo=photo,
                                        caption=text_format)

    current_request_id = await create_new_request(session, message.from_user.id,
                                                  config.channels.search_channel_id,
                                                  sent_message.message_id)
    counter = hcode(f'#{current_request_id}')
    text_format_post = f'{counter}\n' + text_format
    await sent_message.edit_caption(text_format_post)

    create_jobs(scheduler, message.from_user.id, current_request_id)
    await message.answer_photo(photo,
                               caption=f'Спасибо, ваша заявка {counter} была отправлена!' + '\n\n' + text_format_post)
    await state.clear()
