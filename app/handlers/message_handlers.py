from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import keyboards as kb
import database.requests as rq
from database.models import KubachinskiEntry, LezginskiEntry
from models.UserSettings import UserSettingsManager

router = Router()


settings_manager = UserSettingsManager()

LANG_MODEL_MAP = {
    "lezginski": LezginskiEntry,
    "kubachinski": KubachinskiEntry,
}

@router.message(F.text)
async def message_handler(message: Message, state: FSMContext):
    await state.clear()  # Сбросить старое состояние, если было
    try:
        query = message.text.strip()
        settings = await settings_manager.get(message.from_user.id)
        if settings is None:
            await message.answer("Что-то пошло не так. Пожалуйста, используйте /start и попробуйте снова")
            return

        lang = settings["lang"]
        model = LANG_MODEL_MAP[lang]
        mode = settings["mode"]
        entries = await rq.get_entries(query, model, mode)

        if entries is None:
            await message.answer(
                "🔎 Найдено слишком много совпадений.\n\n"
                "Пожалуйста, выберите более точное слово"
                " или попробуйте использовать простой режим /mode для более точного поиска."
            )
            return

        user_entries = await rq.get_users_entries(query)
        entries.extend(user_entries)
    except Exception as e:
        print(f"Exception: {e}")

    if not entries:
        await message.answer("К сожалению ничего не нашлось. Попробуйте:\n"
                             "1) поменять режим перевода - /mode\n"
                             "2) поменять язык перевода - /lang\n\n"
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
