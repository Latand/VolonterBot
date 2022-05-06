import logging
from typing import Optional

from aiogram.dispatcher.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


class TypesOfProvisionCD(CallbackData, prefix="type_of_provision"):
    type: Optional[str]
    increase: Optional[bool]
    decrease: Optional[bool]
    finish: Optional[bool]


def get_types_of_provision_keyboard(provision_types: dict):
    builder = InlineKeyboardBuilder()

    for provision_type, quantity in provision_types.items():
        builder.add(
            InlineKeyboardButton(
                text=f'{provision_type} ({quantity})',
                callback_data=TypesOfProvisionCD(type=provision_type).pack(),
            ),
            InlineKeyboardButton(
                text="-",
                callback_data=TypesOfProvisionCD(type=provision_type, decrease=True).pack(),
            ),

            InlineKeyboardButton(
                text="+",
                callback_data=TypesOfProvisionCD(type=provision_type, increase=True).pack(),
            ),
        )

    builder.add(
        InlineKeyboardButton(text='Завершить ✔', callback_data=TypesOfProvisionCD(finish=True).pack()))
    builder.adjust(
        *[3] * len(provision_types),  # [name, +, -]
        1  # [finish]
    )

    return builder.as_markup()
