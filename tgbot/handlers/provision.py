from aiogram import Router, F, Bot
from aiogram.dispatcher.filters import ContentTypesFilter
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, ContentType, CallbackQuery
from aiogram.utils.markdown import hbold

from tgbot.config import Config
from tgbot.keyboards.inline import get_types_of_provision_keyboard, TypesOfProvisionCD
from tgbot.misc.functions import google_maps_url, create_jobs, post_new_request
from tgbot.misc.states import GetProvision

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


@provision_router.message(GetProvision.EnterAddress, F.text)
async def get_provision_enter_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer('Введите ФИО человека')
    await state.set_state(GetProvision.EnterFullName)


@provision_router.message(GetProvision.EnterFullName)
async def get_provision_enter_full_name(message: Message, state: FSMContext):
    full_name = message.text
    await state.update_data(full_name=full_name)

    types_of_provision_allowed = {
        'Взрослый': 0,
        'Детский': 0,
        'Грудничковый': 0
    }

    await state.update_data(types_of_provision=types_of_provision_allowed)
    keyboard = get_types_of_provision_keyboard(types_of_provision_allowed)
    text = 'Выберите тип набора или завершите выбор'

    await message.answer(text, reply_markup=keyboard)

    await state.set_state(GetProvision.ChooseType)



@provision_router.callback_query(GetProvision.ChooseType, TypesOfProvisionCD.filter(F.increase | F.decrease))
async def add_provision_choose_type_callback(callback_query: CallbackQuery, state: FSMContext,
                                             callback_data: TypesOfProvisionCD):
    data = await state.get_data()

    provision_type = callback_data.type
    types_of_provision = data.get('types_of_provision', {})
    if provision_type not in types_of_provision:
        types_of_provision[provision_type] = 0

    else:
        if callback_data.increase:
            types_of_provision[provision_type] += 1
        elif callback_data.decrease:
            if types_of_provision[provision_type] > 0:
                types_of_provision[provision_type] -= 1
            else:
                await callback_query.answer('Нельзя менять количество наборов в отрицательное значение',
                                            show_alert=True)
                return

    await state.update_data(types_of_provision=types_of_provision)
    keyboard = get_types_of_provision_keyboard(types_of_provision)

    await callback_query.message.edit_reply_markup(reply_markup=keyboard)


@provision_router.callback_query(GetProvision.ChooseType, TypesOfProvisionCD.filter(F.finish))
async def add_provision_choose_type_finish(call: CallbackQuery, state: FSMContext, config: Config, bot: Bot, scheduler):
    data = await state.get_data()
    address = data['address']

    full_name = hbold(data.get('full_name'))
    types_of_provision = data.get('types_of_provision', {})
    types_of_provision_str = '\n'.join([f'{type_of_provision}: {num}'
                                        for type_of_provision, num in types_of_provision.items()])

    text_format = '''
Адрес: {address}
Имя: {full_name}

Наборы:
{types_of_provision_str}
'''.format(address=address, full_name=full_name, types_of_provision_str=types_of_provision_str)

    current_request_id = await post_new_request(bot, config.channels.provision_channel_id, text_format,
                                                state.storage, call.from_user.id)
    create_jobs(scheduler, call.from_user.id, current_request_id)

    await call.message.edit_text(f'Спасибо, ваша заявка {current_request_id} была отправлена!')
    await state.clear()
