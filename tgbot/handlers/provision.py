from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType
from aiogram.utils.markdown import hbold, hcode

from tgbot.config import Config
from tgbot.keyboards.reply import get_types_of_provision_keyboard
from tgbot.misc.functions import google_maps_url
from tgbot.misc.states import GetProvision
from tgbot.services.json_storage import JSONStorage

provision_router = Router()


@provision_router.message(F.text == 'Еда и вода')
async def get_provision(message: Message, state: FSMContext):
    await message.answer('Введите точный адрес человека или пришлите локацию этого человека',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(GetProvision.EnterAddress)


@provision_router.message(GetProvision.EnterAddress, ContentTypesFilter(content_types=ContentType.LOCATION))
async def get_provision_enter_address_location(message: Message, state: FSMContext):
    maps_url = google_maps_url(message.location.latitude, message.location.longitude)
    await state.update_data(address=maps_url)
    await state.set_state(GetProvision.EnterFullName)


@provision_router.message(GetProvision.EnterAddress)
async def get_provision_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите имя человека')
    await state.set_state(GetProvision.EnterFullName)


@provision_router.message(GetProvision.EnterFullName)
async def get_provision_enter_full_name(message: Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)

    types_of_provision_allowed = [
        'Взрослый',
        "Детский",
        "Грудничковый"
    ]

    keyboard = get_types_of_provision_keyboard(types_of_provision_allowed)

    await message.answer('Выберите тип набора (можете выбрать несколько)',
                         reply_markup=keyboard)
    await state.set_state(GetProvision.ChooseType)


async def finish_choice(bot: Bot, state: FSMContext, config: Config, data: dict,
                        counter):
    address = data['address']

    full_name = hbold(data.get('full_name'))
    types_of_provision = hbold(data.get('types_of_provision', []))
    provision_type = hbold('\n'.join(types_of_provision))
    counter = hcode(f'#{counter}')

    text_format = '''{counter}
Адрес: {address}
Имя: {full_name}

Наборы:
{provision_type}
'''.format(address=address, full_name=full_name, provision_type=provision_type, counter=counter)
    await bot.send_message(config.channels.provision_channel_id, text_format)
    await state.clear()


@provision_router.message(GetProvision.ChooseType)
async def add_provision_choose_type(message: Message, state: FSMContext, config: Config, bot: Bot,
                                    json_settings: JSONStorage):
    type_of_provision = message.text
    data = await state.get_data()

    if type_of_provision == 'Завершить ✔':
        counter = json_settings.get('counter') or 0
        counter += 1
        json_settings.set('counter', counter)

        await finish_choice(bot, state, config, data, counter)
        await message.answer('Спасибо, ваша заявка была отправлена!', reply_markup=ReplyKeyboardRemove())
        return

    types_of_provision_in_data = data.get('types_of_provision', [])
    types_of_provision_in_data.append(type_of_provision)
    await state.update_data(types_of_provision=types_of_provision_in_data)

    types_of_provision_allowed = [
        'Взрослый',
        "Детский",
        "Грудничковый"
    ]

    # Get types of provision not in data:
    types_of_provision_not_in_data = [
        type_of_provision
        for type_of_provision in types_of_provision_allowed
        if type_of_provision not in types_of_provision_in_data
    ]
    keyboard = get_types_of_provision_keyboard(types_of_provision_not_in_data)
    types_of_provision_text = '\n'.join(types_of_provision_in_data)
    text = "Вы выбрали:" \
           "\n" \
           f"<b>{types_of_provision_text}</b>" \
           "\n\n" \
           "Выберите еще один тип набора или завершите выбор"

    await message.answer(text, reply_markup=keyboard)
