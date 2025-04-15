from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
import database.requests as rq


router = Router()

class SearchState(StatesGroup):
    page = State()


@router.message(CommandStart())
async def start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Подробную информацию о боте можно посмотреть по команде /info')
    await message.answer('Выберите язык перевода', reply_markup=await kb.inline_languages())


@router.message(Command('help'))
async def help(message: Message):
    await message.answer('По техническим вопросам: @RipeR3d')


@router.message(Command('mode'))
async def help(message: Message):
    await message.answer('Выберите режим перевода', reply_markup=kb.modes)


@router.callback_query(F.data.startswith('mode_'))
async def mode_handler(callback: CallbackQuery):
    mode = callback.data.replace('mode_', '')
    await callback.answer()
    try:
        await rq.set_mode(callback.message.chat.id, mode)
        if mode == "simple":
            await callback.message.edit_text('Вы выбрали простой режим перевода')
        else:
            await callback.message.edit_text('Вы выбрали комплексный режим перевода')
    except:
        await callback.message.edit_text('Что-то пошло не так. /help')


@router.message()
async def message_handler(message: Message, state: FSMContext):
    await state.clear()  # Сбросить старое состояние, если было

    query = message.text.strip()
    entries = await rq.get_entries(query)

    if not entries:
        await message.answer("Ничего не найдено. Попробуйте выбрать комплексный режим перевода: /mode\n"
                             "Если вы знаете перевод, можно добавить его командой /add")
        return

    await state.set_state(SearchState.page)
    await state.update_data(entries=entries, query=query, total=len(entries), page=0)

    await message.answer(
        f"Найдено {len(entries)} совпадений. Вот первая запись:",
    )

    await message.answer(
        entries[0],
        reply_markup=await kb.nav_kb(0, len(entries)),
        parse_mode="HTML"
    )




@router.callback_query(SearchState.page, F.data.in_({"next", "prev"}))
async def pagination_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 0)
    entries = data["entries"]
    total = data["total"]

    if callback.data == "next" and page < total - 1:
        page += 1
    elif callback.data == "prev" and page > 0:
        page -= 1
    else:
        await callback.answer()
        return

    await state.update_data(page=page)
    await callback.message.edit_text(
        entries[page],
        reply_markup=await kb.nav_kb(page, total),
        parse_mode="HTML"
    )
    await callback.answer()