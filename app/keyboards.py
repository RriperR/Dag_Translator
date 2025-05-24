from aiogram.filters import callback_data
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


modes = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Простой', callback_data='mode_simple')],
    [InlineKeyboardButton(text='Комплексный', callback_data='mode_complex')]
])

languages = {'Лезгинский':'lezginski',
             'Кубачинский':'kubachinski'}

async def inline_languages(current: str = None) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for language, model in languages.items():
        prefix = "📌" if current == model else ""
        keyboard.add(InlineKeyboardButton(text=f"{prefix} {language}", callback_data=f"lang_{model}"))
    return keyboard.adjust(2).as_markup()


async def nav_kb(current_page: int, total: int) -> InlineKeyboardMarkup:
    buttons = []

    # Назад на 5
    if current_page >= 5:
        buttons.append(InlineKeyboardButton(text="⏪ -5", callback_data="prev5"))

    # Назад на 1
    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data="prev"))

    # Вперёд на 1
    if current_page < total - 1:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data="next"))

    # Вперёд на 5
    if current_page + 5 < total:
        buttons.append(InlineKeyboardButton(text="⏩ +5", callback_data="next5"))

    return InlineKeyboardMarkup(inline_keyboard=[buttons]) if buttons else None
