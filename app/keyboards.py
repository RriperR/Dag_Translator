from aiogram.filters import callback_data
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Кубачинский')],
    [KeyboardButton(text='Даргинский'), KeyboardButton(text='Лезгинский')]
], resize_keyboard=True, input_field_placeholder='Выберите язык')

modes = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Простой', callback_data='simple')],
    [InlineKeyboardButton(text='Комплексный', callback_data='complex')]
])

languages = ['Кубачинский', 'Даргинский', 'Лезгинский']

async def inline_languages():
    keyboard = ReplyKeyboardBuilder()
    for language in languages:
        keyboard.add(KeyboardButton(text=language))
    return keyboard.adjust(2).as_markup()