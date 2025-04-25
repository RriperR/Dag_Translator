from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import keyboards as kb
import database.requests as rq

router = Router()


@router.message(F.text)
async def message_handler(message: Message, state: FSMContext):
    await state.clear()  # Сбросить старое состояние, если было

    query = message.text.strip()
    entries = await rq.get_entries(query)
    print(f"entries: {entries}")
    try:
        user_entries = await rq.get_users_entries(query)
        print(f"user_entries: {user_entries}")
        entries.extend(user_entries)
        print(f"extended entries: {entries}")
    except Exception as e:
        print(f"Exception: {e}")

    if not entries:
        await message.answer("Ничего не найдено. Попробуйте выбрать комплексный режим перевода: /mode\n"
                             "Если вы знаете перевод, можно добавить его командой /add")
        return

    await state.update_data(entries=entries, query=query, total=len(entries), page=0)

    await message.answer(
        f"Найдено {len(entries)} совпадений. Вот первая запись:",
    )

    await message.answer(
        entries[0],
        reply_markup=await kb.nav_kb(0, len(entries)),
        parse_mode="HTML"
    )


@router.callback_query(F.data.in_({"prev", "next", "prev5", "next5"}))
async def pagination_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    page = data.get("page", 0)
    entries = data["entries"]
    total = data["total"]

    # Вычисляем новую страницу
    if callback.data == "prev" and page > 0:
        page -= 1
    elif callback.data == "next" and page < total - 1:
        page += 1
    elif callback.data == "prev5" and page >= 5:
        page -= 5
    elif callback.data == "next5" and page + 5 < total:
        page += 5
    else:
        await callback.answer()
        return

    # Обновляем страницу
    await state.update_data(page=page)
    await callback.message.edit_text(
        entries[page],
        reply_markup=await kb.nav_kb(page, total),
        parse_mode="HTML"
    )
    await callback.answer()
