import logging
from typing import Optional

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TypesOfProvisionCD(CallbackData, prefix="type_of_provision"):
    type: Optional[str]
    increase: Optional[bool]
    finish: Optional[bool]
    reset: Optional[bool]


class RequestCD(CallbackData, prefix="request"):
    active: bool
    request_id: int


def get_types_of_provision_keyboard(provision_types: dict):
    builder = InlineKeyboardBuilder()

    for provision_type, quantity in provision_types.items():
        builder.add(
            InlineKeyboardButton(
                text=f'{provision_type} ({quantity})',
                callback_data=TypesOfProvisionCD(type=provision_type).pack(),
            ),

            InlineKeyboardButton(
                text="+",
                callback_data=TypesOfProvisionCD(type=provision_type, increase=True).pack(),
            ),
        )

    builder.add(
        InlineKeyboardButton(text='Отправить ✔', callback_data=TypesOfProvisionCD(finish=True).pack())
    )
    builder.add(
        InlineKeyboardButton(text='Сброс ❌', callback_data=TypesOfProvisionCD(reset=True).pack())
    )
    builder.adjust(
        *[2] * len(provision_types),  # [name, +]
        1, 2  # [finish]
    )

    return builder.as_markup()


def approve_request_keyboard(current_request_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data=RequestCD(active=True, request_id=current_request_id).pack()),
            InlineKeyboardButton(text="Нет",
                                 callback_data=RequestCD(active=False, request_id=current_request_id).pack()),
        ]
    ])
    return keyboard
