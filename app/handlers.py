from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

import keyboards as kb
import database.requests as rq


router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Выберите язык перевода', reply_markup=kb.modes)


@router.message(Command('help'))
async def help(message: Message):
    await message.reply('@RipeR3d')


@router.callback_query(F.data == 'simple')
async def simple(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Вы выбрали простой режим перевода')