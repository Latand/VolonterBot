from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

choose_help_type_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Навестить человека"),
            KeyboardButton(text="Еда и вода"),
        ],
        [
            KeyboardButton(text="Лекарства"),
            KeyboardButton(text="Эвакуация"),
        ],
    ]
)