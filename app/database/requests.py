from sqlalchemy import select, update, or_, func

from database.models import async_session, User, LezginskiEntry, UserEntry


async def set_user(tg_id: int, username: str = '', first_name: str = '', last_name: str = '') -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, username=username,
                             first_name=first_name, last_name=last_name))
            await session.commit()


async def get_user_by_tg_id(tg_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.tg_id == tg_id)
        )
        user = result.scalar_one_or_none()
        return user


async def set_mode(tg_id, mode: str) -> None:
    async with async_session() as session:
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(mode=mode)
        )
        await session.commit()


async def set_language(tg_id, lang: str) -> None:
    async with async_session() as session:
        await session.execute(
            update(User).where(User.tg_id == tg_id).values(language=lang)
        )
        await session.commit()



async def get_entries(search_term: str, model=LezginskiEntry, mode: str = "simple") -> list[str] | None:
    term = search_term.strip().lower().replace('1', '').replace('!', '').replace('l', '').replace('i', '').replace('|', '')
    async with async_session() as session:
        # Сначала точные совпадения
        stmt_exact = select(model).where(
            or_(
                func.lower(term) == func.any_(func.string_to_array(func.lower(model.keywords), '; ')),
                func.lower(term) == func.any_(func.string_to_array(func.lower(model.keytranslations), '; '))
            )
        )

        exact_result = await session.execute(stmt_exact)
        exact_entries = exact_result.scalars().all()

        # Потом нестрогие совпадения в examples (только если complex)
        fuzzy_entries = []
        if mode == "complex":
            stmt_fuzzy = select(model).where(
                func.lower(model.examples).ilike(f"%{term}%")
            )
            fuzzy_result = await session.execute(stmt_fuzzy)
            fuzzy_entries = fuzzy_result.scalars().all()

        # Убираем дубликаты
        all_entries = {entry.id: entry for entry in exact_entries}
        all_entries.update({entry.id: entry for entry in fuzzy_entries})

        # Если слишком много совпадений — возвращаем None
        if len(all_entries) > 100:
            return None

        response = []
        for entry in all_entries.values():
            text = f"<b>{entry.words}</b> - {entry.translations}"
            if entry.notes:
                text += f";  {entry.notes}"
            if entry.examples:
                text += f"\n\n{entry.examples.replace('; ', '\n')}"
            response.append(text)

        return response

async def get_users_entries(search_term: str) -> list[str]:
    term = search_term.strip().lower()

    async with async_session() as session:
        stmt = select(UserEntry).where(
            or_(
                func.lower(term) == func.any_(func.string_to_array(func.lower(UserEntry.words), '; ')),
                func.lower(term) == func.any_(func.string_to_array(func.lower(UserEntry.translations), '; '))
            )
        )

        result = await session.execute(stmt)
        entries = result.scalars().all()

        response = []
        for entry in entries:
            text = f"------- перевод от анонимного пользователя ------- \n\n<b>{entry.words}</b> - {entry.translations}"
            if entry.examples:
                text += f"\n\n{entry.examples}"
            if entry.notes:
                text += f"\n\n{entry.notes}"
            response.append(text)

        return response


async def add_entry(word: str, translation: str, tg_id: int, examples: str = None, notes: str = None) -> None:
    async with async_session() as session:
        # Найти пользователя по tg_id
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )

        if user is None:
            raise ValueError("Пользователь не найден. Пожалуйста, зарегистрируйтесь.")

        entry = UserEntry(
            words=word,
            translations=translation,
            examples=examples,
            notes=notes,
            user_id=user.id
        )

        session.add(entry)
        await session.commit()


async def update_user_info(tg_id: int, username: str | None, first_name: str | None, last_name: str | None) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            updated = False
            if user.username != username:
                user.username = username
                updated = True
            if user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if updated:
                await session.commit()
