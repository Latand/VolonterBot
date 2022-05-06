from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

choose_help_type_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Поиск людей"),
            KeyboardButton(text="Еда и вода"),
        ],
        [
            KeyboardButton(text="Лекарства"),
            KeyboardButton(text="Эвакуация"),
        ],
    ]
)


def get_types_of_provision_keyboard(provision_types: list):
    builder = ReplyKeyboardBuilder()

    for provision_type in provision_types:
        builder.add(KeyboardButton(text=provision_type))

    builder.add(KeyboardButton(text='Завершить ✔'))
    builder.adjust(1)

    return builder.as_markup(resize_keyboard=True)
