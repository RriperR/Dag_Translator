from aiogram.filters import callback_data
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


modes = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Простой', callback_data='mode_simple')],
    [InlineKeyboardButton(text='Комплексный', callback_data='mode_complex')]
])

languages = ['Кубачинский', 'Даргинский', 'Лезгинский']

show_more = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="more:yes"),
         InlineKeyboardButton(text="Нет", callback_data="more:no")]
    ])

async def inline_languages():
    keyboard = InlineKeyboardBuilder()
    for language in languages:
        keyboard.add(InlineKeyboardButton(text=language, callback_data=language))
    return keyboard.adjust(2).as_markup()


async def nav_kb(current_page: int, total: int) -> InlineKeyboardMarkup:
    buttons = []
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev"))
    if current_page < total - 1:
        buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data="next"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None
